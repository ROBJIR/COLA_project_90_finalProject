from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from django.contrib.auth.models import Permission, User
from django.core.management.base import CommandError
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from whohas.models import Events, ItemCategories, Items, ItemTypes, Loans, LoanStatuses, WhohasHomePage
from whohas.views.whohas import WhohasView


class WhohasAvailabilityTests(TestCase):
    def test_home_lists_items_without_an_unreturned_loan(self):
        reader = User.objects.create_user('availability-reader')
        reader.user_permissions.add(Permission.objects.get(
            content_type__app_label='whohas', codename='view_whohashomepage',
        ))
        item_type = ItemTypes.objects.create(name='Test item type')
        never_loaned = Items.objects.create(name='Never loaned', item_type=item_type)
        returned = Items.objects.create(name='Returned item')
        loaned = Items.objects.create(name='Currently loaned')
        for item in (returned, loaned):
            Loans.objects.create(item=item, borrower=reader, tstamp_real_end=timezone.now())
        Loans.objects.create(item=loaned, borrower=reader, tstamp_real_start=timezone.now())

        self.assertQuerySetEqual(WhohasView.itemfree(), [never_loaned, returned])
        self.client.force_login(reader)
        response = self.client.get(reverse('whohas'))
        self.assertContains(response, never_loaned.name)
        self.assertContains(response, item_type.name)
        self.assertContains(response, returned.name)
        self.assertNotContains(response, loaned.name)


# Tests replacement of Whohas records by the sample library command.
# Testuje nahrazení záznamů Whohas příkazem pro ukázkovou knihovnu.
class ImportWhohasBooksTests(TestCase):
    # Verifies explicit replacement, stable record counts, and sample relationships.
    # Ověřuje výslovné nahrazení, stejné počty záznamů a ukázkové vazby.
    def test_import_replaces_data_and_can_be_repeated(self):
        existing_book = Items.objects.create(name='Original record')
        with self.assertRaises(CommandError):
            call_command('import_whohas_books', stdout=StringIO())
        self.assertTrue(Items.objects.filter(pk=existing_book.pk).exists())

        for _ in range(2):
            call_command('import_whohas_books', replace=True, stdout=StringIO())
            models = (WhohasHomePage, ItemTypes, ItemCategories, Items, LoanStatuses, Loans, Events)
            self.assertEqual(tuple(model.objects.count() for model in models), (2, 3, 5, 4, 4, 4, 7))
            self.assertFalse(Items.objects.filter(name='Original record').exists())
            loan = Loans.objects.get(item__name='Pavel Tomeš, Až na ten konec dobrý')
            self.assertEqual(loan.item.item_categories.count(), 2)
            self.assertEqual(loan.status.name, 'returned')
            self.assertEqual(loan.loan.count(), 2)
            self.assertFalse(loan.borrower.is_active)

    # Restores the original data if an error interrupts the import.
    # Obnoví původní data, pokud import přeruší chyba.
    def test_import_rolls_back_on_error(self):
        book = Items.objects.create(name='Original record')
        with patch.object(Events.objects, 'bulk_create', side_effect=RuntimeError('Test import failure')):
            with self.assertRaisesMessage(RuntimeError, 'Test import failure'):
                call_command('import_whohas_books', replace=True, stdout=StringIO())
        self.assertEqual(list(Items.objects.values_list('pk', flat=True)), [book.pk])
        self.assertFalse(User.objects.filter(username__startswith='whohas-demo-').exists())

class LoanDetailTests(TestCase):
    # Checks that the list and detail show sample loan information.
    # Ověřuje zobrazení údajů o ukázkové výpůjčce v seznamu i detailu.
    def test_loan_list_and_detail(self):
        reader = User.objects.create_user('loan-reader')
        reader.user_permissions.add(Permission.objects.get(
            content_type__app_label='whohas', codename='view_loans',
        ))
        self.client.force_login(reader)
        loan = Loans.objects.create(borrower=reader, description='Sample loan')
        Events.objects.create(loan=loan, author=reader, description='Sample event')
        self.assertContains(self.client.get(reverse('loans')), loan.description)
        detail = self.client.get(reverse('loandetail', args=[loan.pk]))
        self.assertContains(detail, f"Loan #{loan.pk}")
        self.assertContains(detail, loan.loan.first().description)
        self.assertEqual(self.client.get(reverse('loandetail', args=[999999])).status_code, 404)
        url = reverse('loandetail', args=[loan.pk])
        self.assertEqual(self.client.get(url, {'edit': '1'}).status_code, 403)
        self.assertEqual(self.client.post(url).status_code, 403)

    def test_loan_edit_validates_and_saves_fields_and_relationships(self):
        editor = User.objects.create_user('loan-editor')
        editor.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='whohas', codename__in=['view_loans', 'change_loans'],
        ))
        borrower = User.objects.create_user('new-borrower')
        item = Items.objects.create(name='New item')
        status = LoanStatuses.objects.create(name='active')
        loan = Loans.objects.create(borrower=editor, description='Original')
        url = reverse('loandetail', args=[loan.pk])
        self.client.force_login(editor)
        self.assertContains(self.client.get(url, {'edit': '1'}), 'type="datetime-local"')

        data = {
            'item': item.pk, 'status': status.pk, 'borrower': borrower.pk,
            'tstamp_planned_start': '2026-11-21T09:00',
            'tstamp_planned_end': '2026-11-22T09:00',
            'tstamp_real_start': '2026-11-21T09:05:30',
            'tstamp_real_end': '',
            'description': 'Updated',
        }
        self.assertEqual(self.client.post(url, {**data, 'borrower': ''}).status_code, 400)
        loan.refresh_from_db()
        self.assertEqual(loan.description, 'Original')
        self.assertRedirects(self.client.post(url, data), url)
        loan.refresh_from_db()
        self.assertEqual((loan.item_id, loan.status_id, loan.borrower_id), (item.pk, status.pk, borrower.pk))
        self.assertEqual(loan.description, 'Updated')
        self.assertEqual(loan.tstamp_planned_start.hour, 9)
        self.assertEqual(loan.tstamp_planned_end.day, 22)
        self.assertEqual(loan.tstamp_real_start.second, 30)
        self.assertIsNone(loan.tstamp_real_end)

    def test_overdue_list_shows_only_loans_with_success_status(self):
        reader = User.objects.create_user('overdue-reader')
        reader.user_permissions.add(Permission.objects.get(
            content_type__app_label='whohas', codename='view_loans',
        ))
        success = LoanStatuses.objects.create(name='success')
        borrowed = LoanStatuses.objects.create(name='borrowed')
        matching = Loans.objects.create(
            borrower=reader, status=success, description='Success example',
        )
        for status in (borrowed, None):
            Loans.objects.create(borrower=reader, status=status, description='Excluded example')
        self.assertQuerySetEqual(WhohasView.overdue_loans(), [matching])
        self.client.force_login(reader)
        response = self.client.get(reverse('overdue_loans'))
        self.assertContains(response, matching.description)
        self.assertNotContains(response, 'Excluded example')


# Tests item forms, persistence, and access control.
# Testuje formuláře předmětů, ukládání a řízení přístupu.
class ItemCrudTests(TestCase):
    # Creates shared users and catalogue records.
    # Vytváří sdílené uživatele a záznamy číselníků.
    @classmethod
    def setUpTestData(cls):
        cls.kind = ItemTypes.objects.create(name='Kniha')
        cls.category = ItemCategories.objects.create(item_category_name='Beletrie')
        cls.item = Items.objects.create(name='Hobit', item_type=cls.kind)
        cls.item.item_categories.add(cls.category)
        cls.admin = User.objects.create_superuser('crud_admin', '', 'test-password')
        cls.reader = User.objects.create_user('crud_reader')
        cls.reader.user_permissions.add(Permission.objects.get(codename='view_items', content_type__app_label='whohas'))

    # Builds valid item form data with optional overrides.
    # Sestavuje platná data formuláře s volitelnými změnami.
    def data(self, **overrides):
        data = {'name': 'New book', 'description': 'Description', 'item_type': self.kind.pk,
                'item_categories': [self.category.pk]}
        data.update(overrides)
        return data

    # Checks the item view modes and links in the list.
    # Kontroluje režimy zobrazení předmětu a odkazy v seznamu.
    def test_render_all_modes_and_list_links(self):
        self.client.force_login(self.admin)
        detail = reverse('itemdetail', args=[self.item.pk])
        response = self.client.get(reverse('items'))
        self.assertContains(response, f'href="{detail}"')
        self.assertContains(response, f'href="{reverse("itemcreate")}"')
        for url in [detail, detail+'?edit=1', reverse('itemcreate'), reverse('itemdelete', args=[self.item.pk])]:
            self.assertEqual(self.client.get(url).status_code, 200)

    # Checks item creation, updates, and clearing optional relations.
    # Kontroluje vytvoření, úpravy a odebrání nepovinných vazeb předmětu.
    def test_create_update_and_clear_relations(self):
        self.client.force_login(self.admin)
        create_url = reverse('itemcreate')
        form = self.client.get(create_url).context['web_data']['form']
        self.assertEqual(form['owner'].value(), self.admin.pk)
        response = self.client.post(create_url, self.data())
        created = Items.objects.get(name='New book')
        self.assertEqual(created.owner, self.admin)
        self.assertRedirects(response, reverse('itemdetail', args=[created.pk])+'?saved=1')
        self.assertTrue(created.item_categories.filter(pk=self.category.pk).exists())
        url = reverse('itemdetail', args=[created.pk])
        response = self.client.post(url, self.data(name='Updated', item_categories=[]))
        self.assertEqual(response.status_code, 302)
        created.refresh_from_db()
        self.assertEqual(created.name, 'Updated')
        self.assertFalse(created.item_categories.exists())

    # Checks creation with a selected owner.
    # Kontroluje vytvoření předmětu s vybraným vlastníkem.
    def test_create_with_an_explicit_owner(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('itemcreate'), self.data(owner=self.reader.pk))
        created = Items.objects.get(name='New book')
        self.assertRedirects(response, reverse('itemdetail', args=[created.pk]) + '?saved=1')
        self.assertEqual(created.owner, self.reader)

    # Checks how the owner is displayed in the list and detail.
    # Kontroluje zobrazení vlastníka v seznamu a detailu.
    def test_owner_display_on_list_and_detail(self):
        self.client.force_login(self.reader)
        named_owner = User.objects.create_user('named_owner', first_name='Jana', last_name='Nováková')
        username_only = User.objects.create_user('username_only_owner')
        self.item.owner = named_owner
        self.item.save(update_fields=['owner'])
        other_item = Items.objects.create(name='Other book', owner=username_only)
        unassigned_item = Items.objects.create(name='Unassigned book')

        listing = self.client.get(reverse('items'))
        self.assertEqual(listing.status_code, 200)
        for item, name in (
            (self.item, 'Jana Nováková'),
            (other_item, 'username_only_owner'),
            (unassigned_item, 'Unassigned'),
        ):
            with self.subTest(item=item):
                self.assertRegex(listing.content.decode(), rf'<td>{name}\s*</td>')
                detail = self.client.get(reverse('itemdetail', args=[item.pk]))
                self.assertEqual(detail.status_code, 200)
                self.assertRegex(detail.content.decode(), rf'<p>Owner: {name}\s*</p>')

    # Verifies that invalid item input is rejected.
    # Ověřuje odmítnutí neplatných údajů o předmětu.
    def test_invalid_input_does_not_save(self):
        self.client.force_login(self.admin)
        url = reverse('itemdetail', args=[self.item.pk])
        for data in [self.data(name=''), self.data(item_type=999999), self.data(item_categories=[999999])]:
            self.assertEqual(self.client.post(url, data).status_code, 400)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Hobit')
        count = Items.objects.count()
        self.assertEqual(self.client.post(reverse('itemcreate'), self.data(name='')).status_code, 400)
        self.assertEqual(Items.objects.count(), count)

    # Checks owner selection and persistence during an edit.
    # Kontroluje výběr a uložení vlastníka při úpravě.
    def test_edit_owner_selection_and_save(self):
        self.client.force_login(self.admin)
        owner = User.objects.create_user('owner_account', first_name='Jana', last_name='Nováková')
        url = reverse('itemdetail', args=[self.item.pk])

        response = self.client.get(url + '?edit=1')
        self.assertContains(response, 'Jana Nováková (owner_account)')
        self.assertEqual(response.context['web_data']['form']['owner'].value(), self.admin.pk)
        self.assertRedirects(self.client.post(url, self.data(owner=owner.pk)), url + '?saved=1')
        self.item.refresh_from_db()
        self.assertEqual(self.item.owner, owner)
        self.assertEqual(self.client.get(url + '?edit=1').context['web_data']['form']['owner'].value(), owner.pk)

        self.assertEqual(self.client.post(url, self.data(owner=999999)).status_code, 400)
        self.item.refresh_from_db()
        self.assertEqual(self.item.owner, owner)

        self.assertRedirects(self.client.post(url, self.data(owner='')), url + '?saved=1')
        self.item.refresh_from_db()
        self.assertEqual(self.item.owner, self.admin)

    # Checks deletion confirmation and preservation of catalogue records.
    # Kontroluje potvrzení smazání a zachování číselníkových záznamů.
    def test_delete_requires_confirmation_and_keeps_catalogues(self):
        self.client.force_login(self.admin)
        url = reverse('itemdelete', args=[self.item.pk])
        self.assertContains(self.client.get(url), 'Confirm delete')
        self.assertTrue(Items.objects.filter(pk=self.item.pk).exists())
        self.assertEqual(self.client.post(url, {}).status_code, 400)
        self.assertTrue(Items.objects.filter(pk=self.item.pk).exists())
        self.assertRedirects(self.client.post(url, {'confirm': 'yes'}), reverse('items'))
        self.assertFalse(Items.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(ItemTypes.objects.filter(pk=self.kind.pk).exists())
        self.assertTrue(ItemCategories.objects.filter(pk=self.category.pk).exists())

    # Verifies that a loan protects its item from deletion.
    # Ověřuje, že výpůjčka brání smazání svého předmětu.
    def test_delete_is_blocked_when_item_has_a_loan(self):
        self.client.force_login(self.admin)
        loan = Loans.objects.create(item=self.item, borrower=self.reader)
        url = reverse('itemdelete', args=[self.item.pk])
        detail = reverse('itemdetail', args=[self.item.pk])

        response = self.client.post(url, {'confirm': 'yes'}, follow=True)

        self.assertRedirects(response, detail)
        self.assertContains(response, 'This item cannot be deleted because it has recorded loans.')
        self.assertTrue(Items.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(Loans.objects.filter(pk=loan.pk).exists())

    # Checks permissions and redirects for anonymous users.
    # Kontroluje oprávnění a přesměrování nepřihlášených uživatelů.
    def test_permissions_and_anonymous_redirects(self):
        detail = reverse('itemdetail', args=[self.item.pk])
        delete = reverse('itemdelete', args=[self.item.pk])
        for url in [detail, delete, reverse('itemcreate')]:
            self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.reader)
        response = self.client.get(detail)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '>Edit</a>')
        self.assertNotContains(response, '>Delete</a>')
        for url in [detail+'?edit=1', delete, reverse('itemcreate')]:
            self.assertEqual(self.client.get(url).status_code, 403)
        for url in [detail, delete, reverse('itemcreate')]:
            self.assertEqual(self.client.post(url, self.data(confirm='yes')).status_code, 403)
        self.assertTrue(Items.objects.filter(pk=self.item.pk).exists())

    # Checks permissions for individual item operations.
    # Kontroluje oprávnění jednotlivých operací s předměty.
    def test_operation_specific_permissions(self):
        self.client.force_login(self.reader)
        self.reader.user_permissions.add(Permission.objects.get(codename='add_items', content_type__app_label='whohas'))
        self.assertEqual(self.client.post(reverse('itemcreate'), self.data()).status_code, 302)
        self.assertEqual(self.client.post(reverse('itemdetail', args=[self.item.pk]), self.data()).status_code, 403)
        self.reader.user_permissions.add(Permission.objects.get(codename='change_items', content_type__app_label='whohas'))
        self.assertEqual(self.client.post(reverse('itemdetail', args=[self.item.pk]), self.data()).status_code, 302)
        self.assertEqual(self.client.post(reverse('itemdelete', args=[self.item.pk]), {'confirm': 'yes'}).status_code, 403)
        self.reader.user_permissions.add(Permission.objects.get(codename='delete_items', content_type__app_label='whohas'))
        self.assertEqual(self.client.post(reverse('itemdelete', args=[self.item.pk]), {'confirm': 'yes'}).status_code, 302)

    # Checks CSRF protection and responses for missing items.
    # Kontroluje ochranu CSRF a odpovědi pro chybějící předměty.
    def test_csrf_and_missing_items(self):
        self.client.force_login(self.admin)
        for name in ['itemdetail', 'itemdelete']:
            url = reverse(name, args=[999999])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {'confirm': 'yes'}).status_code, 404)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        for url in [reverse('itemcreate'), reverse('itemdetail', args=[self.item.pk]), reverse('itemdelete', args=[self.item.pk])]:
            self.assertEqual(client.post(url, self.data(confirm='yes')).status_code, 403)

# Tests catalogue lists and access rules.
# Testuje seznamy číselníků a pravidla přístupu.
class CatalogueListTests(TestCase):
    # Creates a user and catalogue records for list tests.
    # Vytváří uživatele a číselníkové záznamy pro testy seznamů.
    def setUp(self):
        self.user = User.objects.create_superuser('catalogue_admin', '', 'test-password')
        self.client.force_login(self.user)
        self.kind = ItemTypes.objects.create(name='Book type')
        self.category = ItemCategories.objects.create(item_category_name='Fiction category')
        self.item = Items.objects.create(name='Assigned book', item_type=self.kind)
        self.item.item_categories.add(self.category)
        ItemTypes.objects.create(name='Unused type')
        ItemCategories.objects.create(item_category_name='Unused category')

    # Checks that catalogue names and assigned items appear.
    # Kontroluje zobrazení názvů číselníků a přiřazených předmětů.
    def test_catalogue_names_and_assigned_items_render(self):
        for route, label in [('itemcategories', 'Fiction category'), ('itemtypes', 'Book type')]:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, label)
                self.assertContains(response, 'Assigned book')
                self.assertContains(response, 'No items assigned.')
                self.assertContains(response, reverse('itemdetail', args=[self.item.pk]))

    # Checks that empty catalogue lists render correctly.
    # Kontroluje správné vykreslení prázdných číselníků.
    def test_empty_catalogues_render(self):
        self.item.delete()
        self.kind.delete()
        self.category.delete()
        ItemTypes.objects.all().delete()
        ItemCategories.objects.all().delete()
        for route in ['itemcategories', 'itemtypes']:
            self.assertContains(self.client.get(reverse(route)), 'No records found.')

    # Checks the permissions required to view catalogues.
    # Kontroluje oprávnění potřebná k zobrazení číselníků.
    def test_catalogue_permissions(self):
        self.client.logout()
        for route in ['itemcategories', 'itemtypes']:
            self.assertEqual(self.client.get(reverse(route)).status_code, 302)
        user = User.objects.create_user('category_reader')
        user.user_permissions.add(Permission.objects.get(content_type__app_label='whohas', codename='view_itemcategories'))
        self.client.force_login(user)
        response = self.client.get(reverse('itemcategories'))
        self.assertContains(response, 'Fiction category')
        self.assertNotContains(response, f'href="{reverse("itemdetail", args=[self.item.pk])}"')
        self.assertEqual(self.client.get(reverse('itemtypes')).status_code, 403)

# Regression tests for administration detail flows and access controls.
# Regresní testy detailů administrace a kontrol přístupu.
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse


# Verify authentication details, validation, permissions, and relationships.
# Ověřuje detaily autentizace, validaci, oprávnění a vztahy.
class AuthDetailTests(TestCase):
    # Create isolated accounts, groups, and permissions for regression tests.
    # Vytváří oddělené účty, skupiny a oprávnění pro regresní testy.
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin', 'admin@example.com', 'test-password')
        cls.reader = User.objects.create_user('reader')
        cls.editor = User.objects.create_user('editor')
        cls.target = User.objects.create_user('target', email='old@example.com')
        cls.group = Group.objects.create(name='public')
        cls.permission = Permission.objects.create(
            name='Custom permission', codename='custom_test',
            content_type=ContentType.objects.get_for_model(Group),
        )
        cls.reader.user_permissions.set(Permission.objects.filter(codename__in=[
            'view_user', 'view_group', 'view_permission'], content_type__app_label='auth'))
        cls.editor.user_permissions.set(Permission.objects.filter(codename__in=[
            'view_user', 'change_user'], content_type__app_label='auth'))

    # Build valid account input with optional test overrides.
    # Sestavuje platné údaje účtu s volitelnými testovacími změnami.
    def user_data(self, **overrides):
        data = {'username': 'target', 'email': 'new@example.com',
                'first_name': 'Test', 'last_name': 'User', 'is_active': 'on'}
        data.update(overrides)
        return data

    # Verify details and lists render.
    # Ověřuje vykreslení detailů a seznamů.
    def test_details_and_lists_render(self):
        self.client.force_login(self.admin)
        for name, pk in [('sysadm-userdet', self.target.pk),
                         ('sysadm-groupdet', self.group.pk),
                         ('sysadm-permissiondet', self.permission.pk)]:
            for suffix in ['', '?edit=1']:
                with self.subTest(name=name, suffix=suffix):
                    response = self.client.get(reverse(name, args=[pk]) + suffix)
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, 'name="csrfmiddlewaretoken"' if suffix else 'Edit')
        for name in ['sysadm-userlist', 'sysadm-grouplist', 'sysadm-permissionlist']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    # Verify read only user cannot edit or post.
    # Ověřuje zákaz editace a POST pro uživatele s právem pouze prohlížet.
    def test_read_only_user_cannot_edit_or_post(self):
        self.client.force_login(self.reader)
        for name, pk in [('sysadm-userdet', self.target.pk),
                         ('sysadm-groupdet', self.group.pk),
                         ('sysadm-permissiondet', self.permission.pk)]:
            url = reverse(name, args=[pk])
            with self.subTest(name=name):
                self.assertEqual(self.client.get(url).status_code, 200)
                self.assertEqual(self.client.get(url + '?edit=1').status_code, 403)
                self.assertEqual(self.client.post(url, {}).status_code, 403)

    # Verify user save including relations and password unchanged.
    # Ověřuje uložení účtu a vztahů bez změny hesla.
    def test_user_save_including_relations_and_password_unchanged(self):
        self.client.force_login(self.admin)
        previous_password = self.target.password
        url = reverse('sysadm-userdet', args=[self.target.pk])
        response = self.client.post(url, self.user_data(
            groups=[self.group.pk], user_permissions=[self.permission.pk]))
        self.assertRedirects(response, url + '?saved=1')
        self.target.refresh_from_db()
        self.assertEqual(self.target.email, 'new@example.com')
        self.assertEqual(self.target.password, previous_password)
        self.assertTrue(self.target.groups.filter(pk=self.group.pk).exists())
        self.assertTrue(self.target.user_permissions.filter(pk=self.permission.pk).exists())
        self.client.post(url, self.user_data())
        self.assertFalse(self.target.groups.exists())
        self.assertFalse(self.target.user_permissions.exists())

    # Verify invalid user preserves data.
    # Ověřuje zachování původních dat při neplatném formuláři.
    def test_invalid_user_preserves_data(self):
        self.client.force_login(self.admin)
        url = reverse('sysadm-userdet', args=[self.target.pk])
        for data in [self.user_data(email='invalid'), self.user_data(username='admin'),
                     self.user_data(groups=['999999'])]:
            with self.subTest(data=data):
                response = self.client.post(url, data)
                self.assertEqual(response.status_code, 400)
                self.target.refresh_from_db()
                self.assertEqual(self.target.email, 'old@example.com')

    # Verify group and permission save and duplicates.
    # Ověřuje ukládání skupin a oprávnění a odmítnutí duplicit.
    def test_group_and_permission_save_and_duplicates(self):
        self.client.force_login(self.admin)
        url = reverse('sysadm-groupdet', args=[self.group.pk])
        self.assertEqual(self.client.post(url, {
            'name': 'renamed', 'permissions': [self.permission.pk]}).status_code, 302)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'renamed')
        self.assertTrue(self.group.permissions.filter(pk=self.permission.pk).exists())
        Group.objects.create(name='duplicate')
        self.assertEqual(self.client.post(url, {'name': 'duplicate'}).status_code, 400)
        url = reverse('sysadm-permissiondet', args=[self.permission.pk])
        data = {'name': 'Updated permission', 'codename': 'updated_test',
                'content_type': self.permission.content_type_id}
        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.codename, 'updated_test')
        Permission.objects.create(name='Existing', codename='duplicate_test',
                                  content_type=self.permission.content_type)
        data['codename'] = 'duplicate_test'
        self.assertEqual(self.client.post(url, data).status_code, 400)

    # Verify non superuser cannot escalate or edit admin.
    # Ověřuje zákaz zvýšení práv a editace správce běžným uživatelem.
    def test_non_superuser_cannot_escalate_or_edit_admin(self):
        self.client.force_login(self.editor)
        url = reverse('sysadm-userdet', args=[self.target.pk])
        self.assertEqual(self.client.post(url, self.user_data(
            is_superuser='on', is_staff='on', groups=[self.group.pk],
            user_permissions=[self.permission.pk])).status_code, 302)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_superuser)
        self.assertFalse(self.target.is_staff)
        self.assertFalse(self.target.groups.exists())
        self.assertFalse(self.target.user_permissions.exists())
        url = reverse('sysadm-userdet', args=[self.admin.pk])
        self.assertEqual(self.client.post(url, self.user_data()).status_code, 403)

    # Verify missing object and anonymous access.
    # Ověřuje chybějící záznamy a anonymní přístup.
    def test_missing_object_and_anonymous_access(self):
        url = reverse('sysadm-userdet', args=[999999])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.admin)
        for name in ['sysadm-userdet', 'sysadm-groupdet', 'sysadm-permissiondet']:
            url = reverse(name, args=[999999])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {}).status_code, 404)

    # Verify csrf is required.
    # Ověřuje povinnou CSRF ochranu.
    def test_csrf_is_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        url = reverse('sysadm-userdet', args=[self.target.pk])
        self.assertEqual(client.post(url, self.user_data()).status_code, 403)

    # Verify group members and bidirectional links.
    # Ověřuje členství ve skupinách a obousměrné odkazy.
    def test_group_members_and_bidirectional_links(self):
        self.target.groups.add(self.group)
        self.client.force_login(self.admin)
        user_url = reverse('sysadm-userdet', args=[self.target.pk])
        group_url = reverse('sysadm-groupdet', args=[self.group.pk])
        for suffix in ['', '?edit=1']:
            with self.subTest(suffix=suffix):
                response = self.client.get(user_url + suffix)
                self.assertContains(response, f'href="{group_url}"')
                response = self.client.get(group_url + suffix)
                self.assertContains(response, f'href="{user_url}"')
                self.assertContains(response, self.target.email)
                self.assertNotContains(response, f'href="{reverse("sysadm-userdet", args=[self.reader.pk])}"')
        self.target.groups.clear()
        self.assertContains(self.client.get(group_url), 'No users assigned to this group.')
        self.assertContains(self.client.get(user_url), 'No groups assigned.')

    # Verify related details respect view permissions.
    # Ověřuje oprávnění k zobrazení souvisejících detailů.
    def test_related_details_respect_view_permissions(self):
        self.target.groups.add(self.group)
        group_reader = User.objects.create_user('group_reader')
        group_reader.user_permissions.add(Permission.objects.get(
            content_type__app_label='auth', codename='view_group'))
        self.client.force_login(group_reader)
        user_url = reverse('sysadm-userdet', args=[self.target.pk])
        group_url = reverse('sysadm-groupdet', args=[self.group.pk])
        response = self.client.get(group_url)
        self.assertNotContains(response, self.target.email)
        self.assertNotContains(response, f'href="{user_url}"')
        self.client.force_login(self.editor)
        self.assertNotContains(self.client.get(user_url), f'href="{group_url}"')

# Verify dashboard aggregates and request diagnostics after refactoring.
# Ověřuje agregace přehledu a diagnostiku požadavků po refaktoringu.
class DashboardTests(TestCase):
    # Keep event counts in one query and exclude old and future records.
    # Zachovává jediný dotaz na počty událostí a vylučuje staré i budoucí záznamy.
    def test_event_counts_use_one_query_and_time_window(self):
        from datetime import timedelta
        from django.utils import timezone
        from sysadm.views.base import SysInfoBase
        from syslog.models import SysLog

        for severity in ['danger', 'info', 'success']:
            SysLog.objects.create(alert_code=severity)
        old = SysLog.objects.create(alert_code='danger')
        future = SysLog.objects.create(alert_code='info')
        SysLog.objects.filter(pk=old.pk).update(timestamp=timezone.now() - timedelta(days=2))
        SysLog.objects.filter(pk=future.pk).update(timestamp=timezone.now() + timedelta(days=2))
        with self.assertNumQueries(1):
            result = SysInfoBase.SysInfoErrors()
        self.assertEqual(list(result.values()), ['1', '1', '1'])

    # Count enabled accounts rather than treating them as online users.
    # Počítá povolené účty a nezaměňuje je za přihlášené uživatele.
    def test_account_summary_uses_one_query(self):
        from sysadm.views.base import SysInfoBase

        User.objects.create_user('enabled')
        User.objects.create_user('disabled', is_active=False)
        with self.assertNumQueries(1):
            self.assertEqual(SysInfoBase.SysInfoUsers(), {'total users': 2, 'active users': 1})

    # Report an unavailable database without exposing the underlying error.
    # Hlásí nedostupnou databázi bez zveřejnění podrobností chyby.
    def test_database_probe_handles_connection_error(self):
        from unittest.mock import patch
        from django.db import DatabaseError
        from sysadm.views.base import SysInfoBase

        with patch('sysadm.views.base.connection.cursor', side_effect=DatabaseError('unavailable')):
            self.assertEqual(SysInfoBase.SysInfoDatabase()['database status'], 'Unavailable')

    # Render the dashboard and permission-protected session and cookie pages.
    # Vykresluje přehled a stránky sessions a cookies chráněné oprávněním.
    def test_dashboard_and_diagnostic_pages(self):
        self.assertContains(self.client.get(reverse('sysadm')), 'Versions')
        admin = User.objects.create_superuser('dashboard_admin', '', 'test-password')
        for name in ['sysadm-sessionsinfo', 'sysadm-cookiesinfo']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)
        self.client.force_login(admin)
        for name in ['sysadm-sessionsinfo', 'sysadm-cookiesinfo']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

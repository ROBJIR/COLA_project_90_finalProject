# Replace Whohas records with a connected sample library.
# Nahrazuje záznamy Whohas provázanou ukázkovou knihovnou.
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from whohas.models import Events, ItemCategories, Items, ItemTypes, Loans, LoanStatuses, WhohasHomePage


BOOKS = (
    ("Hobit", "Fantasy román J. R. R. Tolkiena.", "Pevná vazba", ("Fantasy", "Klasika")),
    ("Malý princ", "Příběh Antoina de Saint-Exupéryho.", "Pevná vazba", ("Klasika", "Pro děti")),
    ("Babička", "Obrazy venkovského života od Boženy Němcové.", "Brožovaná kniha", ("Klasika", "Česká literatura")),
    ("R.U.R.", "Divadelní hra Karla Čapka o robotech.", "Brožovaná kniha", ("Sci-fi", "Česká literatura")),
    ("Duna", "Sci-fi román Franka Herberta z pouštní planety Arrakis.", "Pevná vazba", ("Sci-fi",)),
    ("Stručná historie času", "Populárně-naučná kniha Stephena Hawkinga o vesmíru.", "Brožovaná kniha", ("Populární věda",)),
)

# Each loan uses day offsets relative to the import date.
# Každá výpůjčka používá posuny ve dnech vůči datu importu.
LOAN_EXAMPLES = (
    ("Hobit", "Vrácená výpůjčka", "returned", -21, -7, -21, -9, (
        (-21, "Kniha byla předána čtenářce."),
        (-9, "Čtenářka vrátila knihu v pořádku."),
    )),
    ("Malý princ", "Výpůjčka na čtenářský klub", "borrowed", -3, 11, -3, None, (
        (-3, "Kniha byla vyzvednuta před setkáním čtenářského klubu."),
    )),
    ("Babička", "Rezervace k maturitě", "planned", 4, 18, None, None, (
        (0, "Čtenářka si rezervovala knihu na příští týden."),
    )),
    ("R.U.R.", "Ukončená výpůjčka ke čtenářskému deníku", "success", -35, -21, -34, -22, (
        (-35, "Termín výpůjčky byl domluven."),
        (-34, "Kniha byla předána o den později."),
        (-22, "Vrácení bylo potvrzeno a výpůjčka uzavřena."),
    )),
)


# Import sample books, loan histories, and home page articles.
# Importuje ukázkové knihy, historii výpůjček a články úvodní stránky.
class Command(BaseCommand):
    help = "Replace all Whohas data with sample books and related records."

    # Require the caller to select the destructive replacement explicitly.
    # Vyžaduje, aby volající výslovně zvolil nahrazení původních dat.
    def add_arguments(self, parser):
        parser.add_argument("--replace", action="store_true", help="Delete existing Whohas records before importing.")

    # Create or reuse an inactive demo account without modifying existing accounts.
    # Vytváří nebo znovu používá neaktivní ukázkový účet bez změny existujících účtů.
    def demo_user(self, username, first_name, last_name):
        user, _ = get_user_model().objects.get_or_create(
            username=username,
            defaults={"first_name": first_name, "last_name": last_name, "is_active": False, "password": "!"},
        )
        if user.is_active or user.has_usable_password() or user.is_staff or user.is_superuser or (
            user.first_name, user.last_name
        ) != (first_name, last_name):
            raise CommandError(f"Účet {username!r} je už obsazen. Import byl vrácen zpět.")
        return user

    # Replace all Whohas records in one transaction, deleting dependent rows first.
    # Nahrazuje všechny záznamy Whohas v jedné transakci a nejprve maže závislé záznamy.
    @transaction.atomic
    def handle(self, *args, **options):
        if not options["replace"]:
            raise CommandError("Pro nahrazení stávajících dat Whohas přidejte --replace.")

        owner = self.demo_user("whohas-demo-knihovnik", "Jan", "Knihovník")
        borrower = self.demo_user("whohas-demo-ctenarka", "Eva", "Čtenářka")

        for model in (Events, Loans, Items, LoanStatuses, ItemCategories, ItemTypes, WhohasHomePage):
            model.objects.all().delete()

        WhohasHomePage.objects.bulk_create([
            WhohasHomePage(
                article_code="demo-knihovna", article_sequence=10,
                aticle_content="Ukázková knihovna eviduje knihy, jejich žánry a dostupnost.",
            ),
            WhohasHomePage(
                article_code="demo-vypujcky", article_sequence=20,
                aticle_content="U výpůjček najdete plánované termíny, skutečná předání a historii vrácení.",
            ),
        ])

        types = {
            name: ItemTypes.objects.create(name=name)
            for name in ("Pevná vazba", "Brožovaná kniha")
        }
        categories = {
            name: ItemCategories.objects.create(item_category_name=name)
            for name in sorted({category for _, _, _, names in BOOKS for category in names})
        }
        books = {}
        for title, description, binding, genres in BOOKS:
            book = Items.objects.create(name=title, description=description, owner=owner, item_type=types[binding])
            book.item_categories.set(categories[genre] for genre in genres)
            books[title] = book

        statuses = {
            name: LoanStatuses.objects.create(name=name, format={"bgcolor": background, "color": color})
            for name, background, color in (
                ("planned", "secondary", "white"),
                ("borrowed", "warning", "dark"),
                ("returned", "info", "dark"),
                ("success", "success", "white"),
            )
        }

        now = timezone.now().replace(microsecond=0)
        events = []
        for title, label, status, planned_start, planned_end, real_start, real_end, history in LOAN_EXAMPLES:
            loan = Loans.objects.create(
                name=label,
                description=f"Ukázková výpůjčka knihy {title}.",
                item=books[title],
                borrower=borrower,
                status=statuses[status],
                tstamp_planned_start=now + timedelta(days=planned_start),
                tstamp_planned_end=now + timedelta(days=planned_end),
                tstamp_real_start=now + timedelta(days=real_start) if real_start is not None else None,
                tstamp_real_end=now + timedelta(days=real_end) if real_end is not None else None,
            )
            events.extend(
                Events(loan=loan, author=owner, tstamp=now + timedelta(days=day), description=description)
                for day, description in history
            )
        Events.objects.bulk_create(events)

        self.stdout.write(self.style.SUCCESS(
            f"Whohas: 2 články, {len(types)} typy, {len(categories)} kategorií, "
            f"{len(books)} knih, {len(statuses)} stavy, {len(LOAN_EXAMPLES)} výpůjčky a {len(events)} událostí."
        ))

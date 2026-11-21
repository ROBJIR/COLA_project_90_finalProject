# Replace Whohas records with a connected sample library.
# Nahrazuje záznamy Whohas provázanou ukázkovou knihovnou.
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from meta.models import Interfaces, Instances, Databases, DatabaseType, InterfaceType, Meta, Environments

DATABASES = (
    ("G5CZ", "PROD", "19.3.0", (
        ("G5CZSZ", (("alma","server"), ("almasrvc","interface"), ("almadg","dg-interface"),)),
        ("G5CZTM", (("mater","server"), ("matersrvc","interface"), ("materdg","dg-interface"),)),
    )),
    ("G5ACCCZ", "ACC", "19.3.0", (
        ("G5ACCCZSZ", (("jumbo","server"), ("jumbosrvc","interface"),)),
        ("G5ACCCZTM", (("felix","server"), ("felixsrvc","interface"),)),
    )),
    ("APEXADB", "ACC", "19.3.0", (
        ("APEXADBSZ", (("journal","server"), ("journalsrvc","interface"),)),
        ("APEXADBTM", (("focus","server"), ("focussrvc","interface"),)),
    )),
    ("APEXDB", "PROD", "19.3.0", (
        ("APEXDBSZ", (("argon","server"), ("argonsrvc","interface"), ("argondg","dg-interface"),)),
        ("APEXDBTM", (("metan","server"), ("metansrvc","interface"), ("metandg","dg-interface"),)),
    )),
    ("DATAHUBP", "PROD", "19.3.0", (
        ("DATAHUBPSZ", (("java","server"),("javasrvc","interface"),("javadg","dg-interface"),)),
        ("DATAHUBPTM", (("fortran","server"),("fortransrvc","interface"),("fortrandg","dg-interface"),)),
    )),
    ("DATAHUBA", "ACC", "19.3.0", (
        ("DATAHUBA", (("jedi","server"),("jedisrvc","interface"),)),
    )),
    ("MON2DB", "PROD", "19.3.0", (
        ("MON2DB", (("face","server"),("facesrvc","interface"),)),
    )),
    ("MON2ACC", "ACC", "19.3.0", (
        ("MON2ACC", (("jewel","server"),("jewelsrvc","interface"),)),
    )),
)

class Command(BaseCommand):
    help = "Replace all META data with DATABASE structure."

    # Require the caller to select the destructive replacement explicitly.
    # Vyžaduje, aby volající výslovně zvolil nahrazení původních dat.
    def add_arguments(self, parser):
        parser.add_argument("--replace", action="store_true", help="Delete existing META records before importing.")

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
            raise CommandError("Pro nahrazení stávajících dat META přidejte --replace.")

        for model in (Interfaces, Instances, Databases, DatabaseType, InterfaceType, Meta, Environments ):
            model.objects.all().delete()

        Meta.objects.bulk_create([
            Meta(
                article_code="01", article_sequence=10,
                aticle_content="<strong>Datababses</strong> ...",
            ),
            Meta(
                article_code="02", article_sequence=20,
                aticle_content="<strong>Instances</strong> ...",
            ),
            Meta(
                article_code="03", article_sequence=30,
                aticle_content="<strong>Interfaces</strong> ...",
            ),
        ])

        databasetype = {
            dtype: DatabaseType.objects.create(database_type=dtype, format={"bgcolor": background, "icon": icon})
            for dtype, background, icon in (("single instance", "transparent", "database"),
                                            ("dataguard", "transparent", "dataguard"),)
        }
        interfacetype = {
            itype: InterfaceType.objects.create(interface_type=itype, format={"icon": icon})
            for itype, icon in (("interface",   "interface"),
                                ("dg-interface", "dg-interface"),
                                ("server",      "server"), )
        }
        environments = {
            ename: Environments.objects.create(name=ename, format={"bg-color": bg_color})
            for ename, bg_color in (("PROD", "red"),
                                    ("ACC",  "orange"),
                                    ("DEV", "blue"),
                                    ("TRN", "green"),
                                    )
        }
        idbs=0
        iinst = 0
        interface_count = 0
        for dbs_name, env, prop_version, instances in DATABASES:
            idbs += 1
            dbs = Databases.objects.create(database_name=dbs_name, environment=environments[env], properties={"version": prop_version})
            for instance_name, interfaces in instances:
                iinst += 1
                inst = Instances.objects.create(instance_name=instance_name, database=dbs)
                for interface_name, interface_type in interfaces:
                    interface_count += 1
                    interface = Interfaces.objects.create(
                        interface_name=interface_name,
                        interface_type=interfacetype[interface_type],
                        interface_ip_address=f"192.168.1.{interface_count}",
                    )
                    interface.instance.add(inst)

        self.stdout.write(self.style.SUCCESS(
            f"import META ... \
            \n - meta: 3 rows \
            \n - database types:  {len(databasetype)} \
            \n - interface types: {len(interfacetype)} \
            \n - environments:    {len(environments)} \
            \n - databases:       {idbs} \
            \n - instances:       {iinst} \
            \n - interfaces:      {interface_count} "
        ))

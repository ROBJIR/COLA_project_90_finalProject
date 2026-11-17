# Collect system, database, account, and event summaries for the administration dashboard.
# Shromažďuje přehled systému, databáze, účtů a událostí pro administraci.
from datetime import timedelta
import platform

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import DatabaseError, connection
from django.db.models import Count, Q
from django.utils import timezone

from syslog.models import SysLog


# Collect dashboard values without storing request state.
# Získává hodnoty přehledu bez ukládání stavu požadavku.
class SysInfoBase:
    # Return Django and Python versions.
    # Vrací verze Django a Pythonu.
    @staticmethod
    def SysInfoSystem():
        return {
            "django version": django.get_version(),
            "python version": platform.python_version(),
        }

    # Return database metadata and check connection availability.
    # Vrací údaje databáze a ověřuje dostupnost připojení.
    @staticmethod
    def SysInfoDatabase():
        name = str(connection.settings_dict["NAME"])
        database_info = {
            "database type": connection.vendor,
            "database engine": connection.settings_dict["ENGINE"],
            "database name": f"... {name[-56:]}" if len(name) > 60 else name,
        }
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            database_info["database status"] = "Ready"
        except DatabaseError:
            database_info["database status"] = "Unavailable"
        return database_info

    # Count all and enabled accounts in a single query.
    # Jediným dotazem počítá všechny a povolené účty.
    @staticmethod
    def SysInfoUsers():
        counts = get_user_model().objects.aggregate(
            total=Count("pk"),
            active=Count("pk", filter=Q(is_active=True)),
        )
        return {"total users": counts["total"], "active users": counts["active"]}

    # Count event severities over the last 24 hours in one query.
    # Jediným dotazem počítá závažnosti událostí za posledních 24 hodin.
    @staticmethod
    def SysInfoErrors():
        now = timezone.now()
        # One aggregate query replaces three independent count queries.
        # Jeden agregační dotaz nahrazuje tři samostatné dotazy na počty.
        counts = SysLog.objects.filter(
            timestamp__gte=now - timedelta(hours=24), timestamp__lte=now,
        ).aggregate(
            danger=Count("pk", filter=Q(alert_code="danger")),
            info=Count("pk", filter=Q(alert_code="info")),
            success=Count("pk", filter=Q(alert_code="success")),
        )
        return {
            "DANGER  - 24 hours": str(counts["danger"]),
            "INFO    - 24 hours": str(counts["info"]),
            "SUCCESS - 24 hours": str(counts["success"]),
        }

    # Return the configured debug mode.
    # Vrací nastavený režim ladění.
    @staticmethod
    def SysInfoWeb():
        return {"debug mode": "ON" if settings.DEBUG else "OFF"}

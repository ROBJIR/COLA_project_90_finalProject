# Retain permission-holder models for session and cookie inspection; no session values are stored here.
# Zachovává modely poskytující oprávnění k prohlížení sessions a cookies; jejich hodnoty zde neukládá.
from django.db import models


# Provide Django permissions for viewing session diagnostics.
# Poskytuje Django oprávnění k prohlížení diagnostiky sessions.
class SessionList(models.Model):
    boolean = models.BooleanField(default=False)


# Provide Django permissions for viewing cookie diagnostics.
# Poskytuje Django oprávnění k prohlížení diagnostiky cookies.
class CookieList(models.Model):
    boolean = models.BooleanField(default=False)

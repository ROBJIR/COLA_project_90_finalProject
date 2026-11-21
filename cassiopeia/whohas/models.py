# Retain permission-holder models for session and cookie inspection; no session values are stored here.
# Zachovává modely poskytující oprávnění k prohlížení sessions a cookies; jejich hodnoty zde neukládá.
from django.conf import settings
from django.db import models
from django.utils import timezone

# Stores content for the Whohas home page.
# Ukládá obsah úvodní stránky Whohas.
class WhohasHomePage(models.Model):
     article_code = models.CharField(max_length=24, null=True)
     article_sequence = models.PositiveIntegerField(null=False)
     aticle_content = models.TextField(null=True)

# Defines a type used to classify items.
# Definuje typ pro třídění předmětů.
class ItemTypes(models.Model):
     name = models.CharField(max_length=120, unique=True)
     # Returns the item type name.
     # Vrací název typu předmětu.
     def __str__(self):
          return self.name

# Defines a category used to group items.
# Definuje kategorii pro seskupování předmětů.
class ItemCategories(models.Model):
     item_category_name = models.CharField(max_length=120, null=True)

# Stores a tracked item and its relationships.
# Ukládá evidovaný předmět a jeho vazby.
class Items(models.Model):
     name = models.CharField(max_length=120, null=False, db_index=True)
     description = models.TextField(null=True, blank=True)
     owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT, null=True, blank=True,)
     item_type = models.ForeignKey("ItemTypes", on_delete=models.PROTECT, related_name="items", null=True, blank=True,)
     item_categories = models.ManyToManyField("ItemCategories", related_name="items", blank=True,)
     # Returns the item name.
     # Vrací název předmětu.
     def __str__(self):
          return self.name

# Defines the possible states of a loan.
# Definuje možné stavy výpůjčky.
class LoanStatuses(models.Model):
     name = models.CharField(max_length=24, null=False, db_index=True)
     format = models.JSONField(default=dict, null=True)
     # Returns the loan status name.
     # Vrací název stavu výpůjčky.
     def __str__(self):
          return self.name

# Stores a loan, including its item, dates, and status.
# Ukládá výpůjčku včetně předmětu, dat a stavu.
class Loans(models.Model):
     tstamp_planned_start = models.DateTimeField(default=timezone.now)
     tstamp_planned_end = models.DateTimeField(null=True, blank=True,)
     tstamp_real_start = models.DateTimeField(null=True, blank=True,)
     tstamp_real_end = models.DateTimeField(null=True, blank=True,)
     description = models.TextField(null=True, blank=True)
     status = models.ForeignKey("LoanStatuses", on_delete=models.PROTECT, related_name="loans", null=True, blank=True, )
     item = models.ForeignKey("Items", on_delete=models.PROTECT, related_name="loans", null=True, blank=True, )
     borrower = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT, null=False, blank=False,)
     # Returns the display label for the loan.
     # Vrací označení výpůjčky pro zobrazení.
     def __str__(self):
          return self.name

# Stores an event associated with a loan.
# Ukládá událost spojenou s výpůjčkou.
class Events(models.Model):
     tstamp = models.DateTimeField(default=timezone.now)
     description = models.TextField(null=True, blank=True)
     loan = models.ForeignKey("Loans", on_delete=models.PROTECT, related_name="loan", null=True, blank=True, )
     author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="whohas_events")
     # Returns the display label for the event.
     # Vrací označení události pro zobrazení.
     def __str__(self):
          return f"Event #{self.pk}" if self.pk is not None else "New event"

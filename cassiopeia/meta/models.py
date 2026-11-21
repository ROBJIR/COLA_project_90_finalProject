from django.conf import settings
from django.db import models
from django.utils import timezone

# Stores content for the Whohas home page.
# Ukládá obsah úvodní stránky Whohas.
class Meta(models.Model):
     article_code = models.CharField(max_length=24, null=True)
     article_sequence = models.PositiveIntegerField(null=False)
     aticle_content = models.TextField(null=True)
     format = models.JSONField(default=dict, null=True, blank=True)

class DatabaseType(models.Model):
    database_type = models.CharField(max_length=16, unique=True)
    format = models.JSONField(default=dict, null=True)
    def __str__(self):
        return self.database_type

class Environments(models.Model):
    name = models.CharField(max_length=16, unique=True)
    format = models.JSONField(default=dict, null=True)
    def __str__(self):
        return self.name

class Databases(models.Model):
     database_name  = models.CharField(max_length=120, unique=True)
     database_type  = models.ForeignKey("DatabaseType", on_delete=models.PROTECT, related_name="databases", null=True, blank=True, )
     environment = models.ForeignKey("Environments", on_delete=models.PROTECT, related_name="databases", null=True,
                                       blank=True, )
     properties = models.JSONField(default=dict, null=True)
     def __str__(self):
          return self.database_name

class Instances(models.Model):
    instance_name = models.CharField(max_length=120, unique=True)
    database = models.ForeignKey("Databases", on_delete=models.PROTECT, related_name="instances", null=True, blank=True, )
    properties = models.JSONField(default=dict, null=True)
    listeners = models.JSONField(default=dict, null=True)
    def __str__(self):
        return self.instance_name

class InterfaceType(models.Model):
    interface_type = models.CharField(max_length=16, unique=True)
    format = models.JSONField(default=dict, null=True)
    def __str__(self):
        return self.interface_type

class Interfaces(models.Model):
    interface_name = models.CharField(max_length=120, unique=True)
    interface_ip_address = models.CharField(max_length=22, unique=True)
    interface_type = models.ForeignKey("InterfaceType", on_delete=models.PROTECT, related_name="interfaces", null=True, blank=True, )
    instance = models.ManyToManyField("Instances", related_name="instances", blank=True,)
    domain_alias = properties = models.JSONField(default=dict, null=True)
    properties = models.JSONField(default=dict, null=True)
    def __str__(self):
        return self.interface_name

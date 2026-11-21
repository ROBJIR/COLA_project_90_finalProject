from django.contrib import admin

# Register your models here.
# Configure Django admin lists, filters, and searches for application and web logs.
# Nastavuje seznamy, filtry a vyhledávání aplikačních a webových logů v administraci Django.
from django.contrib import admin
from .models import Meta, Databases, Instances, Interfaces, DatabaseType, InterfaceType, Environments


@admin.register(Meta)
# Configure application log administration.
# Nastavuje administraci aplikačních logů.
class Meta(admin.ModelAdmin):
    list_display = (
        'article_code',
        'article_sequence',
        'aticle_content'
    )
    list_filter = ('article_code', 'article_sequence', 'aticle_content')
    search_fields = ('article_code', 'article_sequence')
    ordering = ('article_sequence',)

@admin.register(Environments)
class EnvironmentsAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Databases)
class DatabasesAdmin(admin.ModelAdmin):
    list_display = ("id", "database_name", "database_type", "properties")
    search_fields = ("database_name","database_type")
    ordering = ("database_name", "database_type")

@admin.register(Instances)
class InstancesAdmin(admin.ModelAdmin):
    list_display = ("id", "instance_name", "properties")
    search_fields = ("instance_name",)
    ordering = ("instance_name",)

@admin.register(Interfaces)
class InterfacesAdmin(admin.ModelAdmin):
    list_display = ("id", "interface_name", "interface_ip_address", "properties")
    search_fields = ("interface_name",)
    ordering = ("interface_name",)

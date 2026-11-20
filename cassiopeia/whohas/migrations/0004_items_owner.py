import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


# Adds an owner relationship to items.
# Přidává k předmětům vazbu na vlastníka.
class Migration(migrations.Migration):

    dependencies = [
        ('whohas', '0003_itemcategories_itemtypes_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='items',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

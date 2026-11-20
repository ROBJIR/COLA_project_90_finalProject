import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


# Renames the loan model, adds loan dates, and creates events.
# Přejmenovává model výpůjček, přidává termíny výpůjček a vytváří události.
class Migration(migrations.Migration):
    dependencies = [
        ("whohas", "0007_alter_loanstatuses_format"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(old_name="Loan", new_name="Loans"),
        migrations.AddField(
            model_name="loans",
            name="tstamp_planned_start",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="loans",
            name="tstamp_planned_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="loans",
            name="tstamp_real_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="loans",
            name="tstamp_real_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="Events",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tstamp", models.DateTimeField(default=django.utils.timezone.now)),
                ("description", models.TextField(blank=True, null=True)),
                ("author", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="whohas_events",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
    ]

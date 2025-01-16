# Generated by Django 4.2.19 on 2025-04-10 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0015_alter_application_index_together"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="application",
            new_name="application_created_ca3f79_idx",
            old_fields=("created_time",),
        ),
        migrations.RenameIndex(
            model_name="application",
            new_name="application_callbac_497d8e_idx",
            old_fields=("callback_id", "sn"),
        ),
    ]

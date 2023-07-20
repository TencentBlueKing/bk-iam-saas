# Generated by Django 3.2.16 on 2023-07-20 08:02

from django.core.management import call_command
from django.db import migrations


def run_migrate_role_resource_label(apps, schema_editor):
    call_command("migrate_role_resource_label")


class Migration(migrations.Migration):

    dependencies = [
        ("role", "0015_roleresourcelabel"),
    ]

    operations = [migrations.RunPython(run_migrate_role_resource_label)]

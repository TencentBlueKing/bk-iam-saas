# Generated by Django 3.2.16 on 2024-02-22 06:16

from django.core.management import call_command
from django.db import migrations


def run_migrate_role_group_member(apps, schema_editor):
    call_command("migrate_role_group_member")


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0022_alter_scopesubject_index_together'),
    ]

    operations = [migrations.RunPython(run_migrate_role_group_member)]

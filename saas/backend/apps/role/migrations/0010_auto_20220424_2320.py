# Generated by Django 2.2.25 on 2022-04-24 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0009_rolesource'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roleuser',
            options={'ordering': ['id'], 'verbose_name': '角色的用户', 'verbose_name_plural': '角色的用户'},
        ),
        migrations.AddIndex(
            model_name='rolerelatedobject',
            index=models.Index(fields=['object_id', 'object_type'], name='role_rolere_object__30736f_idx'),
        ),
    ]

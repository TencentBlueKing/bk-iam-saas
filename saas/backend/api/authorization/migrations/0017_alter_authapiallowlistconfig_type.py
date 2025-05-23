# Generated by Django 4.2.19 on 2025-04-10 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0016_alter_authapiallowlistconfig_index_together_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authapiallowlistconfig",
            name="type",
            field=models.CharField(
                choices=[
                    ("authorization_instance", "实例授权"),
                    ("creator_authorization_instance", "新建关联实例授权"),
                    ("authorization_attribute", "属性授权"),
                ],
                max_length=32,
                verbose_name="API类型",
            ),
        ),
    ]

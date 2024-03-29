# Generated by Django 3.2.16 on 2023-02-03 09:06

from django.db import migrations


def delete_sensitive_user_property(apps, schema_editor):
    """删除敏感用户属性"""
    UserProperty = apps.get_model("account", "UserProperty")

    UserProperty.objects.filter(key="qq").delete()
    UserProperty.objects.filter(key="phone").delete()
    UserProperty.objects.filter(key="email").delete()
    UserProperty.objects.filter(key="wx_userid").delete()
    UserProperty.objects.filter(key="chname").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_init_superuser"),
    ]

    operations = [migrations.RunPython(delete_sensitive_user_property)]

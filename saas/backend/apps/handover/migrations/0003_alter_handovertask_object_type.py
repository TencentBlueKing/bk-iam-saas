# Generated by Django 3.2.16 on 2023-12-12 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handover', '0002_auto_20221213_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handovertask',
            name='object_type',
            field=models.CharField(choices=[('group_ids', '用户组权限'), ('custom_policies', '自定义权限'), ('role_ids', '管理员权限'), ('subject_template_ids', '人员模版权限')], max_length=32, verbose_name='权限类别'),
        ),
    ]

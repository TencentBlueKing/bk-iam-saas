# Generated by Django 2.2.28 on 2022-08-31 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPermissionCleanupRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.CharField(max_length=64, verbose_name='创建者')),
                ('updater', models.CharField(max_length=64, verbose_name='更新者')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('username', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='用户名')),
                ('status', models.CharField(choices=[('created', '已创建'), ('running', '正在清理'), ('succeed', '交接成功'), ('failed', '交接失败')], default='created', max_length=32, verbose_name='单据状态')),
                ('error_info', models.TextField(default='', verbose_name='交接异常信息')),
            ],
            options={
                'verbose_name': '用户权限清理记录',
                'verbose_name_plural': '用户权限清理记录',
            },
        ),
    ]

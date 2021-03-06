# Generated by Django 2.2.14 on 2021-08-31 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAPIAllowListConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.CharField(max_length=64, verbose_name='创建者')),
                ('updater', models.CharField(max_length=64, verbose_name='更新者')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('api', models.CharField(choices=[('group_list', '获取用户组列表'), ('group_member_list', '获取用户组成员列表'), ('subject_joined_group_list', '获取Subject加入的用户组列表')], help_text='*代表任意', max_length=32, verbose_name='API')),
                ('app_code', models.CharField(max_length=32, verbose_name='API调用者')),
            ],
            options={
                'verbose_name': 'Admin API允许的应用白名单',
                'verbose_name_plural': 'Admin API允许的应用白名单',
                'ordering': ['-id'],
                'index_together': {('app_code', 'api')},
            },
        ),
    ]

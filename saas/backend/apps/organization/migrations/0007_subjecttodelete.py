# Generated by Django 3.2.16 on 2023-12-26 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0006_auto_20211104_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectToDelete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('subject_id', models.CharField(max_length=255, verbose_name='Subject ID')),
                ('subject_type', models.CharField(max_length=64, verbose_name='Subject Type')),
            ],
            options={
                'verbose_name': '待删除的Subject',
                'verbose_name_plural': '待删除的Subject',
                'unique_together': {('subject_type', 'subject_id')},
            },
        ),
    ]

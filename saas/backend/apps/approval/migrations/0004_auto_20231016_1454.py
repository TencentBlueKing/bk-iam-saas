# Generated by Django 3.2.16 on 2023-10-16 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval', '0003_auto_20221213_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionprocessrelation',
            name='sensitivity_level',
            field=models.CharField(choices=[('L1', '不敏感'), ('L2', '低'), ('L3', '中'), ('L4', '高')], default='L1', max_length=32, verbose_name='敏感等级'),
        ),
        migrations.AlterField(
            model_name='approvalprocessglobalconfig',
            name='application_type',
            field=models.CharField(choices=[('grant_action', '自定义权限申请'), ('renew_action', '自定义权限续期'), ('join_group', '加入用户组'), ('renew_group', '用户组续期'), ('join_rating_manager', '加入管理空间'), ('create_rating_manager', '创建管理空间'), ('update_rating_manager', '修改管理空间'), ('grant_temporary_action', '临时权限申请')], max_length=32, unique=True, verbose_name='申请类型'),
        ),
    ]

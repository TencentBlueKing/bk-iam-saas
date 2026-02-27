# -*- coding: utf-8 -*-
from django.db import migrations, models


AUDIT_MANAGER_TYPE = "audit_manager"

def add_audit_manager_role(apps, schema_editor):
    """添加审计管理员角色"""
    Role = apps.get_model('role', 'Role')
    
    # 检查是否已存在审计管理员角色
    if not Role.objects.filter(type=AUDIT_MANAGER_TYPE).exists():
        Role.objects.create(
            type=AUDIT_MANAGER_TYPE,
            code='audit_manager',
            name='审计管理员',
            name_en='Audit Manager',
            description='审计管理员，拥有查看所有审计日志的权限',
            hidden=False
        )


def remove_audit_manager_role(apps, schema_editor):
    """移除审计管理员角色"""
    Role = apps.get_model('role', 'Role')
    RoleUser = apps.get_model('role', 'RoleUser')
    
    # 先删除角色关联的用户
    audit_role = Role.objects.filter(type=AUDIT_MANAGER_TYPE).first()
    if audit_role:
        RoleUser.objects.filter(role_id=audit_role.id).delete()
        audit_role.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0028_rename_rolecommonaction_role_id_system_id_role_roleco_role_id_b747b6_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='type',
            field=models.CharField(
                choices=[
                    ('staff', '个人用户'), 
                    ('super_manager', '超级管理员'), 
                    ('system_manager', '系统管理员'), 
                    ('rating_manager', '管理空间管理员'), 
                    ('subset_manager', '二级管理空间管理员'),
                    ('audit_manager', '审计管理员')
                ], 
                db_index=True, 
                max_length=32, 
                verbose_name='类型'
            ),
        ),
        migrations.RunPython(add_audit_manager_role, remove_audit_manager_role),
    ]

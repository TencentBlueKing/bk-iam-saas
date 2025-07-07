# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.urls import path

from . import views

urlpatterns = [
    # 用户组
    path("groups/", views.AdminGroupViewSet.as_view({"get": "list", "post": "create"}), name="open.admin.group"),
    # 用户组基本信息更新 & 删除
    path(
        "groups/<int:id>/",
        views.AdminGroupInfoViewSet.as_view({"put": "update", "delete": "destroy"}),
        name="open.admin.group",
    ),
    # 用户组成员
    path(
        "groups/<int:id>/members/",
        views.AdminGroupMemberViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
        name="open.admin.group_member",
    ),
    # 用户组授权
    path(
        "groups/<str:id>/policies/",
        views.AdminGroupPolicyViewSet.as_view({"post": "create"}),
        name="open.admin.group_policy",
    ),
    # 模板
    path(
        "templates/",
        views.AdminTemplateViewSet.as_view({"get": "list", "post": "create"}),
        name="open.admin.template",
    ),
    # Subject
    path(
        "subjects/<str:subject_type>/<str:subject_id>/groups/",
        views.AdminSubjectGroupViewSet.as_view({"get": "list"}),
        name="open.admin.subject_group",
    ),
    # 系统列表 list(不分页, 或者分页, page_size不传默认100?)
    path(
        "systems/",
        views.AdminSystemViewSet.as_view({"get": "list"}),
        name="open.admin.system",
    ),
    # 系统回调信息
    path(
        "systems/<str:system_id>/provider_config/",
        views.AdminSystemProviderConfigViewSet.as_view({"get": "list"}),
        name="open.admin.system_provider_config",
    ),
    # 超级管理员成员列表  get
    path(
        "roles/super_managers/members/",
        views.AdminSuperManagerMemberViewSet.as_view({"get": "retrieve"}),
        name="open.admin.super_manager.members",
    ),
    # 系统管理员成员列表 get
    path(
        "roles/system_managers/systems/<slug:system_id>/members/",
        views.AdminSystemManagerMemberViewSet.as_view({"get": "retrieve"}),
        name="open.admin.system_manager.members",
    ),
    # 用户的角色列表, list分页 (可以filter=super/system/grade来过滤是否分级管理员) 注意这里路径中user是type, 所以不是users
    path(
        "subjects/user/<str:subject_id>/roles/",
        views.AdminSubjectRoleViewSet.as_view({"get": "list"}),
        name="open.admin.subject.roles",
    ),
    # user permission exists
    path(
        "subjects/user/<str:subject_id>/permission/exists/",
        views.AdminSubjectPermissionExistsViewSet.as_view({"get": "list"}),
        name="open.admin.subject.permission",
    ),
    # 冻结, 解冻, 查询冻结的用户列表接口 (冻结这个用户在蓝鲸平台的所有权限, 包括权限中心本身; 注意只能冻结用户, 部门和组无法冻结)
    path(
        "freeze/users/",
        views.AdminSubjectFreezeViewSet.as_view({"get": "list", "post": "freeze", "delete": "unfreeze"}),
        name="open.admin.subject.freeze",
    ),
    # 审计查询接口: 事件查询列表
    path(
        "audits/events/",
        views.AdminAuditEventViewSet.as_view({"get": "list"}),
        name="open.admin.audit.events",
    ),
    # 清理用户权限
    path(
        "cleanup/users/permission/",
        views.AdminSubjectPermissionCleanupViewSet.as_view({"delete": "cleanup"}),
        name="open.admin.subject.cleanup",
    ),
    # 用户所在用户组的所有权限
    path(
        "subjects/user/<str:subject_id>/group/permission/",
        views.AdminSubjectGroupPermissionViewSet.as_view({"get": "list"}),
        name="admin.subject.group.permission",
    ),
    # 用户的自定义权限
    path(
        "subjects/user/<str:subject_id>/custom/permission/",
        views.AdminSubjectCustomPermissionViewSet.as_view({"get": "list"}),
        name="admin.subject.custom.permission",
    ),
    # 用户的管理权限
    path(
        "subjects/user/<str:subject_id>/management/permission/",
        views.AdminSubjectManagementPermissionViewSet.as_view({"get": "list"}),
        name="admin.subject.manage.permission",
    ),
]

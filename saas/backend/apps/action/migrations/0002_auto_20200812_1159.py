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
# Generated by Django 2.2.14 on 2020-08-12 03:48

import json

from django.db import migrations

from backend.util.json import json_dumps


def init_aggregate_action(apps, schema_editor):
    AggregateAction = apps.get_model("action", "AggregateAction")

    aas = []
    for agg_action in _default_aggregate_actions:
        aa = AggregateAction(
            system_id=agg_action["system_id"],
            _action_ids=json_dumps(agg_action["action_ids"]),
            _aggregate_resource_type=json_dumps(agg_action["aggregate_resource_type"]),
        )

        aas.append(aa)

    AggregateAction.objects.bulk_create(aas)


class Migration(migrations.Migration):

    dependencies = [
        ("action", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(init_aggregate_action),
    ]


_default_aggregate_actions = [
    {
        "system_id": "bk_bcs_app",
        "action_ids": ["project_view", "project_edit"],
        "aggregate_resource_type": {"system_id": "bk_bcs_app", "id": "project"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": [
            "find_business_resource",
            "edit_biz_host",
            "create_biz_topology",
            "edit_biz_topology",
            "delete_biz_topology",
            "create_biz_service_instance",
            "edit_biz_service_instance",
            "delete_biz_service_instance",
            "create_biz_service_template",
            "edit_biz_service_template",
            "delete_biz_service_template",
            "create_biz_set_template",
            "edit_biz_set_template",
            "delete_biz_set_template",
            "create_biz_service_category",
            "edit_biz_service_category",
            "delete_biz_service_category",
            "create_biz_dynamic_query",
            "edit_biz_dynamic_query",
            "delete_biz_dynamic_query",
            "edit_biz_custom_field",
            "edit_biz_host_apply",
            "edit_business",
            "archive_business",
            "find_business",
        ],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "biz"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["create_resource_pool_host", "edit_resource_pool_directory", "delete_resource_pool_directory",],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_resource_pool_directory"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_resource_pool_host", "delete_resource_pool_host",],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_host_rsc_pool_directory"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["create_sys_instance", "edit_sys_instance", "delete_sys_instance"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_instance_model"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_cloud_account", "delete_cloud_account", "find_cloud_account"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_cloud_account"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_cloud_resource_task", "delete_cloud_resource_task", "find_cloud_resource_task"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_cloud_resource_task"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_cloud_area", "delete_cloud_area"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_cloud_area"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_event_subscription", "delete_event_subscription", "find_event_subscription"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_event_pushing"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_model_group", "delete_model_group"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_model_group"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_sys_model", "delete_sys_model"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_model"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_association_type", "delete_association_type"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "sys_association_type"},
    },
    {
        "system_id": "bk_cmdb",
        "action_ids": ["edit_biz_sensitive", "find_biz_sensitive"],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "biz_sensitive"},
    },
    {
        "system_id": "bk_itsm",
        "action_ids": [
            "project_view",
            "project_edit",
            "system_settings_manage",
            "service_create",
            "service_manage",
            "sla_manage",
            "workflow_create",
            "workflow_manage",
            "workflow_deploy",
            "flow_version_restore",
            "flow_version_manage",
            "flow_element_manage",
            "role_create",
            "role_manage",
            "ticket_view",
        ],
        "aggregate_resource_type": {"system_id": "bk_itsm", "id": "project"},
    },
    {
        "system_id": "bk_job",
        "action_ids": [
            "access_business",
            "quick_execute_script",
            "quick_transfer_file",
            "execute_script",
            "create_script",
            "view_script",
            "manage_script",
            "create_job_template",
            "view_job_template",
            "edit_job_template",
            "delete_job_template",
            "debug_job_template",
            "launch_job_plan",
            "create_job_plan",
            "view_job_plan",
            "edit_job_plan",
            "delete_job_plan",
            "sync_job_plan",
            "create_tag",
            "manage_tag",
            "create_cron",
            "manage_cron",
            "view_history",
            "notification_setting",
            "create_account",
            "manage_account",
        ],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "biz"},
    },
    {
        "system_id": "bk_log_search",
        "action_ids": [
            "view_business",
            "search_log",
            "create_indices",
            "manage_indices",
            "create_collection",
            "view_collection",
            "manage_collection",
            "create_es_source",
            "manage_es_source",
            "view_dashboard",
            "manage_dashboard",
            "manage_extract_config",
        ],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "biz"},
    },
    {
        "system_id": "bk_monitorv3",
        "action_ids": [
            "view_business",
            "view_home",
            "view_dashboard",
            "manage_dashboard",
            "view_host",
            "view_synthetic",
            "manage_synthetic",
            "view_event",
            "view_plugin",
            "manage_plugin",
            "view_collection",
            "manage_collection",
            "view_rule",
            "manage_rule",
            "view_notify_team",
            "manage_notify_team",
            "view_downtime",
            "manage_downtime",
            "view_custom_metric",
            "manage_custom_metric",
            "view_custom_event",
            "manage_custom_event",
            "export_config",
            "import_config",
            "view_service_category",
            "manage_upgrade",
            "view_function_switch",
            "manage_function_switch",
            "explore_metric",
            "manage_host",
        ],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "biz"},
    },
    {
        "system_id": "bk_sops",
        "action_ids": [
            "project_view",
            "project_edit",
            "project_fast_create_task",
            "flow_create",
            "flow_view",
            "flow_edit",
            "flow_delete",
            "flow_create_task",
            "flow_create_mini_app",
            "flow_create_periodic_task",
            "task_view",
            "task_operate",
            "task_edit",
            "task_claim",
            "task_delete",
            "task_clone",
            "mini_app_view",
            "mini_app_edit",
            "mini_app_delete",
            "mini_app_create_task",
            "periodic_task_view",
            "periodic_task_edit",
            "periodic_task_delete",
        ],
        "aggregate_resource_type": {"system_id": "bk_sops", "id": "project"},
    },
    {
        "system_id": "bk_sops",
        "action_ids": ["common_flow_delete", "common_flow_edit", "common_flow_view"],
        "aggregate_resource_type": {"system_id": "bk_sops", "id": "common_flow"},
    },
    {
        "system_id": "bk_ci",
        "action_ids": [
            "project_view",
            "project_edit",
            "project_delete",
            "project_manage",
            "pipeline_view",
            "pipeline_edit",
            "pipeline_create",
            "pipeline_download",
            "pipeline_delete",
            "pipeline_share",
            "pipeline_execute",
            "repertory_view",
            "repertory_edit",
            "repertory_create",
            "repertory_delete",
            "repertory_use",
            "credential_view",
            "credential_edit",
            "credential_create",
            "credential_delete",
            "credential_use",
            "cert_view",
            "cert_edit",
            "cert_create",
            "cert_delete",
            "cert_use",
            "environment_view",
            "environment_edit",
            "environment_create",
            "environment_delete",
            "environment_use",
            "env_node_view",
            "env_node_edit",
            "env_node_create",
            "env_node_delete",
            "env_node_use",
        ],
        "aggregate_resource_type": {"system_id": "bk_ci", "id": "project"},
    },
    {
        "system_id": "bk_nodeman",
        "action_ids": [
            "agent_view",
            "agent_operate",
            "proxy_operate",
            "plugin_view",
            "plugin_operate",
            "task_history_view",
        ],
        "aggregate_resource_type": {"system_id": "bk_cmdb", "id": "biz"},
    },
    {
        "system_id": "bk_nodeman",
        "action_ids": ["cloud_edit", "cloud_delete", "cloud_view"],
        "aggregate_resource_type": {"system_id": "bk_nodeman", "id": "cloud"},
    },
    {
        "system_id": "bk_nodeman",
        "action_ids": ["ap_delete", "ap_edit", "ap_view"],
        "aggregate_resource_type": {"system_id": "bk_nodeman", "id": "ap"},
    },
]

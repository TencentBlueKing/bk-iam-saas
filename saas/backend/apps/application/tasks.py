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
import logging
from typing import List

from celery import shared_task
from django.core.paginator import Paginator
from pydantic import parse_obj_as

from backend.biz.application import ApplicationBiz, ApplicationRenewPolicyInfoBean
from backend.service.constants import ApplicationStatus

from .models import Application

logger = logging.getLogger("celery")


@shared_task(ignore_result=True)
def check_or_update_application_status():
    """
    检查并更新申请单据状态
    由于对接第三方审批系统后，回调权限中心可能出现极小概率回调失败，所以需要周期任务检查补偿
    """
    # 查询未结束的申请单据
    # TODO: 是否需要过滤超过多久没处理才查询，但也有可能导致某些单据无法快速回调
    qs = Application.objects.filter(status=ApplicationStatus.PENDING.value)

    # 分页处理，避免调用ITSM查询超时问题
    paginator = Paginator(qs, 20)
    if not paginator.count:
        return

    biz = ApplicationBiz()
    for i in paginator.page_range:
        applications = list(paginator.page(i))

        # 查询ITSM可能出错，若出错，则记录日志，继续执行其他的
        try:
            id_status_dict = biz.query_application_approval_status(applications)
        except Exception:  # pylint: disable=broad-except
            logger.exception("check_or_update_application_status: query_application_approval_status fail")
            continue

        # 遍历每个申请单，进行审批处理
        for application in applications:
            try:
                status = id_status_dict.get(application.id)
                # 若查询不到，则忽略
                if status is None:
                    continue
                biz.handle_application_result(application, status)
            except Exception:  # pylint: disable=broad-except
                logger.exception(
                    "check_or_update_application_status: handle_application_result fail, application sn: %s",
                    application.sn,
                )


@shared_task(ignore_result=True)
def create_policies_renew_applications(data, username):
    """
    创建用户自定义权限续期申请

    由于用户可能一次renew很多个权限, 并且单个操作有很多的资源实例, 查询资源审批人可能会很慢, 需要异步处理
    """
    biz = ApplicationBiz()
    biz.create_for_renew_policy(
        parse_obj_as(List[ApplicationRenewPolicyInfoBean], data["policies"]), username, data["reason"]
    )

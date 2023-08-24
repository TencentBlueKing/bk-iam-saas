# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

主要处理申请的内容数据转为标准结构，给到ApplicationBiz
"""
from typing import Dict

from django.conf import settings
from django.utils.translation import gettext as _

from backend.apps.organization.models import User as UserModel
from backend.biz.application import ActionApplicationDataBean
from backend.biz.policy import PolicyBeanList, PolicyQueryBiz
from backend.common.error_codes import error_codes
from backend.service.constants import SubjectType
from backend.service.models import Applicant, Subject

from .policy import PolicyTrans


class ApplicationDataTrans:
    """用于将申请请求里的Dict转换为调用ApplicationBiz模块创建申请单所需的数据结构"""

    # 由于申请是更上层的业务逻辑，所以需要使用到策略的转换函数
    policy_trans = PolicyTrans()

    policy_query_biz = PolicyQueryBiz()

    def _gen_need_apply_policy_list(
        self, applicant: str, system_id: str, policy_list: PolicyBeanList
    ) -> PolicyBeanList:
        """生成需要申请的策略
        由于前端提交时会将已有权限的资源实例也提交，所以需要剔除掉
        """
        # 只对新增的策略进行申请，所以需要移除掉已有的权限
        # 1. 查询已有权限
        old_policy_list = self.policy_query_biz.new_policy_list(
            system_id,
            Subject.from_username(applicant),
        )

        # 2. 申请的策略里移除已有策略数据, 生成移除已有权限后的策略
        diff_policy_list = policy_list.sub(old_policy_list)

        # 3. 增量策略：校验新增的资源实例ID和Name是否匹配，检查逻辑不可放置于第4步后面，否则可能会出现将过期老策略进行校验
        diff_policy_list.check_resource_name()

        # 4. 检查每个操作新增的资源实例数量不超过限制
        # NOTE: 只需要检查新增的部分，已有的以及申请续期的都不需要检查
        self._check_application_policy_instance_count_limit(diff_policy_list)

        # 5. 由于存在申请时，未修改权限，只是修改有效期的情况，所以需要单独判断，重新添加到申请单里，同时申请的策略需要使用已有策略的有效期
        application_policies = []
        for p in policy_list.policies:
            old_policy = old_policy_list.get(p.action_id)
            # (1) 若老策略不存在，说明整条策略都是新增的
            # (2) 若老策略已过期，则说明是整条权限续期（也包括新增的资源实例）
            if old_policy is None or old_policy.is_expired():
                application_policies.append(p)
                continue

            # 增量申请的策略：新策略减去老策略里的资源实例后的策略
            diff_policy = diff_policy_list.get(p.action_id)
            # （3）没有增量策略，而从（1）（2）知道老策略也没有过期，说明用户没做任何改变，直接忽略
            if diff_policy is None:
                continue
            # （4）增量策略，由（1）（2）知道老的策略未过期，则申请时是不允许修改过期，所以还是调整为老策略的过期时间
            diff_policy.set_expired_at(old_policy.expired_at)
            application_policies.append(diff_policy)

        # 6. 数据完全没有变更
        if len(application_policies) == 0:
            raise error_codes.INVALID_ARGS.format(message=_("无新的权限申请，无需提交"), replace=True)

        return PolicyBeanList(system_id, application_policies)

    def _check_application_policy_instance_count_limit(self, policy_list: PolicyBeanList):
        """
        检查申请策略的资源实例限制
        """
        # 遍历每条策略，进行检查
        for policy in policy_list.policies:
            for c in policy.list_resource_type_instance_count():
                if c.count > settings.APPLY_POLICY_ADD_INSTANCES_LIMIT:
                    raise error_codes.VALIDATE_ERROR.format(
                        _("操作 [{}] 关联的资源类型 [{}] 单次申请限{}个实例，实例权限数过多不利于您后期维护，更多实例建议您申请范围权限。").format(
                            policy.action_id, c.type, settings.APPLY_POLICY_ADD_INSTANCES_LIMIT
                        )
                    )

    def from_grant_policy_application(self, applicant: str, data: Dict) -> ActionApplicationDataBean:
        """来着自定义权限申请的数据转换
        data来着 backend.apps.application.serializers.ApplicationSLZ
        {
            reason,
            system: {id}
            actions: [
                {
                    id,
                    type,
                    resource_groups: {
                        id,
                        related_resource_types: [
                            {
                                system_id,
                                type,
                                condition: [
                                    {
                                        id,
                                        instances: [
                                            {
                                                type,
                                                name,
                                                path: [
                                                    [
                                                        {system_id, type, type_name, id, name},
                                                        ...
                                                    ]
                                                ]
                                            }
                                        ]
                                        attributes: [
                                            {
                                                id,
                                                name,
                                                values: [
                                                    {id, name},
                                                    ...
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    policy_id,
                    expired_at
                }
            ],
            aggregations: [
                {
                    actions: [
                        {system_id, id},
                        ...
                    ]
                    aggregate_resource_type: {
                        system_id,
                        id,
                        instances: [
                            {id, name},
                            ...
                        ]
                    }
                    expired_at,
                }
            ]
        }
        """
        # data数据有两种，操作聚合的和非聚合的
        system_id = data["system"]["id"]

        # 1. 转换数据结构
        policy_list = self.policy_trans.from_aggregate_actions_and_actions(system_id, data)

        if "usernames" in data and data["usernames"]:
            application_policy_list = policy_list
            usernames = data["usernames"]

            if len(usernames) == 1:
                application_policy_list = self._gen_need_apply_policy_list(usernames[0], system_id, policy_list)

            application_policy_list.fill_empty_fields()
        else:
            # 2. 只对新增的策略进行申请，所以需要移除掉已有的权限
            application_policy_list = self._gen_need_apply_policy_list(applicant, system_id, policy_list)
            usernames = [applicant]

        # 3. 转换为ApplicationBiz创建申请单所需数据结构
        applicants = [
            Applicant(type=SubjectType.USER.value, id=u.username, display_name=u.display_name)
            for u in UserModel.objects.filter(username__in=usernames)
        ]

        application_data = ActionApplicationDataBean(
            applicant=applicant,
            policy_list=application_policy_list,
            applicants=applicants,
            reason=data["reason"],
        )

        return application_data

    def from_grant_temporary_policy_application(self, applicant: str, data: Dict) -> ActionApplicationDataBean:
        """来着临时权限申请的数据转换
        data来着 backend.apps.application.serializers.ApplicationSLZ
        """
        # data数据有两种，操作聚合的和非聚合的
        system_id = data["system"]["id"]

        # 1. 转换数据结构
        policy_list = self.policy_trans.from_aggregate_actions_and_actions(system_id, data)

        # 2. 校验每个操作用户已有的权限不能超过10条
        self._check_temporary_policy(applicant, system_id, policy_list)

        # 3. 检查每个操作新增的资源实例数量不超过限制
        self._check_application_policy_instance_count_limit(policy_list)

        if "usernames" in data and data["usernames"]:
            usernames = data["usernames"]
        else:
            usernames = [applicant]

        # 4. 转换为ApplicationBiz创建申请单所需数据结构
        applicants = [
            Applicant(type=SubjectType.USER.value, id=u.username, display_name=u.display_name)
            for u in UserModel.objects.filter(username__in=usernames)
        ]

        # 4. 转换为ApplicationBiz创建申请单所需数据结构
        application_data = ActionApplicationDataBean(
            applicant=applicant, policy_list=policy_list, applicants=applicants, reason=data["reason"]
        )

        return application_data

    def _check_temporary_policy(self, applicant: str, system_id: str, policy_list: PolicyBeanList) -> PolicyBeanList:
        """检查临时权限"""

        # NOTE: 临时权限的申请过期时间限制由前端处理

        # 1. 校验资源名称
        policy_list.check_resource_name()

        # 2. 获取某个系统的所有的临时权限, 包括过期的
        old_policies = self.policy_query_biz.list_temporary_by_subject(
            system_id,
            Subject.from_username(applicant),
        )

        for p in policy_list.policies:
            count = len([one for one in old_policies if one.action_id == p.action_id]) + 1
            if count > settings.TEMPORARY_POLICY_LIMIT:
                raise error_codes.VALIDATE_ERROR.format(
                    _("临时权限操作 [{}] 申请限最大{}条，临时权限过多不利于您后期维护，建议您删除部分权限再申请。").format(
                        p.action_id, settings.TEMPORARY_POLICY_LIMIT
                    )
                )

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
from bk_notice_sdk import config
from django.conf import settings
from django.urls import include, re_path
from django.views.decorators.cache import never_cache
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Monkey Patch: rest_framework.serializers.Serializer
import backend.util.serializer_patch  # noqa
from backend.common.views import login_exempt
from backend.common.vue import LoginSuccessView, VueTemplateView

schema_view = get_schema_view(
    openapi.Info(
        title="IAM_APP API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # backend apps re_path
    re_path(
        r"^api/v1/",
        include(
            [
                re_path(r"^version_log/", include("backend.version_log.urls")),
                re_path(r"^accounts/", include("backend.account.urls")),
                re_path(r"^systems/", include("backend.apps.system.urls")),
                re_path(r"^actions/", include("backend.apps.action.urls")),
                re_path(r"^policies/", include("backend.apps.policy.urls")),
                re_path(r"^applications/", include("backend.apps.application.urls")),  # 申请
                re_path(r"^resources/", include("backend.apps.resource.urls")),
                re_path(r"^approvals/", include("backend.apps.approval.urls")),
                re_path(r"^groups/", include("backend.apps.group.urls")),
                re_path(r"^subjects/", include("backend.apps.subject.urls")),
                re_path(r"^subject_templates/", include("backend.apps.subject_template.urls")),
                re_path(r"^templates/", include("backend.apps.template.urls")),
                re_path(r"^organizations/", include("backend.apps.organization.urls")),
                re_path(r"^open/", include("backend.api.urls_v1")),
                re_path(r"^roles/", include("backend.apps.role.urls")),
                re_path(r"^users/", include("backend.apps.user.urls")),
                re_path(r"^modeling/", include("backend.apps.model_builder.urls")),
                re_path(r"^audits/", include("backend.audit.urls")),
                re_path(r"^debug/", include("backend.debug.urls")),
                re_path(r"^handover/", include("backend.apps.handover.urls")),
                re_path(r"^mgmt/", include("backend.apps.mgmt.urls")),
                re_path(r"^temporary_policies/", include("backend.apps.temporary_policy.urls")),
                re_path(r"^iam/", include("backend.iam.urls")),
                # notice
                re_path(r"^{}".format(config.ENTRANCE_URL), include(("bk_notice_sdk.urls", "notice"), namespace="notice")),
            ]
        ),
    ),
    re_path(
        r"^api/v2/",
        include(
            [
                re_path(r"^open/", include("backend.api.urls_v2")),
            ]
        ),
    ),
    # healthz
    re_path("", include("backend.healthz.urls")),
    # prometheus
    re_path("", include("backend.metrics.urls")),
]

# add swagger api document
if settings.IS_LOCAL or settings.ENABLE_SWAGGER:
    urlpatterns += [
        re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    ]

# static file
urlpatterns += [
    re_path(r"^login_success/", never_cache(LoginSuccessView.as_view())),
    re_path(r"^.*$", never_cache(login_exempt(VueTemplateView.as_view()))),
]

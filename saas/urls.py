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
from django.conf import settings
from django.conf.urls import include, url
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
    # backend apps url
    url(
        r"^api/v1/",
        include(
            [
                url(r"^version_log/", include("backend.version_log.urls")),
                url(r"^accounts/", include("backend.account.urls")),
                url(r"^systems/", include("backend.apps.system.urls")),
                url(r"^actions/", include("backend.apps.action.urls")),
                url(r"^policies/", include("backend.apps.policy.urls")),
                url(r"^applications/", include("backend.apps.application.urls")),  # 申请
                url(r"^resources/", include("backend.apps.resource.urls")),
                url(r"^approvals/", include("backend.apps.approval.urls")),
                url(r"^groups/", include("backend.apps.group.urls")),
                url(r"^subjects/", include("backend.apps.subject.urls")),
                url(r"^templates/", include("backend.apps.template.urls")),
                url(r"^organizations/", include("backend.apps.organization.urls")),
                url(r"^open/", include("backend.api.urls_v1")),
                url(r"^roles/", include("backend.apps.role.urls")),
                url(r"^users/", include("backend.apps.user.urls")),
                url(r"^modeling/", include("backend.apps.model_builder.urls")),
                url(r"^audits/", include("backend.audit.urls")),
                url(r"^debug/", include("backend.debug.urls")),
                url(r"^handover/", include("backend.apps.handover.urls")),
                url(r"^mgmt/", include("backend.apps.mgmt.urls")),
                url(r"^temporary_policies/", include("backend.apps.temporary_policy.urls")),
                url(r"^iam/", include("backend.iam.urls")),
            ]
        ),
    ),
    url(
        r"^api/v2/",
        include(
            [
                url(r"^open/", include("backend.api.urls_v2")),
            ]
        ),
    ),
    # healthz
    url("", include("backend.healthz.urls")),
    # prometheus
    url("", include("backend.metrics.urls")),
]

# add swagger api document
if settings.IS_LOCAL:
    urlpatterns += [
        url(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    ]

# static file
urlpatterns += [
    url(r"^login_success/", never_cache(LoginSuccessView.as_view())),
    url(r"^.*$", never_cache(login_exempt(VueTemplateView.as_view()))),
]

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
from io import StringIO

import mock
import pytest
from django.core.management import call_command
from django_dynamic_fixture import G

from backend.apps.group.models import Group
from backend.apps.role.models import Role, RoleRelatedObject
from backend.apps.subject_template.models import SubjectTemplate
from backend.biz.group import GroupBiz
from backend.service.constants import RoleRelatedObjectType, RoleType

pytestmark = pytest.mark.django_db


@pytest.fixture()
def mock_update_subjects():
    with mock.patch("backend.service.group.iam.update_subjects") as mocked:
        yield mocked


class TestGroupBizUpdate:
    def test_sync_subject_template(self, mock_update_subjects):
        group = G(Group, name="old-name", description="old-desc")
        template = G(SubjectTemplate, name="old-name", description="old-desc", source_group_id=group.id)
        other_template = G(SubjectTemplate, name="other", description="other-desc", source_group_id=0)

        GroupBiz().update(group, "new-name", "new-desc", False, "admin")

        group.refresh_from_db()
        assert group.name == "new-name"
        assert group.description == "new-desc"

        template.refresh_from_db()
        assert template.name == "new-name"
        assert template.description == "new-desc"
        assert template.updater == "admin"

        other_template.refresh_from_db()
        assert other_template.name == "other"
        assert other_template.description == "other-desc"

        mock_update_subjects.assert_called_once_with([{"type": "group", "id": str(group.id), "name": "new-name"}])

    def test_without_subject_template(self, mock_update_subjects):
        group = G(Group, name="old-name", description="old-desc")

        GroupBiz().update(group, "new-name", "new-desc", False, "admin")

        group.refresh_from_db()
        assert group.name == "new-name"
        assert not SubjectTemplate.objects.filter(source_group_id=group.id).exists()


class TestUpdateSyncPermGroupByRole:
    def test_rename_sync_subject_template(self, mock_update_subjects):
        role = G(Role, type=RoleType.GRADE_MANAGER.value, sync_perm=True, description="role-desc")
        group = G(Group, name="old-name", description="old-desc")
        G(
            RoleRelatedObject,
            role_id=role.id,
            object_type=RoleRelatedObjectType.GROUP.value,
            object_id=group.id,
            sync_perm=True,
        )
        template = G(SubjectTemplate, name="old-name", description="old-desc", source_group_id=group.id)

        GroupBiz().update_sync_perm_group_by_role(role, "admin", group_name="new-name")

        group.refresh_from_db()
        assert group.name == "new-name"
        assert group.description == "role-desc"

        template.refresh_from_db()
        assert template.name == "new-name"
        assert template.description == "role-desc"

        mock_update_subjects.assert_called_once_with([{"type": "group", "id": str(group.id), "name": "new-name"}])


class TestSyncSubjectTemplateNameFromGroupCommand:
    def test_command(self):
        group = G(Group, name="new-name", description="new-desc")
        template = G(SubjectTemplate, name="old-name", description="old-desc", source_group_id=group.id)
        synced_group = G(Group, name="synced", description="synced-desc")
        synced_template = G(SubjectTemplate, name="synced", description="synced-desc", source_group_id=synced_group.id)
        another_group = G(Group, name="another-new", description="another-desc")
        another_template = G(SubjectTemplate, name="another-old", description="", source_group_id=another_group.id)

        out = StringIO()
        call_command("sync_subject_template_name_from_group", "--dry-run", stdout=out)
        template.refresh_from_db()
        assert template.name == "old-name"
        assert "2 subject templates need to be updated" in out.getvalue()

        out = StringIO()
        call_command("sync_subject_template_name_from_group", "--batch-size", "1", stdout=out)
        template.refresh_from_db()
        assert template.name == "new-name"
        assert template.description == "new-desc"

        another_template.refresh_from_db()
        assert another_template.name == "another-new"
        assert another_template.description == "another-desc"

        synced_template.refresh_from_db()
        assert synced_template.name == "synced"
        assert "2 subject templates need to be updated" in out.getvalue()

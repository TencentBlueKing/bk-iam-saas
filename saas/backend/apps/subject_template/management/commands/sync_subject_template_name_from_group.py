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
from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.apps.group.models import Group
from backend.apps.subject_template.models import SubjectTemplate


class Command(BaseCommand):
    help = "sync name and description of subject template from its source group"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="only print the templates to be updated")
        parser.add_argument("--batch-size", type=int, default=500, help="number of templates processed per batch")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        last_id = 0
        updated_count = 0
        while True:
            # 按主键游标分批, 避免大偏移量的 OFFSET 分页
            templates = list(
                SubjectTemplate.objects.filter(id__gt=last_id, source_group_id__gt=0)
                .order_by("id")
                .only("id", "name", "description", "source_group_id")[:batch_size]
            )
            if not templates:
                break
            last_id = templates[-1].id

            group_dict = {
                g["id"]: g
                for g in Group.objects.filter(id__in={t.source_group_id for t in templates}).values(
                    "id", "name", "description"
                )
            }

            now = timezone.now()
            changed_templates = []
            for template in templates:
                group = group_dict.get(template.source_group_id)
                if group is None:
                    continue

                if template.name == group["name"] and template.description == group["description"]:
                    continue

                self.stdout.write(
                    f"subject template {template.id}: name `{template.name}` -> `{group['name']}`, "
                    f"description `{template.description}` -> `{group['description']}`"
                )

                template.name = group["name"]
                template.description = group["description"]
                template.updated_time = now
                changed_templates.append(template)

            updated_count += len(changed_templates)
            if changed_templates and not dry_run:
                SubjectTemplate.objects.bulk_update(changed_templates, ["name", "description", "updated_time"])

        self.stdout.write(f"{'[dry-run] ' if dry_run else ''}{updated_count} subject templates need to be updated")

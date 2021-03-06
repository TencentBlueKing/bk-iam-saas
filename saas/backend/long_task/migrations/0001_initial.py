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
# Generated by Django 2.2.14 on 2021-01-04 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SubTaskState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.IntegerField(verbose_name='父亲任务id')),
                ('celery_id', models.CharField(max_length=36, verbose_name='celery任务id')),
                ('index', models.IntegerField(verbose_name='子任务索引')),
                ('status', models.IntegerField(choices=[(0, '未开始'), (1, '运行中'), (2, '成功'), (3, '失败'), (4, '取消')], default=1, verbose_name='任务状态')),
                ('exception', models.TextField(default='', verbose_name='任务异常')),
            ],
            options={
                'verbose_name': '子任务状态',
                'verbose_name_plural': '子任务状态',
                'ordering': ['index'],
            },
        ),
        migrations.CreateModel(
            name='TaskDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.CharField(max_length=64, verbose_name='创建者')),
                ('updater', models.CharField(max_length=64, verbose_name='更新者')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=32, verbose_name='任务类型')),
                ('_args', models.TextField(db_column='args', verbose_name='参数')),
                ('_params', models.TextField(db_column='params', default='', verbose_name='子任务参数集')),
                ('unique_sign', models.CharField(default='', max_length=64, verbose_name='任务唯一标识')),
                ('status', models.IntegerField(choices=[(0, '未开始'), (1, '运行中'), (2, '成功'), (3, '失败'), (4, '取消')], default=0, verbose_name='任务状态')),
                ('celery_id', models.CharField(default='', max_length=36, verbose_name='celery任务id')),
                ('_results', models.TextField(db_column='results', default='', verbose_name='结果集')),
            ],
            options={
                'verbose_name': '长时任务',
                'verbose_name_plural': '长时任务',
                'ordering': ['-id'],
            },
        ),
    ]

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
import os
import re
from typing import Dict, List

from django.conf import settings
from django.utils import translation

from backend.common.constants import DjangoLanguageEnum

from .constants import MD_FILE_NAME_PATTERN, MD_FILE_NAME_PATTERN_EN


def _is_filename_legal(filename: str) -> bool:
    """判断文件名是否存在/合法，"""
    re_pattern = MD_FILE_NAME_PATTERN
    # 根据语言选择文件
    if translation.get_language() == DjangoLanguageEnum.EN.value:
        re_pattern = MD_FILE_NAME_PATTERN_EN
    return False if re.match(re_pattern, filename) is None else True


def _read_file_content(file_path: str) -> str:
    """读取文件内容"""
    content = ""
    if os.path.isfile(file_path):
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    return content


def get_version_list() -> List[Dict[str, str]]:
    """
    获取md日志版本列表
    :return {版本号, 日期, 文件内容} 字段列表，列表根据版本号从大到小排列
    """
    file_dir = settings.VERSION_LOG_MD_FILES_DIR
    if not os.path.isdir(file_dir):  # md文件夹不存在
        return []
    version_list = []
    file_content_dict = {}
    for filename in os.listdir(file_dir):
        if _is_filename_legal(filename):
            version_date = os.path.splitext(filename)[0]
            version_date_list = version_date.split("_")
            version, date = version_date_list[0], version_date_list[1]
            version_list.append((version, date))
            # Note: 不要将文件内容与版本列表一起，因为版本列表需要排序，会影响效率
            # 读取文件内容
            file_content_dict[(version, date)] = _read_file_content(os.path.join(file_dir, filename))
    # 根据版本号按照从新版本到旧版本排序
    version_list.sort(key=lambda x: tuple(int(v) for v in x[0][1:].split(".")), reverse=True)

    return [
        {"version": version, "date": date, "content": file_content_dict[(version, date)]}
        for version, date in version_list
    ]

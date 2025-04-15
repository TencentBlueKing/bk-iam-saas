"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseEnvCondition(ABC):
    def __init__(self, system_id: str, values: List[Any]) -> None:
        self.system_id = system_id
        self.values = values

    @abstractmethod
    def trans(self) -> List[Dict[str, Any]]:
        pass


class WeekdayEnvCondition(BaseEnvCondition):
    def trans(self) -> List[Dict[str, Any]]:
        return [{"NumericEquals": {f"{self.system_id}._bk_iam_env_.weekday": [int(value) for value in self.values]}}]


class HMSEnvCondition(BaseEnvCondition):
    def trans(self) -> List[Dict[str, Any]]:
        return [
            {"NumericGte": {f"{self.system_id}._bk_iam_env_.hms": [self._time_str_to_int(self.values[0])]}},
            {"NumericLte": {f"{self.system_id}._bk_iam_env_.hms": [self._time_str_to_int(self.values[1])]}},
        ]

    def _time_str_to_int(self, time: str) -> int:
        hms = time.split(":")
        return int(hms[0]) * 10000 + int(hms[1]) * 100 + int(hms[2])


class TZEnvCondition(BaseEnvCondition):
    def trans(self) -> List[Dict[str, Any]]:
        return [{"StringEquals": {f"{self.system_id}._bk_iam_env_.tz": self.values}}]

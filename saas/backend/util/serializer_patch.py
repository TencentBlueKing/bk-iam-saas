# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

方便输出错误message
"""

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer


def _is_valid(self, raise_exception=False):
    # This implementation is the same as the default,
    # except that we use lists, rather than dicts, as the empty case.
    assert hasattr(self, "initial_data"), (
        "Cannot call `.is_valid()` as no `data=` keyword argument was "
        "passed when instantiating the serializer instance."
    )

    if not hasattr(self, "_validated_data"):
        try:
            self._validated_data = self.run_validation(self.initial_data)
        except ValidationError as exc:
            self._validated_data = []
            self._errors = exc.detail
        else:
            self._errors = []

    if self._errors and raise_exception:
        error = ValidationError(self.errors)
        error.serializer = self
        raise error

    return not bool(self._errors)


Serializer.is_valid = _is_valid

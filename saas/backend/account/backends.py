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
import traceback

from blue_krill.web.std_error import APIError
from django.contrib.auth.backends import ModelBackend
from django.db import IntegrityError
from rest_framework import status

from backend.account import get_user_model
from backend.component import login

logger = logging.getLogger("app")

ROLE_TYPE_ADMIN = "1"


class PermissionForbidden(Exception):
    def __init__(self, message):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.code = 1302403
        self.message = message


class TokenBackend(ModelBackend):
    def authenticate(self, request=None, bk_token=None):
        logger.debug("Enter in TokenBackend")
        # 判断是否传入验证所需的bk_token,没传入则返回None
        if not bk_token:
            return None

        verify_result, username = self.verify_bk_token(bk_token)
        # 判断bk_token是否验证通过,不通过则返回None
        if not verify_result:
            return None

        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(username=username)
            get_user_info_result, user_info = self.get_user_info(bk_token)
            # 判断是否获取到用户信息,获取不到则返回None
            if not get_user_info_result:
                return None
            # user.set_property(key="qq", value=user_info.get("qq", ""))
            user.set_property(key="language", value=user_info.get("language", ""))
            user.set_property(key="time_zone", value=user_info.get("time_zone", ""))
            user.set_property(key="role", value=user_info.get("role", ""))
            # user.set_property(key="phone", value=user_info.get("phone", ""))
            # user.set_property(key="email", value=user_info.get("email", ""))
            # user.set_property(key="wx_userid", value=user_info.get("wx_userid", ""))
            # user.set_property(key="chname", value=user_info.get("chname", ""))

            # 用户如果不是管理员，则需要判断是否存在平台权限，如果有则需要加上
            if not user.is_superuser and not user.is_staff:
                role = user_info.get("role", "")
                is_admin = True if str(role) == ROLE_TYPE_ADMIN else False
                user.is_superuser = is_admin
                user.is_staff = is_admin
                user.save()
            return user

        except PermissionForbidden as e:
            raise e
        except IntegrityError:
            logger.exception(traceback.format_exc())
            logger.exception("get_or_create UserModel fail or update_or_create UserProperty")
            return None
        except Exception:  # pylint: disable=broad-except
            logger.exception(traceback.format_exc())
            logger.exception("Auto create & update UserModel fail")
            return None

    def get_user_info(self, bk_token):
        """
        请求平台ESB接口获取用户信息
        @param bk_token: bk_token
        @type bk_token: str
        @return:True, {
            u'message': u'\u7528\u6237\u4fe1\u606f\u83b7\u53d6\u6210\u529f',
            u'code': 0,
            u'data': {
                u'qq': u'',
                u'wx_userid': u'',
                u'language': u'zh-cn',
                u'username': u'test',
                u'time_zone': u'Asia/Shanghai',
                u'role': 2,
                u'phone': u'11111111111',
                u'email': u'test',
                u'chname': u'test'
            },
            u'result': True,
            u'request_id': u'eac0fee52ba24a47a335fd3fef75c099'
        }
        @rtype: bool,dict
        """
        try:
            data = login.get_user_info(bk_token)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Abnormal error in get_user_info...:%s" % e)
            self._handle_exception(e)
            return False, {}

        user_info = {}
        # v1,v2字段相同的部分
        user_info["wx_userid"] = data.get("wx_userid", "")
        user_info["language"] = data.get("language", "")
        user_info["time_zone"] = data.get("time_zone", "")
        user_info["phone"] = data.get("phone", "")
        user_info["chname"] = data.get("chname", "")
        user_info["email"] = data.get("email", "")
        user_info["qq"] = data.get("qq", "")
        user_info["username"] = data.get("bk_username", "")
        user_info["role"] = data.get("bk_role", "")
        return True, user_info

    def verify_bk_token(self, bk_token):
        """
        请求VERIFY_URL,认证bk_token是否正确
        @param bk_token: "_FrcQiMNevOD05f8AY0tCynWmubZbWz86HslzmOqnhk"
        @type bk_token: str
        @return: False,None True,username
        @rtype: bool,None/str
        """
        try:
            data = login.verify_bk_token(bk_token)
        except Exception as e:  # pylint: disable=broad-except
            logger.warn("Abnormal error in verify_bk_token...", exc_info=True)
            self._handle_exception(e)
            return False, None

        return True, data["bk_username"]

    def _handle_exception(self, e):
        """处理登录特殊异常, 需要前端响应给用户"""
        if isinstance(e, APIError) and "1302403" in e.message:
            msg_prefix = "message="
            idx = e.message.rfind(msg_prefix)
            message = e.message[idx + len(msg_prefix) : -1]

            raise PermissionForbidden(message)

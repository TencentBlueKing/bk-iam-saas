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

# Create your views here.
from typing import Dict, List, Tuple

from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.apps.model_builder.constants import GenerateJsonTypeEnum, ModelSectionEnum, ModelSectionTypeList
from backend.apps.model_builder.models import MockSystemModel
from backend.apps.model_builder.permissions import ModelOwnerPermission
from backend.apps.model_builder.serializers import (
    ActionGroupSLZ,
    ActionSLZ,
    CommonActionSLZ,
    DeletePartSLZ,
    GenerateJsonSLZ,
    InstanceSelectionListSLZ,
    InstanceSelectionSLZ,
    ModelDataIDExistsSLZ,
    ModelIDExistsResponseSLZ,
    ModelIdSLZ,
    ModelSLZ,
    ModelSystemIDExistsSLZ,
    ModelSystemSLZ,
    ModelUpdateSLZ,
    ResourceTypeListSLZ,
    ResourceTypeSLZ,
    RetrievePartSLZ,
)
from backend.apps.model_builder.validators import (
    validate_action,
    validate_actions_groups,
    validate_common_actions,
    validate_delete_part,
    validate_instance_selection,
    validate_system,
)
from backend.biz.instance_selection import InstanceSelectionBiz
from backend.biz.system import SystemBiz
from backend.common.error_codes import error_codes
from backend.service.instance_selection import InstanceSelectionService
from backend.service.models.resource_type import ResourceTypeDict
from backend.service.resource_type import ResourceTypeService


class UserMockSystemModelViewSet(GenericViewSet, mixins.ListModelMixin):
    translate_exempt = True

    serializer_class = ModelSLZ

    def get_queryset(self):
        request = self.request
        return MockSystemModel.objects.filter(owner=request.user.username)

    @swagger_auto_schema(
        operation_description="创建一个模型系统",
        request_body=ModelSystemSLZ(label="模型系统"),
        responses={status.HTTP_200_OK: ModelIdSLZ(label="模型ID")},
        tags=["model_builder"],
    )
    def create(self, request, *args, **kwargs):
        serializer = ModelSystemSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        body = serializer.data

        if MockSystemModel.objects.filter(system_id=body["id"]).exists():
            raise error_codes.VALIDATE_ERROR.format(_("唯一ID已存在"))

        model = MockSystemModel.objects.create(
            system_id=body["id"],
            owner=request.user.username,
            creator=request.user.username,
        )

        model.add_or_update_section(ModelSectionEnum.SYSTEM.value, body)
        model.save()

        return Response({"id": model.id})

    @swagger_auto_schema(
        operation_description="获取用户页面接入构建模型",
        responses={status.HTTP_200_OK: ModelSLZ(label="模型", many=True)},
        tags=["model_builder"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class MockSystemModelViewSet(GenericViewSet):
    translate_exempt = True

    permission_classes = [ModelOwnerPermission]

    lookup_field = "id"
    queryset = MockSystemModel.objects.all()

    @swagger_auto_schema(
        operation_description="获取用户页面接入构建模型",
        query_serializer=RetrievePartSLZ(label="查询类型, 不设置返回全部, 设置key返回对应数据"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["model_builder"],
    )
    # TODO 优化代码, 圈复杂度23, 超过规范20
    def retrieve(self, request, *args, **kwargs):
        model = MockSystemModel.objects.get(id=kwargs["id"])
        mock_system_id = model.data["system"]["id"]
        mock_system_name = model.data["system"]["name"]

        slz = RetrievePartSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        section = slz.data.get("type")
        data = model.data.get(section) if section else model.data

        if not data:
            return Response(data)

        # NOTE: 1 fill resource_type_chain[resource_type=> system_name/name]
        # [{
        #     "id": "app_view",
        #     "name": "test",
        #     "resource_type_chain": [{"system_id": "abc", "id": "app"}]
        # }]
        if section == ModelSectionEnum.INSTANCE_SELECTION.value:
            system_dict = dict(_list_all_systems(mock_system_id, mock_system_name))
            system_ids = [rt["system_id"] for d in data for rt in d.get("resource_type_chain", [])]
            resource_type_dict = {
                system_id: {d["id"]: d["name"] for d in _list_all_resource_types(model, system_id, mock_system_id)}
                for system_id in system_ids
            }

            for d in data:
                for rt in d.get("resource_type_chain", []):
                    rt_system_id = rt["system_id"]
                    rt["system_name"] = system_dict.get(rt_system_id, rt_system_id)
                    rt["name"] = resource_type_dict.get(rt_system_id, {}).get(rt["id"], rt["id"])
        # NOTE: 2 fill action resource_type and instance_selections
        # [
        #     {
        #       "id": "develop_app",
        #       "related_resource_types": [
        #         {
        #           "system_id": "abc",   # system_name
        #           "id": "app",          # name
        #           "related_instance_selections": [
        #             {
        #               "system_id": "abc",    # system_name
        #               "id": "app_view",      # name
        #               "ignore_iam_path": false
        #             }
        #           ]
        #         }
        #       ]
        #     }
        # ]
        elif section == ModelSectionEnum.ACTION.value:
            system_dict = dict(_list_all_systems(mock_system_id, mock_system_name))

            rt_system_ids = [rt["system_id"] for d in data for rt in d.get("related_resource_types", [])]
            resource_type_dict = {
                system_id: {d["id"]: d["name"] for d in _list_all_resource_types(model, system_id, mock_system_id)}
                for system_id in rt_system_ids
            }
            ins_system_ids = [
                ins["system_id"]
                for d in data
                for rt in d.get("related_resource_types", [])
                for ins in rt.get("related_instance_selections", [])
            ]
            instance_selection_dict = {
                system_id: {
                    d["id"]: d["name"] for d in _list_all_instance_selections(model, system_id, mock_system_id)
                }
                for system_id in ins_system_ids
            }

            for d in data:
                for rt in d.get("related_resource_types", []):
                    rt_system_id = rt["system_id"]
                    rt["system_name"] = system_dict.get(rt_system_id, rt_system_id)
                    rt["name"] = resource_type_dict.get(rt_system_id, {}).get(rt["id"])

                    for ris in rt.get("related_instance_selections", []):
                        ris_system_id = ris["system_id"]
                        ris["system_name"] = system_dict.get(ris_system_id, ris_system_id)
                        ris["name"] = instance_selection_dict.get(ris_system_id, {}).get(ris["id"], ris["id"])

        return Response(data)

    @swagger_auto_schema(
        operation_description="根据 ID 删除模型中的部分数据",
        request_body=DeletePartSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["model_builder"],
    )
    def delete_part(self, request, *args, **kwargs):
        slz = DeletePartSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        body = slz.data

        _type = body["type"]
        if _type == ModelSectionEnum.SYSTEM.value:
            raise error_codes.VALIDATE_ERROR.format(_("系统不能被删除"))

        # 需要检查引用, 被引用不能删除
        validate_delete_part(kwargs["id"], _type, body.get("id"))

        model = MockSystemModel.objects.get(id=kwargs["id"])
        model.delete_from_section(_type, body.get("id"))
        model.save()

        return Response()

    @swagger_auto_schema(
        operation_description="根据 ID 更新模型中的部分数据",
        request_body=ModelUpdateSLZ(label="更新模型"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["model_builder"],
    )
    def update_part(self, request, *args, **kwargs):
        serializer = ModelUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        body = serializer.data

        # _type: (slz_class, many=False|True)
        type_slzs = {
            ModelSectionEnum.SYSTEM.value: (ModelSystemSLZ, False),
            # 以下三个支持单个新增/删除, 因为有 ID
            # TODO 遗留问题: => 如果 ID 重复, 会更新掉? 前端需要校验?
            ModelSectionEnum.RESOURCE_TYPE.value: (ResourceTypeSLZ, False),
            ModelSectionEnum.INSTANCE_SELECTION.value: (InstanceSelectionSLZ, False),
            ModelSectionEnum.ACTION.value: (ActionSLZ, False),
            # 以下两个, 只能整体地增删
            ModelSectionEnum.ACTION_GROUPS.value: (ActionGroupSLZ, True),
            ModelSectionEnum.COMMON_ACTIONS.value: (CommonActionSLZ, True),
        }

        _type = body["type"]
        if _type not in type_slzs:
            raise error_codes.VALIDATE_ERROR.format(_("暂时不支持这种type"))

        slz_class, many = type_slzs[_type]
        ds = slz_class(data=body["data"], many=many)
        ds.is_valid(raise_exception=True)

        # custom validations
        type_validate_funcs = {
            ModelSectionEnum.SYSTEM.value: validate_system,
            ModelSectionEnum.ACTION_GROUPS.value: validate_actions_groups,
            ModelSectionEnum.COMMON_ACTIONS.value: validate_common_actions,
            ModelSectionEnum.INSTANCE_SELECTION.value: validate_instance_selection,
            ModelSectionEnum.ACTION.value: validate_action,
        }
        validate_func = type_validate_funcs.get(_type)
        if validate_func is not None:
            validate_func(kwargs["id"], ds.data)

        # do save
        model = MockSystemModel.objects.get(id=kwargs["id"])
        model.add_or_update_section(_type, ds.data)
        model.save()

        return Response()


def _list_all_systems(mock_system_id: str, mock_system_name: str) -> List[Tuple[str, str]]:
    data = [(mock_system_id, mock_system_name)]

    biz = SystemBiz()
    systems = biz.list()
    for s in systems:
        if s.id != mock_system_id:
            data.append((s.id, s.name))

    return data


class SystemListView(GenericViewSet):
    """
    [API] 拉取外部的系统列表 + 本系统列表  (my_system + list_systems)
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    permission_classes = [ModelOwnerPermission]

    @swagger_auto_schema(
        operation_description="构建模型时拉取所有系统列表",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["model_builder"],
    )
    def list_system(self, request, *args, **kwargs):
        model = MockSystemModel.objects.get(id=kwargs["id"])
        mock_system_id = model.data["system"]["id"]
        mock_system_name = model.data["system"]["name"]

        data = _list_all_systems(mock_system_id, mock_system_name)

        return Response(data)


def _list_all_resource_types(model: MockSystemModel, system_id: str, mock_system_id: str) -> List[Dict]:
    if system_id == mock_system_id:
        if not model.data.get(ModelSectionEnum.RESOURCE_TYPE.value):
            return []
        data = model.data[ModelSectionEnum.RESOURCE_TYPE.value]
    else:
        svc = ResourceTypeService()
        rtsd = svc.get_system_resource_type_list_map([system_id])
        rts = rtsd.get(system_id, [])
        data = [rt.dict() for rt in rts]

    return data


class ResourceTypeListView(GenericViewSet):
    """
    [API] 拉去某个系统的 资源类型列表 (my_system or external_system)
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    permission_classes = [ModelOwnerPermission]

    svc = ResourceTypeService()

    @swagger_auto_schema(
        operation_description="构建模型时拉取某个系统的资源列表",
        query_serializer=ResourceTypeListSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["model_builder"],
    )
    def list_resource_type(self, request, *args, **kwargs):
        model = MockSystemModel.objects.get(id=kwargs["id"])
        mock_system_id = model.data["system"]["id"]

        slz = ResourceTypeListSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.data["system_id"]
        data = _list_all_resource_types(model, system_id, mock_system_id)

        return Response(data)


def _list_all_instance_selections(
    model: MockSystemModel, system_id: str, mock_system_id: str, raw: bool = False
) -> List[Dict]:
    if system_id == mock_system_id:
        if not model.data.get(ModelSectionEnum.INSTANCE_SELECTION.value):
            return []

        data = model.data[ModelSectionEnum.INSTANCE_SELECTION.value]
    else:
        svc = InstanceSelectionService()
        instance_selections = svc.list_raw_by_system(system_id)
        data = [d.dict() for d in instance_selections] if instance_selections else []

    if raw:
        return data

    # put the default resource_type_dict
    resource_types = model.data.get(ModelSectionEnum.RESOURCE_TYPE.value)
    resource_type_dict = {}
    if resource_types:
        resource_type_dict = {(mock_system_id, i["id"]): i for i in resource_types}

    mock_system_name = model.data["system"]["name"]
    system_dict = dict(_list_all_systems(mock_system_id, mock_system_name))

    # 查询涉及到的系统
    system_ids = [
        j["system_id"] for i in data for j in i.get("resource_type_chain", []) if j["system_id"] != mock_system_id
    ]
    # 查询资源类型
    if system_ids:
        ext_resource_type_dict = ResourceTypeService().get_system_resource_type_dict(system_ids)
        resource_type_dict.update(ext_resource_type_dict.data)

    resource_type_name_provider = ResourceTypeDict(data=resource_type_dict)

    for d in data:
        if d.get("resource_type_chain"):
            chain = d["resource_type_chain"]
            for rt in chain:
                name, name_en = resource_type_name_provider.get_name(rt["system_id"], rt["id"])
                rt["name"], rt["name_en"] = name, name_en
                rt["system_name"] = system_dict.get(rt["system_id"], rt["system_id"])
    return data


class InstanceSelectionListView(GenericViewSet):
    """
    [API] 拉取外部的系统列表 + 本系统列表  (my_system + list_systems)
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    permission_classes = [ModelOwnerPermission]

    biz = InstanceSelectionBiz()

    @swagger_auto_schema(
        operation_description="构建模型时拉取某个系统的实例视图列表",
        query_serializer=InstanceSelectionListSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["model_builder"],
    )
    def list_instance_selection(self, request, *args, **kwargs):
        model = MockSystemModel.objects.get(id=kwargs["id"])
        mock_system_id = model.data["system"]["id"]

        slz = InstanceSelectionListSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.data["system_id"]
        data = _list_all_instance_selections(model, system_id, mock_system_id)

        return Response(data)


class GenerateJsonView(GenericViewSet):
    """
    [API] 生成json 1. 多个注册json 2. migration json   type=[api|migrate]
    """

    translate_exempt = True
    permission_classes = [ModelOwnerPermission]

    @swagger_auto_schema(
        operation_description="生成json",
        request_body=GenerateJsonSLZ(label="类型"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["model_builder"],
    )
    def generate_json(self, request, *args, **kwargs):
        model = MockSystemModel.objects.get(id=kwargs["id"])

        slz = GenerateJsonSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        _type = slz.data["type"]
        if _type == GenerateJsonTypeEnum.API.value:
            data = model.data_to_preview_json()
        else:
            data = model.data_to_migrate_json()

        return Response(data)


class ModelDataIdExistsViewSet(GenericViewSet):
    """
    [API] 检查模型中的某种资源的id是否已存在
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="检查模型中的某种资源的id是否已存在(当前只支持resource_type/instance_selection/action",
        query_serializer=ModelDataIDExistsSLZ(label="检查id是否占用"),
        responses={status.HTTP_200_OK: ModelIDExistsResponseSLZ(label="是否存在")},
        tags=["model_builder"],
    )
    def exists(self, request, *args, **kwargs):
        model = MockSystemModel.objects.get(id=kwargs["id"])

        slz = ModelDataIDExistsSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        data = slz.data

        _type = data["type"]
        _id = data["id"]

        if _type not in ModelSectionTypeList:
            raise error_codes.VALIDATE_ERROR.format(_("当前只支持resource_type/instance_selection/action"))

        exists_and_message = model.ids_exists_in_section(_type, [_id])

        return Response({"exists": exists_and_message[0]})


class IdExistsViewSet(GenericViewSet):
    """
    [API] 检查这个人的system_id是否已经存在(当前 system_id + owner唯一)
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="判断某个id是否已经存在(当前 system_id+owner唯一)",
        query_serializer=ModelSystemIDExistsSLZ(label="检查id是否占用"),
        responses={status.HTTP_200_OK: ModelIDExistsResponseSLZ(label="是否存在")},
        tags=["model_builder"],
    )
    def exists(self, request, *args, **kwargs):
        slz = ModelSystemIDExistsSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        _id = slz.data["id"]

        if MockSystemModel.objects.filter(system_id=_id, owner=request.user.username).exists():
            return Response({"exists": True})

        return Response({"exists": False})

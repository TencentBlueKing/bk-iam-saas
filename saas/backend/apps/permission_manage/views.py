from rest_framework.viewsets import GenericViewSet
from backend.apps.permission_manage.serializer import PermissionManageSLZ
from rest_framework.response import Response
from backend.biz.permission_manage import list_subject_by_custom, list_subject_by_template, list_subject_with_resource


class PremissoinManageViewSet(GenericViewSet):

    def list(self, request, *args, **kwargs):
        serializer = PermissionManageSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        system_id = data["system_id"]
        action_id = data["action_id"]
        limit = data["limit"]
        resource_info = data["resource_info"]
        permission_type = data["permission_type"]

        if permission_type == "template":
            if resource_info:
                results = list_subject_with_resource(system_id, action_id, resource_info, limit)
                return Response(results)

            results = list_subject_by_template(system_id=system_id, action_id=action_id, limit=limit)
            return Response(results)

        if permission_type == "custom":
            if resource_info:
                results = list_subject_with_resource(system_id, action_id, resource_info, limit=limit)
                return Response(results)

            results = list_subject_by_custom(system_id=system_id, action_id=action_id, limit=limit)
            return Response(results)

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from backend.apps.permission_manage.serializer import PermissionManageSLZ
from backend.biz.permission_resource_subjects import PermissionResourceSubjects


class PermissionResourceSubjectsViewSet(GenericViewSet):
    max_limit = 1000

    def list(self, request, *args, **kwargs):
        serializer = PermissionManageSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        subjects = PermissionResourceSubjects(data).query_subjects_by_resource()
        return Response(subjects)

    def export(self, request):
        """
        TODO 使用openpyxl实现导出excel(参考用户管理的导出方法)
        """
        from openpyxl.workbook.workbook import Workbook
        from openpyxl.styles import Alignment, Font, colors
        from backend.component.iam import get_system
        from backend.component.iam import get_action
        serializer = PermissionManageSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # 查询导出数据
        per = PermissionResourceSubjects(data)
        system_name = get_system(per.system_id)['system_name']
        action_name = get_action(per.system_id, per.action_id)['action_name']
        resource_instance_name = per.resource_instance['name']  # 资源示例名称不太好拿，从前端取
        subjects = per.query_subjects_by_resource()
        # 导出excel TODO 待实现
        sheet = Workbook().worksheets[0]
        sheet.alignment = Alignment(wrapText=True)
        # excel返回列包含：系统名，操作名，实例名(有则返回), 成员名称
        # 后面待补充

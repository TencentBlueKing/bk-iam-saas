import pytest
from werkzeug.local import Local, release_local
from celery import shared_task

from backend.common.local import celery_local, get_local
from backend.common.debug import stack


@pytest.mark.django_db
class TestLocalContextIsolation:
    test_chain_data = [{"data1": "value1"}, {"data2": "value2"}]
    key = "debug_stack"

    def test_celery_local_context_isolation(self):
        """测试在Celery任务上下文，异步任务中调用api的情况"""
        local = celery_local
        setattr(local, self.key, self.test_chain_data)
        storage = local._get_storage()
        assert storage.get(self.key) == self.test_chain_data
        local.__release_local__()
        assert hasattr(local, "debug_stack") is False

    def test_web_api_context_isolation(self):
        """测试Web API上下文隔离"""
        local_api = Local()
        setattr(local_api, self.key, self.test_chain_data)
        print(local_api)
        storage = getattr(local_api, self.key)
        assert storage == self.test_chain_data
        release_local(local_api)
        print("local: ", local_api)
        assert hasattr(local_api, "debug_stack") is False

    def test_celery_task_api_call_context_isolation(self):
        """测试Celery任务中API调用的上下文隔离"""
        
        @shared_task
        def mock_celery_task():
            # 模拟在Celery任务中调用API
            local = get_local()
            
            # 添加调试信息
            stack.push({
                "type": "TASK_API_CALL",
                "task_id": mock_celery_task.request.id,
                "data": "test_data"
            })
            
            # 验证数据被正确存储在当前任务的上下文中
            if hasattr(local, '_get_storage'):
                storage = local._get_storage()
                assert "debug_stack" in storage
                
            # 获取并验证调试数据
            debug_data = stack.pop_all()
            assert len(debug_data) == 1
            assert debug_data[0]["type"] == "TASK_API_CALL"
            assert debug_data[0]["task_id"] == mock_celery_task.request.id
            
            return debug_data
        
        # 直接调用任务函数进行测试（模拟Celery任务执行环境）
        result = mock_celery_task()
        assert len(result) == 1
        assert result[0]["type"] == "TASK_API_CALL"
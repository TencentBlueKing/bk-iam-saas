import threading

# 线程局部存储用于请求上下文
_thread_local = threading.local()


def get_current_request():
    """获取当前请求对象"""
    return getattr(_thread_local, "request", None)


def get_current_tenant_id():
    """获取当前请求的租户ID"""
    request = get_current_request()
    if request and hasattr(request, "tenant_id"):
        return request.tenant_id
    # 如果没有请求上下文，返回空字符串（全租户）
    return ""


def set_current_request(request):
    """设置当前请求对象（由中间件调用）"""
    _thread_local.request = request


def clear_current_request():
    """清理当前请求对象（由中间件调用）"""
    if hasattr(_thread_local, "request"):
        delattr(_thread_local, "request")

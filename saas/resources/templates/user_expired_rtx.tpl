{% if policies %}
*自定义权限({{ policies|length }})*
{% endif %}
{% for policy in policies %}
系统: {{ policy.system.name }}, 操作: {{ policy.action.name }}, 资源实例: {{ policy.gen_resource_summary }}, 到期时间: {{ policy.expired_display }}
{% endfor %}

---

{% groups %}
*用户组权限({{ groups|length }})*
{% endif %}
{% for group in groups %}
用户组: {{ group.name }}, 管理空间: {{ group.get_role_name }}, 描述: {{ group.description }}, 过期时间: {{ group.expired_at_display }}
{% endfor %}

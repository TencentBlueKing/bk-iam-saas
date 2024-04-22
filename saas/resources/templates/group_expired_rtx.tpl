{% for group in groups %}
管理空间: {{ role.name }}, 用户组: {{ group.name }}, 过期成员: {{ group.subject_name }}, 到期时间: {{ group.expired_at_display }}
{% endfor %}

---

<span style="color: gray;">你收到此提醒, 是因为你是【{{ roe.name }}】的管理员</span>

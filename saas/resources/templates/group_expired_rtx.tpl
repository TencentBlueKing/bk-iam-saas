{% for group in groups %}
管理空间: **{{ role.name }}**, 用户组: **{{ group.name }}**, 过期成员: **{{ group.subject_name }}**, 到期时间: **{{ group.expired_at_display }}**
{% endfor %}

你收到此提醒, 是因为你是【{{ role.name }}】{% if role.type != "super_manager" %}{{ role.get_type_display }}{% endif %}

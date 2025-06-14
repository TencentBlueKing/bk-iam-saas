<!-- 2025-05-28 -->
# V1.10.44 版本更新日志

### 缺陷修复
* 修复登录认证在角色身份认证之后执行导致当角色身份会话泄露时可能存在安全问题

---

<!-- 2025-05-15 -->
# V1.10.43 版本更新日志

### 新增功能
* 支持 MySQL/Redis/RabbitMQ 等组件的 TLS 加密连接配置
* 权限模板编辑用户组模块交互整改 (处理旧版无法全量提交用户组问题)
* 全平台属性条件搜索增加防抖搜索 (处理组件库 searchLoading 持续触发)
* 区分系统管理员和其他类型管理员展示形式

---

<!-- 2025-04-17 -->
# V1.10.42 版本更新日志

### 功能优化
* 兼容网关低版本不支持 openapi 3.0 协议的资源配置

---

<!-- 2025-04-10 -->
# V1.10.41 版本更新日志

### 缺陷修复
* 修复 dbm 自定义权限审理流转异常

---

<!-- 2025-04-01 -->
# V1.10.40 版本更新日志

### 新增功能
* 新增文档链接环境变量 BK_CE_URL
* 新增单个 action 属性授权 OpenAPI
* 新增用户组批量续期 OpenAPI
* 新增权限模板相关 OpenAPI

### 功能优化
* 平台管理和管理空间资源权限管理共用一套业务
* 管理空间导航栏下侧边栏整改
* 所有需要验证管理员身份的页面链接添加管理员身份进行快速检索定位

### 缺陷修复
* 修复离职用户 SaaS 部分表数据未清理
* 修复由于 bulk_create 不能触发 signal，导致的审计日志缺失
* 修复审批流程管理 —> 加入用户组审批流程 select 框样式异常

---

<!-- 2025-02-13 -->
# V1.10.39 版本更新日志

### 新增功能
* 蓝盾内嵌页面续期添加事件通信
* 申请加入用户组时，二级资源拥有者离职，上升到一级管理员审批
* 二级管理空间支持编辑人员、资源实例授权范围
* 二级管理空间克隆、编辑增加主操作自动关联操作实例
* 切换管理员身份重定向的页面增加授权边界和二级管理空间
* 授权边界增加理由字段
* 管理空间角色选择器二级管理空间增加分页
* Open API 成员列表接口支持获取成员加入用户组的时间
* 增加蓝盾侧业务场景是扩大授权人员边界范围则不需要调用接口校验授权范围
* 蓝盾侧增加通过环境变量注入限制勾选组织架构业务
* 添加需要自定义添加授权人员边界样式的页面

### 功能优化
* 蓝盾侧需求协调参数归一化
* 优化二级管理空间菜单
* 二级管理空间兼容公共组件下权限模板业务

### 缺陷修复
* 修复主操作存在关联操作且接口响应数据为空时，表格关联操作数据会被置空
* 处理只有自定义属性无资源实例的授权范围时提示 undefined 问题
* 修复细粒度权限申请个别样式错乱问题
* 修复分级管理员在授权边界编辑页切换二级管理员身份需要重定向到用户组页面
* 去掉管理空间编辑权限模板
* 修复二级管理空间编辑实力资源偶现实例已选 disabled
* 处理聚合场景下主操作是否跟关联操作的资源授权范围是否一致
* 修复管理员身份的资源实例表格模块偶现表格样式错乱问题
* 修复用户加入用户组的有效期相差 8 小时问题

---

<!-- 2024-11-12 -->
# V1.10.38 版本更新日志

### 功能优化
* 管理空间人员选择器编辑组件支持默认为空 (该管理员已离职) 后可重新编辑场景

---

<!-- 2024-11-07 -->
# V1.10.37 版本更新日志

### 缺陷修复
* 修复用户组无资源实例和属性条件时预览差异对比报错
* 只有用户组模块且该用户组存在才能预览资源实例差异对比
* 修复 child_type 取值错误导致无法展开非最后一个节点拓扑
* 修复用户组、二级管理空间主操作下关联操作的资源实例过滤掉无限制后，会偶现授权边界溢出问题

---

<!-- 2024-10-11 -->
# V1.10.36 版本更新日志

### 新增功能
* 用户组授权支持关联不在同一系统资源类型下的权限实例范围

### 功能优化
* 更新所有文档中心跳转链接最新规范

---

<!-- 2024-09-27 -->
# V1.10.35 版本更新日志

### 缺陷修复
* 使用 pymysql 替换 mysql-client

---

<!-- 2024-09-25 -->
# V1.10.34 版本更新日志

### 新增功能
* 蓝盾用户组权限 iframe 内嵌页面增加增加、删除、编辑等事件通信需求

### 功能优化
* 更新产品文档、我的管理空间等文档跳转最新链接
* 处理实例视图最后一个节点且当前拓扑层级 child_type 为空时，不需要获取下一级数据的接口

### 缺陷修复
* 修复偶发 path 视图层展示数量与实际授权范围实例数量不一致
* 修复拓扑数据扁平化结构无法区分实例作用域范围，会存在分级管理员授权实例范围是父级，但是选择子集自动关联操作会造成数据错乱问题
* 修复我的管理空间面包屑返回页面异常

---

<!-- 2024-09-02 -->
# V1.10.33 版本更新日志

### 缺陷修复

* 申请加入用户组资源实例搜索增加系统筛选
* 组权限添加权限模板去掉刷新 icon
* 兼容容器化部署外部环境非根路径的 path

---

<!-- 2024-08-22 -->
# V1.10.32 版本更新日志

### 缺陷修复

* 修复 apigw 资源定义 yaml 错误

---

<!-- 2024-08-22 -->
# V1.10.31 版本更新日志

### 新增功能

* 超级管理类 API - 模板列表和用户组添加成员

### 缺陷修复

* 蓝盾内嵌页面隐藏跳转到授权边界入口
* 修复退出登录重定向地址转义多次

---

<!-- 2024-08-14 -->
# V1.10.30 版本更新日志

### 新增功能

* 增加当用户拥有管理员身份时且当前页面属于个人工作台 staff 角色场景下时，支持管理员菜单页面快捷跳转
* 全局配置版本升级，支持产品名称和 title 区别文案

### 缺陷修复

* 修复用户组—>分级管理员权限下依赖操作会偶现自动关联不在授权范围内的实例
* 修复申请自定义权限部分系统的操作存在批量编辑后操作关联的资源实例显示异常
* 修复二级管理员—>分级管理员权限下依赖操作会偶现自动关联不在授权范围内的实例
* 修复删除人员模板最后一页唯一一条模板数据，提示数据不存在
* 修复添加自定义权限 - 查看已经选择的数据时，已选择的操作个数会消失
* 修复新建权限模板时推荐权限输入空格点击保存，前端未做判断
* 修复用户组资源实例表格自定义权限聚合后在选择权限模板后重新聚合会偶现 resouce_group 为空情况
* 修复自定义权限查看实例资源组件有多个资源类型 tab 项时无法删除实例
* 修复新用户无任何权限申请跳转到权限中心资源实例应该置空而非无限制
* 修改国际化 language 的 cookie 有限期默认为一年

---

<!-- 2024-06-25 -->
# V1.10.29 版本更新日志

### 新增功能

* 增加 npm 集成插件统一管理 logo、footer、title 等配置项
* 全平台资源实例批量聚合方式由 switch 组件替换为自定义 tab 组件
* 全平台属性视图兼容个别接入系统自定义属性集需要展示人员选择器组件
* 全平台添加系统和操作页面排版整改（刷新功能由只对分级管理员开放改为全员开放）

### 缺陷修复

* 修复申请用户组—>无权限申请权限和常用推荐权限业务场景下需要隐藏接入系统提供的操作
* 修复申请自定义权限切换系统未清空资源实例表格数据
* 修复编辑用户组权限—>修改资源实例内容后点击取消失效

---

<!-- 2024-05-13 -->
# V1.10.28 版本更新日志

### 新增功能

* 配置权限失效提醒通知策略功能
* 权限失效提醒通知增加企业微信
* 小窗登录 iframe 方式变更且支持通过 npm 集成统一 iframe 加载模式
* 申请加入用户组——>资源实例搜索增加管理空间筛选
* 新增 API - 创建申请自定义权限审批单，支持自定义审批内容

### 缺陷修复

* 修复管理空间、用户组详情页链接直接访问会重定向到对应列表页
* 修复资源实例输入关键词进行搜索返回的数据有缺失
* 修复已关联用户组的人员模板在批量删除的时候可以成功被删除
* 修复模板关联用户组页面下拉到底部后翻页按钮显示异常
* 修复删除超级管理员成员后成功的弹窗无法自行关闭
* 修复用户组页面删除用户组后，用户组数量展示消失，需要刷新页面后才重新展示
* 修复申请续期—>自定义权限所属系统筛选无法自定义分页
* 修复只有一层拓扑且资源类型存在多条导致 type 取值错误

---

<!-- 2024-04-25 -->
# V1.10.27 版本更新日志

### 缺陷修复

* 系统注册的不可申请操作对「我的管理空间」生效
* 添加成员支持模糊搜索（解决带登录域无法搜索问题）

---

<!-- 2024-04-12 -->
# V1.10.26 版本更新日志

### 功能优化

* 依赖版本升级

### 缺陷修复

* 修复同步组织定时任务失效

---

<!-- 2024-04-11 -->
# V1.10.25 版本更新日志

### 新增功能

* 管理空间下心中用户/部门权限管理
* 系统管理员增加查询有权限的人员功能
* 系统管理员增加操作敏感等级编辑功能

---

<!-- 2024-03-01 -->
# V1.10.24 版本更新日志

### 功能优化

* 资源实例 IP 选择器改版

### 缺陷修复

* 修复我的权限——>用户组权限增加跨页选择
* 修复我的权限—>管理员交接增加跨页选择

---

<!-- 2024-02-23 -->
# V1.10.23 版本更新日志

### 缺陷修复

* 修复用户组只添加权限模板，快捷关闭后表格数据清空
* 修复权限模板添加实例无法批量粘贴
* 修复蓝盾内嵌页面部分二级管理员 role_id 错误
* 蓝盾用户组内嵌页面增加 hidden 字段筛选隐藏的系统操作

---

<!-- 2024-01-30 -->
# V1.10.22 版本更新日志

### 缺陷修复

* 修复自定义权限申请—>编辑回显无法展示已选资源实例为无限制类型数据
* 修复用户组—>添加组权限个别实例 path 数量不同步，导致出现提示层级链路列表不能为空
* 优化组织架构人员选择器隐藏已选数量为 0 的 type

---

<!-- 2024-01-22 -->
# V1.10.21 版本更新日志

### 功能优化

* 对接蓝鲸消息通知中心

---

<!-- 2024-01-16 -->
# V1.10.20 版本更新日志

### 功能优化

* 权限申请单内容优化

### 缺陷修复

* 修复蓝盾内嵌页面最大授权范围选择组织后无法选择用户
* 修复用户组添加组权限—>先添加操作和权限模板，再取消操作或者对权限模板数量进行删减后不显示
* 修复人员选择器编辑组件内容为空，重新添加会重置上一次的数据

---

<!-- 2023-12-26 -->
# V1.10.19 版本更新日志

### 新增功能

* 管理空间导航栏下新增人员模板菜单
* 用户组详情增加关联用户组的人员模板业务
* 个人工作台—>我的权限增加关联人员模板加入所属用户组权限业务
* 平台管理—>用户菜单下组织架构人员详情增加所属人员模板用户组权限业务
* 自定义权限下拉列表支持用户收藏常用系统
* 修改申请用户组超过 100 加入用户组的数量报错提示语
* 组织架构成员选择器添加人员模板选项，手动输入选项支持协定的特殊字符分割，支持单次 100 个成员限制
* 蓝盾内嵌添加最大授权范围 dailog 页面增加全员选项，支持授权范围为全员

### 缺陷修复

* 修复敏感等级搜索之后在转移列表接口总数与获取数量接口总个数不同步问题
*  修复编辑 textarea 组件点击任意占位符触发失焦问题

---

<!-- 2023-11-28 -->
# V1.10.18 版本更新日志

### 缺陷修复

* 修复处理组织架构选择器在 iam 系统和蓝盾系统中不需要校验授权范围的业务场景
* 修复用户组成员续期时间戳计算是浮点数造成四舍五入后天数显示错误
* 审计模块增加敏感等级业务区块
* 修复敏感等级全部等级筛选失效问题
* 处理蓝盾内嵌 iam 权限中心页面无自定义权限时提示 length 报错
* 克隆用户组首次加载无法批量编辑新建用户组时选择的权限模板
* 修复用户模块—>组织架构未添加人员时提交按钮置灰
* 修复 table 组件打开控制台无法自适应高度
* 我的管理空间退出功能

---

<!-- 2023-11-16 -->
# V1.10.17 版本更新日志

### 功能优化
* 敏感等级需求
* 申请自定义权限—>接入系统添加用户组超过 100 个增加自定义 message
* 用户模块—>用户类型增加资源实例搜索
* 用户模块—>组织架构成员增加添加人员

### 缺陷修复
* 前端配置化哪些页面的操作需要隐藏 (不再通过后台标识处理)
* 管理员添加成员重复时无响应 (无法添加成员时给出 tip)
* 处理 staff 角色在人员选择器里提示无权限问题

---

<!-- 2023-11-07 -->
# V1.10.16 版本更新日志

### 功能优化
* 优化添加系统和操作侧边栏处理接口调用多次异常导致有时无法聚合问题
* 我的权限列表增加底部版本声明
* 用户组成员列表支持跨页批量删除、批量续期
* 组织架构人员选择器设计改版
* 产品文档链接改为动态配置项
* 申请加入用户组超过 100 条自定义错误信息
* 申请加入用户组—>过期用户组添加续期

### 缺陷修复
* 修复用户组新建、克隆添加组权限重新编辑不变更操作后，无法回显之前所选项
* 修复分级管理员下多个无限制操作实例无法批量粘贴
* 修复聚合批量操作下处理个别操作聚合报错，导致拿不到授权范围接口数据
* 修复编辑授权边界或者编辑管理空间没有同步勾选依赖操作
* 修复批量复粘贴无可复制属性条件内容时会导致展示无限制问题
* 修复删除完所有自定义权限后，页面样式出现一个方框
* 修复批量编辑无交集的操作导致出现空白页
* 修复权限模板编辑关联实例后提示授权的用户组更新信息不完整
* 修复管理空间模块无选择实例时，没有清空选择的旧数据
* 修复自定义日期选择器无法根据时间戳显示当前所选择的天数

---

<!-- 2023-09-19 -->
# V1.10.15 版本更新日志

### 缺陷修复
* 我的权限用户搜索支持蓝盾
* 分级管理员二级管理员名字修改支持比较大小写
* 新增用户同步策略调整

---

<!-- 2023-09-14 -->
# V1.10.14 版本更新日志

### 缺陷修复
* “不可被申请”在自动推荐规则里生效
* 蓝盾我的权限页面搜索条件只展示蓝盾项目
* 静态文件 CDN hash 问题

---

<!-- 2023-09-05 -->
# V1.10.13 版本更新日志

### 新增功能
* 用户组增加“不可被申请”的属性设置

### 功能优化
* 全平台同步最新的 message 规范、searchSelect 规范
* 用户加入的用户组支持批量退出
* 用户组权限续期页面增加描述、管理员、管理空间数据展示
* 用户组成员增加，复制成员和组织架构功能
* 我的权限页面增加搜索功能
* 资源权限管理—>去掉查询类型筛选项，保留默认查询类型为实例权限

### 缺陷修复
* 蓝盾项目管理员续期邮件点击跳转链接，网页内容显示空白
* 修复用户组成员续期有效期时间戳累加计算错误
* 修复蓝盾权限交接判断 disabled 错误，用户组组权限交接和管理员交接增加分页
* 修复修改项目名称还是超时问题
* 用户申请多个组标题过长导致报错问题

---

<!-- 2023-07-31 -->
# V1.10.12 版本更新日志

### 新增功能
* 自定义权限可配置分级管理员审批
* 用户组新建、克隆、添加组权限增加批量无限制
* 用户组增加批量复制用户、组织人员功能

### 缺陷修复
* 修复用户模块->用户类型点击同步，出现第三方接口异常提示

---

<!-- 2023-07-26 -->
# V1.10.11 版本更新日志

### 新增功能
* 登录切换 ESB 接口，支持 esb 验证应用权限

---

<!-- 2023-07-17 -->
# V1.10.10 版本更新日志

### 新增功能
* 用户组成员列表增加部门展示
* 过期权限列表增加权限详情
* 聚合操作选择可选任意
* 一级管理员可直接进入二级管理员

---

<!-- 2023-07-07 -->
# V1.10.9 版本更新日志

### 缺陷修复
* 修复用户组组权限—>添加属性条件时依赖操作没同步数据
* 系统管理员成员编辑异常，系统管理员成员输入框异常
* 我的权限添加删除单系统下所有操作实例需求
* 用户组组权限删除、查看模块排版整改

---

<!-- 2023-07-05 -->
# V1.10.8 版本更新日志

### 缺陷修复
* 修复前端国际化问题

---

<!-- 2023-06-27 -->
# V1.10.7 版本更新日志

### 新增功能
* 自定义权限删除实例时同时删除被依赖权限的实例

### 缺陷修复
* ITSM 提单表单字段国际化
* 语言切换制定 BK_DOMAIN
* 分级管理员同步权限用户组名称国际化

---

<!-- 2023-06-21 -->
# V1.10.6 版本更新日志

### 缺陷修复
* 分级管理员默认流程设置为空问题
* 修复审计日志记录表创建名称问题

---

<!-- 2023-06-07 -->
# V1.10.5 版本更新日志

### 新增功能
* 申请用户组权限可以通过操作与实例搜索用户组

### 功能优化
* 优化关联权限删除逻辑

---

<!-- 2023-06-02 -->
# V1.10.4 版本更新日志

### 新增功能
* BCS 自动初始化管理员用户组

### 缺陷修复
* 修复用户列表查询列表 bug
* gunicorn 增加 max request number

---

<!-- 2023-05-29 -->
# V1.10.3 版本更新日志

### 功能优化
* 优化权限申请审批单创建动态字段方式

---

<!-- 2023-05-25 -->
# V1.10.2 版本更新日志

### 功能优化
* 优化蓝盾权限迁移功能

---

<!-- 2023-05-18 -->
# V1.10.1 版本更新日志

### 缺陷修复
* open api 创建权限申请单增加过期时间
* 修复提交自定义权限申请未处理权限剔除

---

<!-- 2023-05-10 -->
# V1.10.0 版本更新日志

### 新增功能
* 支持二级管理空间功能

---

<!-- 2023-03-28 -->
# V1.9.10 版本更新日志

### 新增功能
* 增加临时权限开关
* 修改 api 可创建的分级管理员最大数量 500

---

<!-- 2023-02-20 -->
# V1.9.9 版本更新日志

### 缺陷修复
* 管理类接口用户组授权不关联资源实例转换 bug

---

<!-- 2023-01-31 -->
# V1.9.8 版本更新日志

### 新增功能
* 初始化分级管理员更新定制操作

### 缺陷修复
* 修复 healthz 接口主动关闭 mysql 连接
* 修复前端体验问题

---

<!-- 2022-12-22 -->
# V1.9.7 版本更新日志

### 缺陷修复
* 操作权限删除部分实例报错

---

<!-- 2022-11-28 -->
# V1.9.6 版本更新日志

### 缺陷修复
* 修复克隆用户组数据未在第一页显示为空

---

<!-- 2022-11-22 -->
# V1.9.5 版本更新日志

### 缺陷修复
* 修复用户组可能选择实例为空问题

### 功能优化
* 推荐操作只移除用户已有的实例
* 操作列表缓存一分钟

---

<!-- 2022-11-08 -->
# V1.9.4 版本更新日志

### 缺陷修复
* 修复 chooseip 拓扑组件点击查看更多漏缺搜索关键字

---

<!-- 2022-11-02 -->
# V1.9.3 版本更新日志

### 缺陷修复
* 用户组授权不关联资源类型的操作未生效问题

---

<!-- 2022-10-12 -->
# V1.9.2 版本更新日志

### 新增功能
* 合并 master 分支变更
* 优化过期提醒邮件发送逻辑

---

<!-- 2022-08-25 -->
# V1.9.1 版本更新日志

### 新增功能
* 增加 v2 版本管理类 api

---

<!-- 2022-07-15 -->
# V1.9.0 版本更新日志

### 新增功能
* 用户组配置 RBAC 策略

---

<!-- 2022-10-10 -->
# V1.8.25 版本更新日志

### 缺陷修复
* 初始化分级管理员修复定制系统不一致问题

---

<!-- 2022-09-27 -->
# V1.8.24 版本更新日志

### 缺陷修复
* 前端国际化问题修复

---

<!-- 2022-09-27 -->
# V1.8.23 版本更新日志

### 缺陷修复
* 前端体验修复

---

<!-- 2022-09-27 -->
# V1.8.22 版本更新日志

### 缺陷修复
* 前端体验修复

---

<!-- 2022-09-26 -->
# V1.8.21 版本更新日志

### 缺陷修复
* 修复前端克隆问题
* 修复新增用户组批量编辑问题
* 修复新建用户组数据重复问题
* 优化分级管理员图片
* 优化版本日志 icon
* 优化无权限应该禁用权限交接
* 优化续期 tips
* 优化权限交接禁用
* 优化下拉框字体颜色
* 修复克隆可以选择全部实例的 bug
* 修复授权与操作不一致的 bug

---

<!-- 2022-09-24 -->
# V1.8.20 版本更新日志

### 缺陷修复
* 修复自定义申请续期检查实例数量 bug
* 修复前端体验问题

---

<!-- 2022-09-23 -->
# V1.8.19 版本更新日志

### 缺陷修复
* 修复 1 天以内过期时间展示问题
* 修复初始化分级管理员成员过期时间错误
* 修复前端若干体验问题

---

<!-- 2022-09-21 -->
# V1.8.18 版本更新日志

### 功能优化
* 移除 permission logger
* 增加初始化分级管理员功能，需要环境变量开关 BKAPP_ENABLE_INIT_GRADE_MANAGER
* 初始化系统管理员增加默认成员
* 前端体验优化

---

<!-- 2022-09-09 -->
# V1.8.17 版本更新日志

### 缺陷修复
* 修复切换导航时获取角色失败的 bug

---

<!-- 2022-09-08 -->
# V1.8.16 版本更新日志

### 功能优化
* 优化过期时间显示

### 缺陷修复
* 修复切换导航时获取角色失败的 bug

---

<!-- 2022-09-02 -->
# V1.8.15 版本更新日志

### 缺陷修复
* healthz 修改 celery 检查超时时间
* 修复角色只有一种角色且为系统管理员的 bug

---

<!-- 2022-09-01 -->
# V1.8.14 版本更新日志

### 缺陷修复
* healthz 依赖用户管理逻辑优化
* 修复角色仅为系统管理员页面卡顿的 bug

### 功能优化
* 用户组名称最小长度更新为 2 个字符

---

<!-- 2022-08-25 -->
# V1.8.13 版本更新日志

### 缺陷修复
* 无权限跳转申请推荐权限去除用户已有权限
* 更新管理类 api 错误信息
* 多窗口页面切换分级管理员权限问题

---

<!-- 2022-08-04 -->
# V1.8.12 版本更新日志


### 缺陷修复
* 修改头部跳转逻辑
* 分级管理员删除用户组错误

---

<!-- 2022-07-28 -->
# V1.8.11 版本更新日志

### 功能优化
* 监听 ipv6

### 缺陷修复
* 修改分级管理员基本信息只校验新增成员的数量限制

---

<!-- 2022-07-19 -->
# V1.8.10 版本更新日志

### 缺陷修复
* 修复 model_event 变更事件由于数据转换出错而执行失败

---

<!-- 2022-07-12 -->
# V1.8.9 版本更新日志

### 新增功能
* 新增分级管理员指引

---

<!-- 2022-07-01 -->
# V1.8.8 版本更新日志

### 缺陷修复
* 邮件文案调整
* windows 窗口 title 问题
* 按需申请无限制问题
* 推荐操作重复问题

---

<!-- 2022-06-23 -->
# V1.8.7 版本更新日志

### 功能优化
* 无权限跳转申请页面优化
* 导航调整
* 通知邮件模板优化

---

<!-- 2022-06-21 -->
# V1.8.6 版本更新日志

### 缺陷修复
* 修复新建关联实例授权 API 白名单 - 监控白名单不生效问题

---

<!-- 2022-06-16 -->
# V1.8.5 版本更新日志

### 缺陷修复
* 修复推荐操作点击无法选中问题

---

<!-- 2022-05-31 -->
# V1.8.4 版本更新日志

### 新增功能
* 新增管理类 API
  - 删除用户组策略
  - 支持回收用户组策略的资源实例权限
  - 分页查询某个系统创建的分级管理员列表
  - 更新分级管理员授权范围和基本信息
* 增强授权 API - 支持授权与资源实例无关的操作权限
* 支持定时清理已完成的模型变更事件

### 功能优化
* Cache 重构，统一使用 Django Cache
* 完善各数据模型的数量限制
  - 资源 ID 限制 36 位
  - 每个系统可创建最多 100 个分级管理员
  - 一个分级管理员可添加的成员个数：100
  - 一个用户可加入的分级管理员个数：100
  - 一个分级管理员可创建的用户组个数：100
* 分页参数由limit/offset调整为page/page_size
* 性能优化 - 每月审计表全局变量缓存
* Swagger 重构

### 缺陷修复
* 修复前端相关体验问题

---

<!-- 2022-05-16 -->
# V1.8.3 版本更新日志

### 缺陷修复
* 只有临时权限时，我的权限不展示问题
* 临时权限过期时间选择问题
* request_id 参数错误问题

---

<!-- 2022-05-13 -->
# V1.8.2 版本更新日志

### 缺陷修复
* 临时权限系统切换操作未清空问题
* 临时权限聚合操作资源选择问题

---

<!-- 2022-05-10 -->
# V1.8.1 版本更新日志

### 新增功能
* 无权限跳转增加推荐权限

---

<!-- 2022-03-23 -->
# V1.8.0 版本更新日志

### 新增功能
* 临时权限

---

<!-- 2022-05-19 -->
# V1.7.19 版本更新日志

### 缺陷修复
*  无权限跳转申请没有依赖操作的问题

---

<!-- 2022-05-12 -->
# V1.7.18 版本更新日志

### 缺陷修复
* 资源实例选择下级搜索报错问题

---

<!-- 2022-04-26 -->
# V1.7.17 版本更新日志

### 缺陷修复
* 聚合操作无限制问题修复

---

<!-- 2022-04-25 -->
# V1.7.16 版本更新日志

### 缺陷修复
* 聚合操作批量复制批量粘贴问题修复

---

<!-- 2022-04-25 -->
# V1.7.15 版本更新日志

### 缺陷修复
* 聚合操作选择相关问题修复
* 审批流程操作列表支持国际化

### 功能优化
* Django 版本升级到 2.2.27

---

<!-- 2022-04-21 -->
# V1.7.14 版本更新日志

### 新增功能
* 接入系统回调查询实例列表支持传祖先实例
* 聚合操作支持同时聚合多种资源类型

---

<!-- 2022-04-19 -->
# V1.7.13 版本更新日志

### 功能优化
* OpenAPI分页参数调整为page_size/page，对于admin.list_group/admin.list_group_member/mgmt.list_group/mgmt.list_group_member已开放接口，兼容limit/offset

---

<!-- 2022-04-13 -->
# V1.7.12 版本更新日志

### 缺陷修复
* 修复国际化相关数据

### 功能优化
* 优化导航条显示

---

<!-- 2022-04-07 -->
# V1.7.11 版本更新日志

### 缺陷修复
* 修复分级管理员申请单 ITSM 展示问题
* 修复前端合并选择实例问题

### 功能优化
* sentry sdk 切换

---

<!-- 2022-04-01 -->
# V1.7.10 版本更新日志

### 缺陷修复
* 查询资源有权限的 subject 修复跨系统资源查询报错

---

<!-- 2022-04-01 -->
# V1.7.9 版本更新日志

### 缺陷修复
* 修复资源权限管理查询接口报错问题
* 修复用户组跨页添加多个组权限，确定后，会缺失跨页选中的权限模板的问题
* 修复申请有关联权限，选择实例后，默认期限会变为不可更改的问题

---

<!-- 2022-03-24 -->
# V1.7.8 版本更新日志

### 缺陷修复
* 修复分级管理员下不能添加权限的问题
* 新增系统接入说明
* 修复用户组不存在导致用户组续期申请回调报错问题

---

<!-- 2022-03-15 -->
# V1.7.7 版本更新日志

### 功能优化
* 环境属性功能 release

---

<!-- 2022-03-08 -->
# V1.7.6 版本更新日志

### 功能优化
* apigw 新增user-groups/department-groups两个开放 API
* 变更原 policy 查询三个 api 的路径，增加 /open/(但是保持向前兼容: 老的 public=false, 新增三个新的)
* apigw-manage 升级到 1.0.2
* apigw 配置后端由 SaaS Web 调整为 SaaS API

---

<!-- 2022-03-04 -->
# V1.7.5 版本更新日志

### 功能优化
* 对接 APIGateway 的 SaaS Open API，其后端由 bkiam-saas-web 调整为 bkiam-saas-api

### 缺陷修复
* 修复前端用户组配置权限相关问题
* 组织架构部门同步修复了部门lft/rght/level数据错误问题

---

<!-- 2022-03-02 -->
# V1.7.4 版本更新日志

### 缺陷修复
* 修复 healthz 导致 redis 连接泄露问题
* 修复前端用户组配置权限没有显示资源类型问题

---

<!-- 2022-02-24 -->
# V1.7.3 版本更新日志

### 缺陷修复
* 修复自动注册 apigateway 配置错误

---

<!-- 2022-02-24 -->
# V1.7.2 版本更新日志

### 缺陷修复
* 修复权限模板变更操作报错
* 修复自动注册 apigateway 配置错误

---

<!-- 2022-02-21 -->
# V1.7.1 版本更新日志

### 新增功能
* 定时清理后台未被引用的 expression

### 功能优化
* 优化操作审计信息
* 优化日志打印
* 优化 SaaS Django 配置，去除 blueapps 依赖

---

<!-- 2021-01-11 -->
# V1.7.0 版本更新日志

### 新增功能
* 关联多个资源类型的操作支持配置多个实例组合
* 权限策略增加生效条件

---

<!-- 2022-01-20 -->
# V1.6.5 版本更新日志

### 缺陷修复
* 修复注册 API 网关配置错误

### 功能优化
* ESB 及 Login 慢请求打 component 日志
* 增加 bk_job 操作 file_resource 的新建关联白名单

---

<!-- 2021-12-23 -->
# V1.6.4 版本更新日志

### 缺陷修复
* 修复权限交接 bug
* 修复自动注册 apigateway 脚本错误
* 修复同步 ITSM 申请单状态报错

---

<!-- 2021-12-21 -->
# V1.6.3 版本更新日志

### 新增功能
* 查询有权限的 subjects

---

<!-- 2021-12-16 -->
# V1.6.2 版本更新日志

### 新增功能
* opentelemetry 链路跟踪

### 功能优化
* 增加权限交接功能开关

---

<!-- 2021-12-10 -->
# V1.6.1 版本更新日志

### 新增功能
* 权限交接

### 功能优化
* 前端重构

---

<!-- 2021-12-08 -->
# V1.5.16 版本更新日志

### 功能优化
* 组织架构同步时不删除后台用户和部门

### 缺陷修复
* 锁定依赖包 typing-extensions 版本，避免自动更新最新版导致部署失败

---

<!-- 2021-12-06 -->
# V1.5.15 版本更新日志

### 缺陷修复
* 修复 LongTask 改同步后，celery_id 获取为 None 的问题
* 修复分级管理员权限 Scope 数据结构不兼容 action_id 问题

---

<!-- 2021-11-30 -->
# V1.5.14 版本更新日志

### 新增功能
* 支持初始化接入 APIGateway 的 API 和文档

### 功能优化
* 自动更新资源实例名称对大策略的防御性忽略
* 新增接入系统管理类 API 的 bk_nocode 白名单
* 调用第三方接口失败时支持返回异常信息
* 用户组授权调整为立即执行任务

### 缺陷修复
* 自动更新资源实例名称兼容接入系统回调异常
* 解决未资源实例视图为空时导致授权异常

---

<!-- 2021-11-23 -->
# V1.5.13 版本更新日志

### 新增功能
* 授权 API 白名单支持前缀匹配规则
* 自动更新策略里的重命名的资源实例

### 功能优化
* 组织名称 tips 显示完整路径
* 组织架构同步记录中的日志详情添加换行
* 接入系统管理类 API 对于创建分级管理员和用户组授权接口支持无限制资源实例的授权

### 缺陷修复
* 修复分级管理员用户组模板授权报错
* 修复无权限跳转推荐的用户组权限已过期的 bug
* 后台任务清理用户组过期成员的审计异常
* 修复 Action 模型删除事件处理异常问题
* 解决 migrate 时依赖 esb 的问题
* 修复 project_view 问题导致系统授权报错

---

<!-- 2021-11-11 -->
# V1.5.12 版本更新日志

### 功能优化
* 增加用户同步记录
* 分级管理员修改操作范围后，范围不一致的模板不能授权

---

<!-- 2021-11-04 -->
# V1.5.11 版本更新日志

### 功能优化
* redis 版本降级 2.10.6, 作为 celery broker

### 缺陷修复
* 修复容器化版本的日志配置
* 修复 redis timeout 配置问题

---

<!-- 2021-10-21 -->
# V1.5.10 版本更新日志

### 缺陷修复
* 修复越权访问用户组成员列表问题

---

<!-- 2021-10-20 -->
# V1.5.9 版本更新日志

### 缺陷修复
* 修复长时任务获取结果报错

---

<!-- 2021-10-20 -->
# V1.5.8 版本更新日志

### 功能优化
* 优化资源回调结构错误提示
* 长时任务重试

### 缺陷修复
* 修复更新模板未同步到用户组权限问题
* 修复非80/443端口时cookie domain 错误问题
* 取消勾选对应权限的实例报错
* 修复后台关联数据时 tag 返回值 bug

---

<!-- 2021-10-11 -->
# V1.5.7 版本更新日志

### 缺陷修复
* 修复url拼接多个/导致访问出错问题
* 修复前端人员列表组件范围地址错误问题

---

<!-- 2021-10-11 -->
# V1.5.6 版本更新日志

### 缺陷修复
* 修复管理类 API-用户组自定义授权异步导致无法连续授权失败

---

<!-- 2021-10-08 -->
# V1.5.5 版本更新日志

### 缺陷修复
* 用户组更新模板授权报错

---

<!-- 2021-09-29 -->
# V1.5.4 版本更新日志

### 功能优化
* 自定义权限申请支持实例审批人
* 跳转申请不合并用户的已有权限
* 授权 api 返回策略的实例数量

### 缺陷修复
* 修复企业微信邮件中续期邮件链接显示问题
* 我的权限用户组权限查看态提示删除 bug
* 业务跳转权限中心申请权限，申请期限不能修改
* 修复通用操作显示问题

---

<!-- 2021-09-24 -->
# V1.5.3 版本更新日志

### 缺陷修复
* 修复 v3 Smart 包前端 ESB 地址
* 修复忽略路径 bug 导致授权信息错误
* 修复续期邮件企业微信邮箱链接显示问题
* 修改我的权限用户组权限查看态提示删除 bug
* 修复资源实例无限制的权限，申请权限时不应该能修改
* 修复业务跳转权限中心申请权限，申请期限不能修改

---

<!-- 2021-09-15 -->
# V1.5.2 版本更新日志

### 功能优化
* 更新 paas v3 smart 配置
* 分享链接自动带上条件过滤

### 缺陷修复
* 修复权限策略部分删除报错问题
* 修复由于资源实例名称中存在空格导致授权报错问题
* 修复清理过期权限出错问题
* 修改权限审批使用系统管理员审批流程审批人员为空问题
* 修复管理类 API 创建用户组绑定分级管理员错误问题
* 修复管理类 API 创建分级管理员时授权范围没有按照系统聚合导致后续授权问题
* 修复未选择任何权限可保存为推荐权限模板
* 修复从配置平台跳转到权限中心无法选择
* 修复已有实例权限不应该纳入新实例申请限制数里
* 修复普通用户没有任何分级管理员时无法注销问题

---

<!-- 2021-09-09 -->
# V1.5.1 版本更新日志

### 缺陷修复
* 修复新建关联授权 API 由于注册的配置里存在资源类型层级导致失败问题

---

<!-- 2021-08-30 -->
# V1.5.0 版本更新日志

### 功能优化
* SaaS 代码重构
* 开源代码优化

---

<!-- 2021-08-26 -->
# V1.4.30 版本更新日志

### 功能优化
* 调整普通用户可管理其加入的分级管理员成员列表
* 更新JOB/BCS新建关联API白名单

### 缺陷修复
* 接入页面实例视图 id，资源类型 ID 唯一性校验，按钮位置调整
* 接入页面表单验证规则修复
* 接入页面删除操作 type 值修改
* 接入页面删除操作时屏幕闪烁
* 接入页面步骤切换时跳转错误的问题
* 接入页面其他体验问题修复以及文案优化
* 修复接入页面导出 JSON 丢失 system clients 数据
* 修复分级管理员可授权范围由全员调整为其他时的错误

---

<!-- 2021-08-13 -->
# V1.4.29 版本更新日志

### 功能优化
* 权限过期提醒邮件改为 11 点发送

### 缺陷修复
* 用户组授权校验分级管理员授权范围报错问题
* 授权页面忽略路径导致授权数据错误问题

---

<!-- 2021-08-11 -->
# V1.4.28 版本更新日志

### 功能优化
* 优化“忽略路径”后前端展示完整路径

### 缺陷修复
* 修复作业平台授权具体主机实例报错问题

---

<!-- 2021-08-10 -->
# V1.4.27 版本更新日志

### 功能优化
* 优化资源类型 ID 校验
* 优化操作 ID 校验
* 优化资源类型保存问题

### 缺陷修复
* 修复依赖资源勾选 bug
* 修复切换身份问题
* 修复模型创建完成 icon 问题

---

<!-- 2021-08-05 -->
# V1.4.26 版本更新日志

### 功能优化
* 分级管理员过滤问题
* 系统注册校验规则
* 回调地址校验合法性

### 缺陷修复
* 修复添加 gsekit 权限报错问题
* 修复差异对比异常

---

<!-- 2021-08-02 -->
# V1.4.25 版本更新日志

### 缺陷修复
* 申请单详情拒绝非申请人查看
* 操作列表拒绝非登录用户查看

---

<!-- 2021-08-02 -->
# V1.4.24 版本更新日志

### 功能优化
* 续期页面交互优化

### 缺陷修复
* v2migrate api 权限模板增加授权对象出错 bug 修复
* 修复忽略路径授权实例失败的问题
* 修复自定义权限申请点击续期无响应问题

---

<!-- 2021-07-22 -->
# V1.4.23 版本更新日志

### 功能优化
* 申请侧有效期去掉“永久”时间
* 一些已知问题优化

### 缺陷修复
* 修复依赖操作自动填充过期时间为空问题
* 修复分级管理员选择人员范围保存失败问题
* 修复依赖操作实例变只读问题
* 修复一些已知问题

---

<!-- 2021-07-20 -->
# V1.4.22 版本更新日志

### 缺陷修复
* 修复依赖操作自动填充过期时间为空问题

---

<!-- 2021-07-20 -->
# V1.4.21 版本更新日志

### 缺陷修复
* 修复 CORS 任意 Origin 请求的安全问题
* 修复编辑分级管理员页面报错
* 修复编辑用户组权限，新增自定义权限不保存再次编辑自定义权限，保存后添加的自定义权限不显示在权限页问题
* 修复申请自定义权限选择有关联权限后，后置权限选择实例，前置权限实例期限为空且不能修改的问题

---

<!-- 2021-07-19 -->
# V1.4.20 版本更新日志

### 缺陷修复
* 修复自定义权限申请，存在依赖关系时选择资源实例后不能再编辑的问题
* 修复自定义权限有效期为空的问题

---

<!-- 2021-07-15 -->
# V1.4.19 版本更新日志

### 新增功能
* 分级管理员相关操作链接支持角色 id 参数；支持自动切换分级管理员身份

### 功能优化
* 我的权限，只有一个系统的自定义权限时默认展开
* 更新 ITSM 新建关联 API 白名单

### 缺陷修复
* 修复删除分级管理员操作问题
* 修复组同时添加自定义权限和模板权限问题
* 修复分级管理员推荐权限显示问题
* 修复人员输入框带空格时导致的问题

---

<!-- 2021-07-13 -->
# V1.4.18 版本更新日志

### 功能优化
* 分级管理员编辑态优化

### 缺陷修复
* 无权限跳转有效期时间处理
* 权限模板更新问题
* 用户组添加权限依赖操作问题
* 组添加模板权限选择实例报错问题
* 用户组添加模板权限
* 分级管理员编辑操作问题
* 权限模板更新后还显示编辑中问题

---

<!-- 2021-07-08 -->
# V1.4.17 版本更新日志

### 缺陷修复
* 用户组添加模板权限选择实例样式错乱问题
* 用户组添加权限出现部分实例选择框不可点击问题
* 分级管理员编辑态优化，最大权限发范围默认折叠
* 权限模板更新后还显示「编辑中」问题

---

<!-- 2021-07-05 -->
# V1.4.16 版本更新日志

### 缺陷修复
* 修复用户组添加自定义权限报有效期错误
* 修复合并选择/批量编辑错误问题
* 修复用户组自定义权限依赖操作问题
* 修复分级管理员新增操作 bug
* 修复分级管理员和用户组授权范围不一致问题
* 修复切换身份问题
* 修复用户组删除自定义权限报错
* 修复续期邮件跳转前端 bug
* 修复用户组权限模板删除样式优化

---

<!-- 2021-07-01 -->
# V1.4.15 版本更新日志

### 新增功能
* 支持异步删除 Action 和删除 Action 的策略
* 用户组自定义权限支持删除某个操作权限功能
* 支持通过环境变量来启用系统接入的功能

### 功能优化
* 用户组权限编辑问题优化
* 用户组权限展示优化
* 授权用户组 OpenAPI 支持跳过分级管理员权限范围校验

### 缺陷修复
* 修复分级管理员文案问题
* 修复批量编辑（合并选择）选择实例自动展开问题

---

<!-- 2021-06-17 -->
# V1.4.12 版本更新日志

### 新增功能
* SaaS 侧无权限跳转自动匹配用户组

### 功能优化
* 分级管理员切换身份优化

### 缺陷修复
* 修复申请用户组页面 ID 搜索 bug
* 修复申请页面搜索条件缓存问题
* 修复退出分级管理员失败问题

---

<!-- 2021-06-15 -->
# V1.4.11 版本更新日志

### 新增功能
* 新增管理员 API- 获取某个用户在某个分级管理员下的用户组列表
* 支持用户组授权 API

### 缺陷修复
* 修复未配置 IAM-Engine 请求 Endpoint 的问题
* 修复当申请通过之前用户组已经被删除未忽略错误导致异常问题

---

<!-- 2021-06-08 -->
# V1.4.10 版本更新日志

### 新增功能
* 支持页面接入，在页面配置并生成权限模型

---

<!-- 2021-05-28 -->
# V1.4.9 版本更新日志

### 缺陷修复
* 修复 1.4.5 开始引入的 SaaS 删除用户组，但后台未删除，导致权限错误的问题

---

<!-- 2021-05-19 -->
# V1.4.8 版本更新日志

### 新增功能
* 授权 Open API 支持有效期设置
* 批量授权 Open API 支持授予无限制范围的权限
* 支持删除策略订阅事件推送

### 功能优化
* Open API 支持错误码 1902409 来表示重复名称等的冲突
* 我的权限页面排序调整

### 缺陷修复
* 修复过滤用户组时缺少全员范围判断的问题
* 修复无法删除分级管理员成员的问题
* 修复权限资源实例的 Tips 重复显示问题

---

<!-- 2021-05-13 -->
# V1.4.7 版本更新日志

### 新增功能
* 自动生成聚合操作配置
* 依赖操作
* 用户组支持按角色筛选
* ping api

---

<!-- 2021-04-28 -->
# V1.4.6 版本更新日志

### 新增功能
* 管理类 API-创建分级管理员和用户组授权支持授予部分资源无限制
* 管理类 API 支持配置系统可管控授权的系统范围

---

<!-- 2021-04-27 -->
# V1.4.5 版本更新日志

### 功能优化
* 我的权限页面优化

### 缺陷修复
* 修复用户组删除时，其关联的权限模板成员数量无更新的问题
* 修复更新权限模板时名称可为空的问题
* 修复用户组授权时新增权限模板 404
* 修复新增用户组时组权限为空报错问题

---

<!-- 2021-04-19 -->
# V1.4.4 版本更新日志

### 新增功能
* 新版权限模板
* 用户组自定义权限

### 功能优化
* 一些已知问题优化

### 缺陷修复
* 一些已知问题修复

---

<!-- 2021-04-01 -->
# V1.3.6 版本更新日志

### 新增功能
* 新增权限模板全量同步脚本

### 缺陷修复
* 修复分级管理员创建未校验实例视图问题

---

<!-- 2021-03-25 -->
# V1.3.5 版本更新日志

### 新增功能
* 新增 GSEKIT 操作聚合配置

---

<!-- 2021-03-23 -->
# V1.3.4 版本更新日志

### 缺陷修复
* 修复分级管理员限制不生效问题
* 修复权限申请选择实例清空无效问题

---

<!-- 2021-03-18 -->
# V1.3.3 版本更新日志

### 功能优化
* 用户组添加用户时提前去重
* 选择操作面板去掉展开查看更多的交互

### 缺陷修复
* 修复更新分级管理员基础信息时越权问题
* 修复选择无限制实例时复制粘贴报错问题
* 修复 v2migrate api 认证导致审计报错问题
* 修复加密解释器记录 celery 任务 trace 信息报错问题

---

<!-- 2021-03-09 -->
# V1.3.2 版本更新日志

### 新增功能
* 分级管理员增加克隆功能

### 代码优化
* 部分代码重构

### 功能优化
* 分级管理员选择操作时增加操作分组的快捷选择

### 缺陷修复
* 批量续期权限时，选择期限未生效
* 申请自定义权限，需要续期权限时选择期限未生效

---

<!-- 2021-02-25 -->
# V1.3.1 版本更新日志

### 代码优化
* 部分代码重构

---

<!-- 2021-02-20 -->
# V1.3.0 版本更新日志

### 新增功能
* 支持根据 Request ID 或 task ID 进行 Debug Trace

### 功能优化
* 添加用户组成员最大数量 1000 的限制

---

<!-- 2021-02-19 -->
# V1.2.15 版本更新日志

### 缺陷修复
* 修复 BK_PAAS_HOST 带端口时无法验证通过 CSRF_TRUSTED_ORIGINS
* 修复分级管理员续期提醒邮件用户组超限问题

---

<!-- 2021-02-02 -->
# V1.2.14 版本更新日志

### 缺陷修复
* 修复自定义权限续期时 ITSM 审批单据里操作名称不显示的问题

---

<!-- 2021-01-28 -->
# V1.2.13 版本更新日志

### 新增功能
* 操作审计
* 定期删除过期权限策略

### 功能优化
* 更新分级管理员的用户组成员过期提醒

---

<!-- 2021-01-25 -->
# V1.2.12 版本更新日志

### 功能优化
* 更新审批回调地址为内网地址
* 分级管理员名称唯一性检查

### 缺陷修复
* 修复权限配置时层级选择问题
* 修复申请单据有效期显示错误问题

---

<!-- 2021-01-20 -->
# V1.2.11 版本更新日志

### 缺陷修复
* 修复申请更新分级管理员异常
* 修复常用操作选择分组异常

---

<!-- 2021-01-15 -->
# V1.2.10 版本更新日志

### 缺陷修复
* 修复更新分级管理员异常

---

<!-- 2021-01-14 -->
# V1.2.9 版本更新日志

### 新增功能
* 实例授权相关 API 添加白名单限制
* 支持国际化时区

### 功能优化
* 编辑模板和分级管理员添加资源实例 ID 和 Name 校验
* 侧滑关闭增加二次确认交互
* 新增的权限不判断是否过期
* Enum 类代码重构优化
* Celery Healthz 优化

### 缺陷修复
* 修复鉴权相关接口判断超级权限时用户不存在异常问题
* 新建权限模板时操作合并时表格数据显示错误问题修复

---

<!-- 2021-01-14 -->
# V1.2.8 版本更新日志

### 缺陷修复
* 修复 V2 数据迁移 V3 时用户组未绑定分级管理员导致迁移失败问题

---

<!-- 2020-12-31 -->
# V1.2.7 版本更新日志

### 新增功能
* 自定义申请增加操作分组功能

### 功能优化
* 默认 Migrate DB 时同步 admin 用户且添加为超级管理员成员
* 反馈链接支持多版本区分
* 无权限跳转定位到选择的操作
* 拓扑实例支持按住 shift 批量选择


### 缺陷修复
* 修复审批流程设置时部分 API 无鉴权问题
* 修复无组织归属的用户提交申请单据错误问题
* 修复主动给用户组成员续期时不生效问题
* 修复单据撤销状态未显示问题
* 修复新增审批流程文案提示信息泄露问题
* 修复新建用户组名时校验规则前后端不一致问题
* 修复审批流程设置页面在角色切换后未更新问题
* 修复当选择带无限制的层级资源时资源实例 ID 和 Name 错误问题
* 修复聚合选择实例时第二次选择查询条件未重置问题

---

<!-- 2020-12-24 -->
# V1.2.6 版本更新日志

### 新增功能
* 增加新手指引
* 增加策略过期邮件提醒

### 功能优化
* 优化授权时若已有策略包含了新策略则不更新
* 操作分组增加默认分组不可删除逻辑

### 缺陷修复
* 修复删除策略实例可能出现的 DB 竞争锁问题
* 修复权限模板聚合实例选择具体实例时报错
* 修复选择实例点击批量粘贴时会触发打开选择实例的侧边栏

---

<!-- 2020-12-17 -->
# V1.2.5 版本更新日志

### 新增功能
* 申请单据支持撤销
* 支持用户的用户组与自定义权限续期
* 支持管理员的用户组成员续期
* 选择实例增加聚合与非聚合时的粘贴和批量粘贴
* 支持初始化时使用 ITSM 默认流程
* 支持查询回调接入系统的资源实例名称缓存
* 支持接入系统注册功能开关

### 功能优化
* 支持按功能页面区分产品文档链接
* 分级管理员页面增加更多详情链接
* 前端缓存页面表格数据的查询参数
* 权限选择实例聚合操作的交互优化
* 所有权限提交都校验资源实例 ID 和 Name 是否匹配
* 默认无归属的用户组和模板迁移到超级管理员下

### 缺陷修复
* 修复编辑分级管理员时聚合操作的开关状态显示错误
* 修复设置默认审批流程数据未及时生效

### 包依赖
* [ee] bk_itsm >= 2.5.7.235 ([ce] bk_itsm >= 2.5.7.237)

---

<!-- 2020-12-03 -->
# V1.2.4 版本更新日志

### 新增功能
* 我的审批菜单，用户点击跳转到 ITSM 个人审批中心
* 超级管理员可以将用户组转出到指定的分级管理员
* 批量鉴权 api

### 功能优化
* 去除新手指引
* 分级管理员详情系统的操作权限增加展开收起交互
* 分级管理员详情系统操作权限列表增加按系统过滤
* 选择单个实例时直接显示其实例名称
* 优化 subject action 的缓存方式
* 优化鉴权时超级权限的角色判断

### 缺陷修复
* 修复搜索拓扑实例缓存错误问题
* 分级管理员详情成员列表编辑按钮样式错乱修复
* 新建权限模板多个实例视图存在范围限制时，切换不用视图实例数据不匹配问题修复
* 超级管理员时新建权限模板属性选择框禁用问题修复
* 新建分级管理员选择了跨系统的相同操作 id 时保存实例数据错误问提修复

---

<!-- 2020-11-26 -->
# V1.2.3 版本更新日志

### 新增功能
* 分级管理员申请修改

### 功能优化
* 创建分级管理员支持生成依赖操作

### 缺陷修复
* 权限模板修改部分资源未删除 bug
* 前端若干 bug 修复

---

<!-- 2020-11-20 -->
# V1.2.2 版本更新日志

### 新增功能
* 支持新增用户 1 分钟内实时同步

### 功能优化
* 初始化超级管理员方式从 API 调用调整为部署时 Migrate DB
* 申请权限选择单个实例时直接显示其具体实例
* 产品文档链接更新
* 新建权限模板当实例存在限制数据时搜索应调整为前端搜索
* 登录窗口大小适配调整

### 缺陷修复
* 修复权限申请偶发选择了具体实例但是传了空值的问题

---

<!-- 2020-11-18 -->
# V1.2.1 版本更新日志

### 功能优化
* 初始化操作聚合优化
* 展示流程列表时审批节点显示优化
* 注销窗口样式优化
* 超级管理员将当前登录的用户删除时自动刷新页面
* 申请权限选择单个实例时直接显示其具体实例

### 缺陷修复
* 修复 OpenAPI 在超级管理员不存在的情况下鉴权角色出错
* 申请权限时复制实例粘贴按钮显示 bug 修复

---

<!-- 2020-11-17 -->
# V1.2.0 版本更新日志

### 新增功能
* 支持分级管理员功能
* 审批流程对接 itsm（支持审批通知）
* 支持超级管理员、系统管理员设置
* 多操作实例合并选择
* 支持常用操作保存（管理员功能）
* 支持管理员角色切换
* 支持审批流程配置

### 功能优化
* 全站搜索优化

---

<!-- 2020-12-07 -->
# V1.1.46 版本更新日志

### 缺陷修复
* 修复搜索拓扑实例缓存错误问题

---

<!-- 2020-11-12 -->
# V1.1.45 版本更新日志

### 新增功能
* 支持用户登出功能

### 功能优化
* 更新产品文件链接

### 缺陷修复
* 修复新建权限模板在切换系统时描述清空的问题
* 修复用户组编辑基本信息时保存异常问题

---

<!-- 2020-11-09 -->
# V1.1.44 版本更新日志

### 缺陷修复
* 修复前端处理实例选择增加无限制错误

---

<!-- 2020-11-04 -->
# V1.1.43 版本更新日志

### 新增功能
* 新增产品文档链接入口

### 功能优化
* 资源实例搜索第一层级报错提示优化
* 表格搜索框前端优化

---

<!-- 2020-10-22 -->
# V1.1.42 版本更新日志

### 缺陷修复
* 修复数据迁移接口产生 add tag 问题

---

<!-- 2020-10-20 -->
# V1.1.41 版本更新日志

### 缺陷修复
* 修复新用户未同步情况下进入权限中心异常的问题
* 修复新用户未同步情况下授权 API 出错的问题

---

<!-- 2020-10-14 -->
# V1.1.40 版本更新日志

### 功能优化
* 拓扑实例搜索前端优化错误提示
* 移除资源实例粘贴功能

---

<!-- 2020-10-01 -->
# V1.1.39 版本更新日志

### 功能优化
* 重构优化错误异常模块
* 拓扑实例搜索前端显示细节优化

---

<!-- 2020-09-28 -->
# V1.1.38 版本更新日志

### 新增功能
* 支持拓扑实例的搜索

### 功能优化
* 同步组织架构分布式锁失败提示失败并记录日志

### 缺陷修复
* 修复同步组织架构分页获取部门和用户时由于排序问题导致拉取不全的问题

---

<!-- 2020-09-25 -->
# V1.1.37 版本更新日志

### 功能优化
* 调用接入系统资源查询相关接口异常错误提示和日志优化

### 缺陷修复
* 修复新建关联属性授权不生效问题

---

<!-- 2020-09-23 -->
# V1.1.36 版本更新日志

### 新增功能
* 增加资源实例粘贴功能

### 功能优化
* 拓扑实例选择面板支持拖动
* 实例视图仅有一个时无需下拉列表

### 缺陷修复
* 修复拓扑实例选择时不带子级资源无限制问题

---

<!-- 2020-09-18 -->
# V1.1.35 版本更新日志

### 更新
* [ 修复 ] 新建关联权限, 实例名称显示错误bug
* [ 优化 ] 接入系统回调错误信息优化

### 功能
* [ 功能 ] 新增用户组成员匹配添加功能

---

<!-- 2020-09-14 -->
# V1.1.34 版本更新日志

### 修复
* [ 修复 ] 我的权限-加入用户组时间错误
* [ 修复 ] 申请或配置权限页面 - 时间选择自定义时icon与文字重叠问题

---

<!-- 2020-09-10 -->
# V1.1.33 版本更新日志

### 新增
* [ 新增 ] 我的权限页面用户组权限增加组成员的显示

---

<!-- 2020-09-08 -->
# V1.1.32 版本更新日志

### 新增
* [ 新增 ] 新建关联支持资源属性授权

---

<!-- 2020-09-07 -->
# V1.1.31 版本更新日志

### 新增
* [ 新增 ] `资源实例申请/授权增加实例个数限制`

---

<!-- 2020-06-22 -->
# V1.1.1 版本更新日志

### 新增
* [ 新增 ] `资源选择的实例视图支持配置忽略路径`

> 支持资源配置权限时忽略路径，用于仅仅鉴权资源的 ID

---

<!-- 2020-06-19 -->
# V1.1.0 版本更新日志

## 权限中心 V3 版 V1.1.0 上线！

### 新增

* [ 新增 ] `权限申请` 按用户场景，支持按权限模板申请、加入用户组、自定义申请功能：

> `按权限模板申请` 用户需要单个系统角色权限时，用户可以直接搜索需要权限模板申请，无需再关联实例
>
> `加入用户组` 用户需要跨多个系统的权限时，可以通过加入用户组快速获得需要的权限
>
> `自定义申请` 自定义申请权限是高级功能，用户可以随意勾选申请需要的权限
>
> - 支持已有权限的回显
> - 支持权限变更差异对比
> - 支持拓扑选择实例
> - 支持属性过滤实例

* [ 新增 ] `我的权限`

> 个人所有权限的展示，包括自定义申请的权限、通过权限模板申请的权限、加入用户组的权限、继承组织的权限
>
> 支持实例权限的回收
>
> 支持退出用户组

* [ 新增 ] `我的申请`

> 个人所有发起过的申请单据

* [ 新增 ] `我的审批`

> 个人需要审批的所有单据

* [ 新增 ] `权限模板`

> V3 版的权限模板是实例化后的模板实例，权限模板的变更也可以同步到已授权用户

* [ 新增 ] `用户/组织权限管理`

> 管理员可以通过组织架构管理用户或者组织的权限

* [ 新增 ] `用户组`

> 用户组关联权限模板，用户组可以选择同步被更新的权限模板
>
> 用户组可以添加用户或组织，组内用户会继承用户组的权限

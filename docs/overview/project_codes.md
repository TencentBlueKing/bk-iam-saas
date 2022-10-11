# 蓝鲸权限中心代码结构

bk-iam SaaS源码目录:

```
iam_app
├── LICENSE.txt                    license
├── docs                           文档
├── frontend                       前端文件
├── saas                           SaaS文件
│   ├── Makefile                   make 生成国际化文件
│   ├── backend
│   │   ├── account
│   │   ├── api                    open api代码
│   │   ├── apps                   Django app代码
│   │   │   ├── action
│   │   │   ├── application
│   │   │   ├── approval
│   │   │   ├── group
│   │   │   ├── model_builder
│   │   │   ├── organization
│   │   │   ├── policy
│   │   │   ├── resource
│   │   │   ├── role
│   │   │   ├── subject
│   │   │   ├── system
│   │   │   ├── template
│   │   │   └── user
│   │   ├── audit                  审计代码
│   │   ├── biz                    Biz业务层
│   │   ├── common                 通用模块
│   │   ├── component              依赖组件封装
│   │   ├── debug                  debug模块
│   │   ├── healthz                healthz模块
│   │   ├── long_task              long_task模块
│   │   ├── plugins                plugins模块
│   │   ├── service                Service层
│   │   ├── util                   util模块
│   │   └── version_log            版本日志模块
│   ├── blueapps
│   ├── blueking
│   ├── build                      封包文件
│   ├── config                     配置文件
│   ├── manage.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   ├── release.md
│   ├── requirements.txt           依赖包
│   ├── requirements_dev.txt
│   ├── resources
│   │   ├── locale                 国际化文件
│   │   ├── templates              html模板文件
│   │   └── version_log            版本日志文件
│   ├── runtime.txt
│   ├── settings.py
│   ├── tests
│   ├── urls.py
│   └── wsgi.py
├── readme.md
├── readme_en.md
```

SaaS代码分层:

```
        -----------------
        |  Django apps  |
        -----------------
                ↓
        -----------------
        |      Biz      |
        -----------------
                ↓
        -----------------
        |    Service    |
        -----------------
                ↓
-----------------    -----------------
|   component   |    | Django Models |
-----------------    -----------------
```

分层职责：

1. Django apps
   - 负责api的数据检查
   - 鉴权准入规则/白名单校验
   - 调用biz完成业务任务
2. Biz
   - 负责对接业务场景的逻辑处理
   - 负责业务场景下的Check操作
   - 负责入口数据到Biz模型的转换
   - 负责构造Service的数据并调用Sevice提供的方法完成业务逻辑
   - 负责组合Service的数据模型向View提供Biz的模型数据
   - 负责单一场景的与Service无关的业务逻辑
3. Service
   - 负责模块领域内的CURD操作
   - 对接component与Django Models

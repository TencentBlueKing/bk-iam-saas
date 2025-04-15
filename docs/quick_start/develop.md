# SaaS本地开发环境搭建

## 部署蓝鲸社区版

权限中心 SaaS 的登录鉴权依赖于蓝鲸智云PaaS平台，所以你需要部署蓝鲸PaaS平台和蓝鲸配置平台，作为开发联调环境。

1）如果你只需要定制开发权限中心，不需要改动蓝鲸PaaS和蓝鲸配置平台的源码，建议你直接从官方下载蓝鲸智云社区版完整包进行。
- [下载网址](https://bk.tencent.com/download/)
- [部署指南](https://docs.bk.tencent.com/bkce_install_guide/)
- [产品论坛](https://bk.tencent.com/s-mart/community)
- QQ交流群:495299374

2）权限中心 SaaS 用户管理功能依赖于蓝鲸用户管理，权限申请单据审批依赖于蓝鲸流程服务。
- [蓝鲸用户管理](https://github.com/TencentBlueKing/bk-user)
- [蓝鲸流程服务](https://github.com/TencentBlueKing/bk-itsm)

3）权限中心 SaaS 依赖于蓝鲸权限中心后台。
- [蓝鲸权限中心后台](https://github.com/TencentBlueKing/bk-iam)

## 准备本地 rabbitmq 资源
在本地安装 rabbitmq，并启动 rabbitmq-server，服务监听的端口保持默认（5672）。


## 准备本地 redis 资源
在本地安装 redis，并启动 redis-server，服务监听的端口保持默认（6379）。


## 准备本地 mysql
在本地安装 mysql，并启动 mysql-server，服务监听的端口保持默认（3306）。


## 安装 python 和依赖库
在本地安装 python3.6.7 和 pip，通过 git 拉取源代码到工程目录后，并进入saas目录下运行 pip 命令安装 python 包。
```bash

# linux macos 下
make init

# windows 下
pip install -U pip setuptools
pip install -U pip setuptools
pip install poetry
poetry install
pip install pre-commit
pre-commit install
```


## 环境配置及数据库准备

1) 在执行任何 django `manage.py` 命令时，需要保证环境中有以下环境变量

```
export APP_ID="bk_iam"
export APP_TOKEN="{你的权限中心应用 TOKEN}"
export BK_PAAS_HOST="{开发环境 PAAS 域名}"  # 蓝鲸智云开发者中心的域名，形如：http://paas.bking.com
export APP_URL="{你的权限中心访问域名}"      # 蓝鲸智权限中心的域名，形如：http://iam.bking.com:8000
export BKAPP_ENABLE_PYINSTRUMENT="true"
export MYSQL_NAME="bk_iam"
export MYSQL_USER="root"
export MYSQL_PASSWORD=""
export MYSQL_HOST="localhost"
export MYSQL_PORT=3306
export REDIS_HOST="localhost"                        # redis host
export REDIS_PORT=6379                               # redis port
export REDIS_PASSWORD=""                             # redis password
export REDIS_DB=0                                    # redis db
export BROKER_URL="amqp://guest:guest@localhost:5672//"
export BK_IAM_V3_INNER_HOST="http://127.0.0.1:9000"  # 权限中心后台地址
```

或者在config目录下新增.env文件, 写入变量, 程序启动时会自动加载:

```
APP_ID="bk_iam"
APP_TOKEN="{你的权限中心应用 TOKEN}"
BK_PAAS_HOST="{开发环境 PAAS 域名}"  # 蓝鲸智云开发者中心的域名，形如：http://paas.bking.com
APP_URL="{你的权限中心访问域名}"      # 蓝鲸智权限中心的域名，形如：http://iam.bking.com:8000
BKAPP_ENABLE_PYINSTRUMENT="true"
MYSQL_NAME="bk_iam"
MYSQL_USER="root"
MYSQL_PASSWORD=""
MYSQL_HOST="localhost"
MYSQL_PORT=3306
REDIS_HOST="localhost"                        # redis host
REDIS_PORT=6379                               # redis port
REDIS_PASSWORD=""                             # redis password
REDIS_DB=0                                    # redis db
BROKER_URL="amqp://guest:guest@localhost:5672//"
BK_IAM_V3_INNER_HOST="http://127.0.0.1:9000"  # 权限中心后台地址
```


## 创建并初始化数据库

1) 在 mysql 中创建名为 bk_iam 的数据库
```sql
CREATE DATABASE `bk_iam` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

2) 在工程目录下执行以下命令初始化数据库
```bash
python manage.py migrate
```


## 配置本地 hosts
windows: 在 `C:\Windows\System32\drivers\etc\host` 文件中添加`127.0.0.1 {IAM_APP_HOST}`，比如： iam.bking.com。

mac: 执行 `sudo vim /etc/hosts`，添加`127.0.0.1 {IAM_APP_HOST}`。


## 启动进程
```bash
python manage.py celery worker -l info -B
python manage.py celery beat -l info
python manage.py runserver 8000
```


## 访问页面
使用浏览器开发 `http://{IAM_APP_HOST}:8000/` 访问应用。


# 前端本地开发环境搭建

## 安装 nodejs 和依赖库
在本地安装 nodejs 和 npm（nodejs 版本建议 >= 10.13.0），通过 git 拉取源代码到工程目录后，并进入frontend目录下运行 npm 命令安装 nodejs 依赖包。
```bash
npm install .
```


## 创建本地开发的渲染页面 `index-dev.html`
参照 `index-dev.html.example` 创建 `index-dev.html` 文件。

**`BK_PAAS_HOST`, `LOGIN_SERVICE_URL`, `AJAX_URL_PREFIX` 按照实际部署情况填写（其他配置无需改变）**


## 配置本地 hosts
windows: 在 `C:\Windows\System32\drivers\etc\host` 文件中添加 `127.0.0.1 {IAM_FRONTEND_HOST}`，比如: iam-frontend.bking.com

mac: 执行 `sudo vim /etc/hosts`，添加 `127.0.0.1 {IAM_FRONTEND_HOST}`


## 启动进程
```bash
npm run dev
```


## 访问页面
使用浏览器开发 `http://{IAM_FRONTEND_HOST}:8001/` 访问应用。

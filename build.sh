#!/usr/bin/env bash

# build frontend
cd /app/frontend

npm install . && npm run build:ee

# build saas src
cd /app

mv "/app/saas/resources/bk_iam.png" "/app/logo.png"
mv "/app/saas/resources/app.yml" "/app/"
mkdir -p "/app/saas/staticfiles"

mv /app/frontend/dist/static/* "/app/saas/staticfiles/"

mv "/app/frontend/dist/index.html" "/app/saas/resources/templates/"
mv "/app/frontend/dist/login_success.html" "/app/saas/resources/templates/"

ls -al "/app/saas/staticfiles"
ls -al "/app/saas/resources/templates"

# requestment.txt 对每个包 去除platform和markers
sed -i 's/;.*//' "/app/saas/requirements.txt"

# 修改index.html的title
sed -i "s/https:\/\/bk.tencent.com\/docs\//https:\/\/bk.tencent.com\/docs\/markdown/" "/app/saas/resources/templates/index.html"

cd "/app/saas/"
# 更新app.yml里的版本号
sed -i "s/__APP_VERSION__/$(head -1 VERSION)/" ../app.yml
# 删除敏感信息文件
rm -rf config/dev.py
# 删除test文件
rm -rf tests
# 改名
cd "/app"
mv saas src
shopt -s extglob
rm -rf !(src|app.yml|logo.png)

echo "show all files"
ls -al "/app/"

echo "show all source files"
ls -al "/app/src"

cat "/app/app.yml"
cat "/app/src/requirements.txt"

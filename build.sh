#!/usr/bin/env bash

# build frontend
echo "Building frontend..."

cd /app/frontend || exit 1

npm install . && npm run build:ee
if [ $? -ne 0 ]
then
    echo "build frontend failed!"
    exit 1
fi

echo "build frontend success!"

# build saas src
echo "Building saas src..."

cd /app

mv "/app/saas/resources/bk_iam.png" "/app/logo.png" || exit 1
mv "/app/saas/resources/app.yml" "/app/" || exit 1
mkdir -p "/app/saas/staticfiles"

mv /app/frontend/dist/static/* "/app/saas/staticfiles/" || exit 1

mv "/app/frontend/dist/index.html" "/app/saas/resources/templates/" || exit 1
mv "/app/frontend/dist/login_success.html" "/app/saas/resources/templates/" || exit 1

ls -al "/app/saas/staticfiles" || exit 1
ls -al "/app/saas/resources/templates" || exit 1

# 修改index.html的文档地址
sed -i "s/https:\/\/bk.tencent.com\/docs\//https:\/\/bk.tencent.com\/docs\/markdown/" "/app/saas/resources/templates/index.html"

cd "/app/saas/" || exit 1
# 更新app.yml里的版本号
sed -i "s/__APP_VERSION__/$(head -1 VERSION)/" ../app.yml || exit 1
# 删除test文件
rm -rf tests || exit 1
# 改名
cd /app
mv saas src
shopt -s extglob
rm -rf !(src|app.yml|logo.png)
echo "build saas src success!"

echo "show all files"
ls -al "/app/"

echo "show all source files"
ls -al "/app/src"

cat "/app/app.yml"

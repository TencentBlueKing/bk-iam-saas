/*
 * Tencent is pleased to support the open source community by making
 * 蓝鲸智云-权限中心(BlueKing-IAM) available.
 *
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 *
 * 蓝鲸智云-权限中心(BlueKing-IAM) is licensed under the MIT License.
 *
 * License for 蓝鲸智云-权限中心(BlueKing-IAM):
 *
 * ---------------------------------------------------
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 * to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
 * the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 * THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
*/

/**
 * @file prod server
 * 静态资源
 * 模块渲染输出
 * 注入全局变量
 * 添加html模板引擎
 */
import express from 'express';
import path from 'path';
import artTemplate from 'express-art-template';
import history from 'connect-history-api-fallback';
import cookieParser from 'cookie-parser';
import axios from 'axios';
import ajaxMiddleware from './ajax-middleware';
import config from './config';

// eslint-disable-next-line new-cap
const app = new express();
const PORT = process.env.PORT || config.build.localDevPort || 5000;
const http = axios.create({
  withCredentials: true
});

http.interceptors.response.use(response => response, error => Promise.reject(error));

// 注入全局变量
const GLOBAL_VAR = {
  LOGIN_SERVICE_URL: process.env.LOGIN_SERVICE_URL || '',
  AJAX_URL_PREFIX: process.env.AJAX_URL_PREFIX || '',
  SITE_URL: process.env.SITE_URL || '',
  STATIC_URL: process.env.STATIC_URL || '',
  BK_PAAS_HOST: process.env.BK_PAAS_HOST || '',
  CSRF_COOKIE_NAME: process.env.CSRF_COOKIE_NAME || '',
  SESSION_COOKIE_DOMAIN: process.env.SESSION_COOKIE_DOMAIN || '',
  BK_ITSM_APP_URL: process.env.BK_ITSM_APP_URL || '',
  ENABLE_MODEL_BUILD: process.env.ENABLE_MODEL_BUILD || '',
  ENABLE_PERMISSION_HANDOVER: process.env.ENABLE_PERMISSION_HANDOVER || '',
  ENABLE_TEMPORARY_POLICY: process.env.ENABLE_TEMPORARY_POLICY || '',
  BK_COMPONENT_API_URL: process.env.BK_COMPONENT_API_URL || ''
};

// APA 重定向回首页，由首页Route响应处理
// https://github.com/bripkens/connect-history-api-fallback#index
app.use(history({
  index: '/',
  rewrites: [
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容 /cs/28aa9eda67644a6eb254d694d944307e/cluster/BCS-MESOS-10001/node/127.0.0.1 这样以 IP 结尾的 url
      // from: /\d+\.\d+\.\d+\.\d+$/,
      from: /\/(\d+\.)*\d+$/,
      to: '/'
    },
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容 /bcs/projectId/app/214/taskgroups/0.application-1-13.test123.10013.151080613/containers/containerId
      from: /\/\/+.*\..*\//,
      to: '/'
    },
    {
      from: '/login_success/',
      to: '/login_success/'
    }
  ]
}));

app.use(cookieParser());

// 首页
app.get('/', (req, res) => {
  const index = path.join(__dirname, '../dist/index.html');
  res.render(index, GLOBAL_VAR);
});
app.get('/login_success/', (req, res) => {
  const loginSuccess = path.join(__dirname, '../dist/login_success.html');
  res.render(loginSuccess, GLOBAL_VAR);
});

app.use(ajaxMiddleware);
// 配置静态资源
app.use('/static', express.static(path.join(__dirname, '../dist/static')));

// 配置视图
app.set('views', path.join(__dirname, '../dist'));

// 配置模板引擎
// http://aui.github.io/art-template/zh-cn/docs/
app.engine('html', artTemplate);
app.set('view engine', 'html');

// 配置端口
app.listen(PORT, () => {
  console.log(`App is running in port ${PORT}`);
});

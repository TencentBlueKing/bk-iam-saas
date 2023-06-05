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

import path from 'path';
import fs from 'fs';
import url from 'url';
import queryString from 'querystring';
import chalk from 'chalk';
import devEnv from './dev.env';

const mockReqHandler = (req, mockParamValue) => {
  // mockFile replace 去掉 最后的 /，例如 /a/b/c/ => /a/b/c
  const mockFilePath = path.join(__dirname, '../mock/ajax', mockParamValue.replace(/\/+$/, '')) + '.js';
  if (!fs.existsSync(mockFilePath)) {
    return false;
  }

  console.log(chalk.magenta('Mock File Query: ', mockParamValue));
  console.log(chalk.magenta('Mock File Path: ', mockFilePath));

  delete require.cache[require.resolve(mockFilePath)];
  return require(mockFilePath);
};

export default async function ajaxMiddleWare (req, res, next) {
  // eslint-disable-next-line node/no-deprecated-api
  let query = url.parse(req.url).query;

  if (!query) {
    return next();
  }

  query = queryString.parse(query);

  const mockParamValue = query[JSON.parse(devEnv.AJAX_MOCK_PARAM)];
  // 不是 mock 请求
  if (!mockParamValue) {
    return next();
  } else {
    const postData = req.body || '';
    const mockDataHandler = mockReqHandler(req, mockParamValue);

    if (!mockDataHandler) {
      res.status(404).end();
      return;
    }

    let data = await mockDataHandler.response(query, postData, req);

    if (data.statusCode) {
      res.status(data.statusCode).end(JSON.stringify(data));
      return;
    }

    let contentType = req.headers['Content-Type'];

    // 返回值未指定内容类型，默认按 JSON 格式处理返回
    if (!contentType) {
      contentType = 'application/json;charset=UTF-8';
      req.headers['Content-Type'] = contentType;
      res.setHeader('Content-Type', contentType);
      data = JSON.stringify(data || {});
    }

    res.end(data);

    return next();
  }
}

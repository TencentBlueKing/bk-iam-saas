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

import Vue from 'vue';
// import bkMagic from 'bk-magic-vue'
// Vue.use(bkMagic)

// 全量引入
import './fully-import';

// 按需引入
// import './demand-import'

const Message = Vue.prototype.$bkMessage;

let messageInstance = null;

export const messageError = (message, delay = 3000, ellipsisLine = 1) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    limit: 1,
    message,
    delay,
    theme: 'error',
    ellipsisLine,
    ellipsisCopy: true
  });
};

export const messageSuccess = (message, delay = 3000, ellipsisLine = 1) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    limit: 1,
    message,
    delay,
    theme: 'success',
    ellipsisLine
  });
};

export const messageInfo = (message, delay = 3000) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    limit: 1,
    message,
    delay,
    theme: 'primary'
  });
};

export const messageWarn = (message, delay = 3000, ellipsisLine = 3) => {
  messageInstance && messageInstance.close();
  messageInstance = Message({
    limit: 1,
    message,
    delay,
    theme: 'warning',
    hasCloseIcon: true,
    ellipsisLine
  });
};

// message高阶用法

export const messageAdvancedError = (details, delay = 8000, ellipsisLine = 3, externalMsg = '') => {
  // 区分内外部链接
  let linkContent = {
    url: ''
  };
  const isTencent = window.ENABLE_ASSISTANT.toLowerCase() === 'true';
  const linkMap = {
    true: () => {
      linkContent = Object.assign(linkContent, {
        url: 'wxwork://message/?username=BK助手'
      });
    },
    false: () => {
      linkContent = Object.assign(linkContent, {
        url: 'https://wpa1.qq.com/KziXGWJs?_type=wpa&qidian=true'
      });
    }
  };
  linkMap[isTencent]();
  const { code, data, message, statusText, response } = details;
  let errCode = null;
  const errMsg = externalMsg || (message || data.msg || statusText);
  if (![null, undefined].includes(code)) {
    errCode = code;
  }
  if (response && response.data) {
    errCode = response.data.code;
  }
  const messageDetail = {
    code: errCode,
    overview: errMsg,
    suggestion: '',
    details: errMsg,
    assistant: linkContent.url
  };
  messageInstance && messageInstance.close();
  messageInstance = Message({
    limit: 1,
    message: messageDetail,
    delay,
    theme: 'error',
    ellipsisCopy: true,
    ellipsisLine
  });
};

Vue.prototype.messageError = messageError;
Vue.prototype.messageSuccess = messageSuccess;
Vue.prototype.messageInfo = messageInfo;
Vue.prototype.messageWarn = messageWarn;
Vue.prototype.messageAdvancedError = messageAdvancedError;

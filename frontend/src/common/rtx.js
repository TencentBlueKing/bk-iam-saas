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
import store from '@/store';

let callbackSeed = 0;
// 是否存在多租户
const isExistTenant = !!store.state.user.tenant_id;
const webUrl = window.BK_USER_WEB_APIGW_URL.endsWith('/') ? window.BK_USER_WEB_APIGW_URL.slice(0, -1) : window.BK_USER_WEB_APIGW_URL;
const api = isExistTenant ? `${webUrl}/api/v3/open-web/tenant/users/-/search/` : window.BK_USER_API;
function JSONP (params = {}, options = {}) {
  return new Promise((resolve, reject) => {
    let timer;
    const callbackName = `USER_LIST_CALLBACK_${callbackSeed++}`;
    window[callbackName] = response => {
      timer && clearTimeout(timer);
      document.body.removeChild(script);
      delete window[callbackName];
      resolve(response);
    };
    const script = document.createElement('script');
    script.onerror = event => {
      document.body.removeChild(script);
      delete window[callbackName];
      // eslint-disable-next-line
            reject('Get user list failed.')
    };
    const query = [];
    for (const key in params) {
      query.push(`${key}=${params[key]}`);
    }
    script.src = `${api}?${query.join('&')}&callback=${callbackName}`;
    if (options.timeout) {
      setTimeout(() => {
        document.body.removeChild(script);
        delete window[callbackName];
        // eslint-disable-next-line
                reject('Get user list timeout.')
      }, options.timeout);
    }
    document.body.appendChild(script);
  });
}

export async function fuzzyRtxSearch (keyword, options) {
  if (isExistTenant) {
    try {
      if (!keyword) {
        return {
          count: 0,
          results: []
        };
      }
      const res = await store.dispatch('tenantConfig/getTenantUserSelector', { keyword });
      (res.data || []).forEach(item => {
        item.name = item.display_name || item.bk_username;
        item.id = item.bk_username;
      });
      return {
        count: res.data.length || 0,
        results: res.data || []
      };
    } catch {
      return {
        count: 0,
        results: []
      };
    }
  } else {
    const requestParams = {
      fuzzy_lookups: keyword,
      app_code: 'bk-magicbox',
      page_size: 100,
      page: 1
    };
    const data = {};
    try {
      const response = await JSONP(requestParams, options);
      data.count = response.data.count;
      data.results = response.data.results || [];
      data.results.forEach(item => {
        item.name = item.display_name ? `${item.username}(${item.display_name})` : item.username;
        item.id = item.username;
      });
      if (response.code !== 0) {
        throw new Error(response);
      }
    } catch (error) {
      data.count = 0;
      data.results = [];
    }
    return data;
  }
}

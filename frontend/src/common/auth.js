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

import _ from 'lodash';
import store from '@/store';

const ANONYMOUS_USER = {
  id: null,
  isAuthenticated: false,
  username: 'anonymous',
  avatarUrl: null,
  chineseName: 'anonymous',
  phone: null,
  email: null
};

let currentUser = {
  avatar_url: '',
  bkpaas_user_id: '',
  chinese_name: '',
  username: ''
};

/**
 * 转换 user 对象，注意 camelCase
 *
 * @param {Object} data 待转换的对象
 *
 * @return {Object} 结果
 */
const transformUserData = data => {
  const user = {};
  Object.keys(data).forEach((key, index) => {
    const value = data[key];
    key = _.camelCase(key);
    user[key] = value;
  });
  return user;
};

export default {
  /**
     * 未登录状态码
     */
  HTTP_STATUS_UNAUTHORIZED: 401,

  /**
     * 获取当前用户
     *
     * @return {Object} 当前用户信息
     */
  getCurrentUser () {
    return currentUser;
  },

  /**
     * 跳转到登录页
     */
  redirectToLogin () {
    const LOGIN_SERVICE_URL = window.LOGIN_SERVICE_URL;
    window.location.href = LOGIN_SERVICE_URL + '/?c_url=' + encodeURIComponent(window.location.href);
  },

  /**
     * 请求当前用户信息
     *
     * @return {Promise} promise 对象
     */
  requestCurrentUser () {
    let promise = null;
    if (currentUser.bkpaas_user_id) {
      promise = new Promise((resolve, reject) => {
        const user = transformUserData(currentUser);
        if (user.code && user.code === 'Unauthorized') {
          user.isAuthenticated = false;
        } else {
          user.isAuthenticated = true;
        }
        resolve(user);
      });
    } else {
      if (!store.getters.user || !Object.keys(store.getters.user).length) {
        const req = store.dispatch('userInfo', { cancelWhenRouteChange: false });
        promise = new Promise((resolve, reject) => {
          req.then(resp => {
            const user = transformUserData(resp);
            if (user.code && user.code === 'Unauthorized') {
              user.isAuthenticated = false;
            } else {
              user.isAuthenticated = true;
            }

            // 存储当前用户信息(全局)
            currentUser = store.getters.user;
            resolve(user);
          }, err => {
            if (err.response.status === this.HTTP_STATUS_UNAUTHORIZED || err.crossDomain) {
              resolve({ ...ANONYMOUS_USER });
            } else {
              reject(err);
            }
          });
        });
      }
    }

    return promise;
  }
};

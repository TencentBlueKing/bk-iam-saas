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

import http from '@/api';

const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;

export default {
  namespaced: true,
  state: {},
  getters: {},
  mutations: {},
  actions: {
    /**
         * 获取超级管理员的通知配置
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    getSuperNoticeConfig ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/notification_config/`, config);
    },

    /**
         * 更新超级管理员的通知配置
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    updateSuperNoticeConfig ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/notification_config/`, params, config);
    }
  }
};

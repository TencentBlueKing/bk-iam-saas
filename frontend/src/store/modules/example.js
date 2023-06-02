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
import { json2Query } from '@/common/util';

export default {
  namespaced: true,
  state: {
  },
  mutations: {
  },
  actions: {
    // 待审批列表
    getWaitApproval ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=getWaitApproval`, params, config);
    },
    // 审批记录
    getApprovalRecord ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=getApprovalRecord`, params, config);
    },
    // 审批记录
    getApprovalDetail ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=getApprovalDetail`, params, config);
    },
    /**
         * enterExample1 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    enterExample1 ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=enterExample1&${json2Query(params)}`, config);
    },

    /**
         * enterExample2 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    enterExample2 ({ commit, state, dispatch }, params, config) {
      return http.post(`/app/index?invoke=enterExample2`, params, config);
    },

    /**
         * btn1 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    btn1 ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=btn1`, params, config);
    },

    /**
         * btn2 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    btn2 ({ commit, state, dispatch }, params, config) {
      return http.post(`/app/index?invoke=btn2`, params, config);
    },

    /**
         * del 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 参数
         *
         * @return {Promise} promise 对象
         */
    del ({ commit, state, dispatch }, params, config) {
      return http.delete(`/app/index?invoke=del`, { data: params }, config);
    },

    /**
         * same 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    same ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=same&${json2Query(params)}`, config);
    },

    /**
         * go 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    go ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=go&${json2Query(params)}`, config);
    },

    /**
         * same post 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    postSame ({ commit, state, dispatch }, params, config) {
      return http.post(`/app/index?invoke=postSame`, params, config);
    },

    /**
         * get 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    get ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=get&${json2Query(params)}`, config);
    },

    /**
         * post 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    post ({ commit, state, dispatch }, params, config) {
      return http.post(`/app/index?invoke=post`, params, config);
    },

    /**
         * long 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    long ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=long&${json2Query(params)}`, config);
    },

    /**
         * long1 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    long1 ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=long1&${json2Query(params)}`, config);
    }
  }
};

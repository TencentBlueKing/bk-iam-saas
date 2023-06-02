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

const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;

export default {
  namespaced: true,
  state: {},
  getters: {},
  mutations: {},
  actions: {
    /**
         * 获取审批列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    getApprovalList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/approvals/?${json2Query(params)}`, config);
    },

    /**
         * 单据审批
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
    approvalAction ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/approvals/approve/`, params, config);
    },

    /**
         * 获取审批流程列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    getProcessesList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/approvals/processes/?${json2Query(params)}`, config);
    },

    /**
         * 获取操作的审批流程列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    getActionProcessesList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/approvals/processes/actions/?${json2Query(params)}`, config);
    },

    /**
         * 设置操作的审批流程
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    updateActionProcesses ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/approvals/processes/actions/`, params, config);
    },

    /**
         * 获取用户组的审批流程列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    getGroupProcessesList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/approvals/processes/groups/?${json2Query(params)}`, config);
    },

    /**
         * 设置用户组的审批流程
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    updateGroupProcesses ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/approvals/processes/groups/`, params, config);
    },

    /**
         * 获取操作分组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    getActionGroups ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/actions/action_groups/?${json2Query(params)}`, config);
    },

    /**
         * 获取默认审批流程配置
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         *
         * @return {Promise} promise 对象
         */
    getDefaultProcesses ({ commit, state, dispatch }, config) {
      return http.get(`${AJAX_URL_PREFIX}/approvals/processes/global_config/`, config);
    },

    /**
         * 批量设置操作的审批流程
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    updateDefaultProcesses ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/approvals/processes/global_config/`, params, config);
    }
  }
};

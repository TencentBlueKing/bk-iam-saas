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
  state: {
    // 右侧整块的 loading
    rightLoading: false,
    // 右侧切换 tab 的 loading
    toggleTabLoading: false
  },
  getters: {
    rightLoading: state => state.rightLoading,
    toggleTabLoading: state => state.toggleTabLoading
  },
  mutations: {
    /**
         * 更新 store.rightLoading
         *
         * @param {Object} state store state
         * @param {Boolean} rightLoading rightLoading 值
         */
    updateRightLoading (state, rightLoading) {
      state.rightLoading = rightLoading;
    },
    /**
         * 更新 store.toggleTabLoading
         *
         * @param {Object} state store state
         * @param {Boolean} toggleTabLoading toggleTabLoading 值
         */
    updateToggleTabLoading (state, toggleTabLoading) {
      state.toggleTabLoading = toggleTabLoading;
    }
  },
  actions: {
    /**
         * 获取目录列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {String} departmentId departmentId 参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getCategories ({ commit, state, dispatch }, config = {}) {
      return http.get(`${AJAX_URL_PREFIX}/organizations/categories/`, {}, config);
    },

    /**
         * 获取组织架构
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params { departmentId } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getOrganizations ({ commit, state, dispatch }, { departmentId }, config = {}) {
      return http.get(`${AJAX_URL_PREFIX}/organizations/departments/${departmentId}/`, {}, config);
    },

    /**
         * 组织架构搜索
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getSearchOrganizations ({ commit, state, dispatch }, params, config = {}) {
      return http.get(`${AJAX_URL_PREFIX}/organizations/search/?${json2Query(params)}`, {}, config);
    },

    /**
         * 获取subject有权限的所有系统列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @return {Promise} promise 对象
         */
    getSubjectHasPermSystem ({ commit, state, dispatch }, params, config) {
      const subjectType = params.subjectType;
      const subjectId = params.subjectId;
      return http.get(`${AJAX_URL_PREFIX}/subjects/${subjectType}/${subjectId}/systems/`, config);
    },

    /**
         * 获取subject有临时权限的所有系统列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @return {Promise} promise 对象
         */
    getSubjectTemporaryHasPermSystem ({ commit, state, dispatch }, params, config) {
      const subjectType = params.subjectType;
      const subjectId = params.subjectId;
      return http.get(`${AJAX_URL_PREFIX}/subjects/${subjectType}/${subjectId}/temporary_policies/systems/`, config);
    },

    /**
         * 组织架构执行同步任务
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @return {Promise} promise 对象
         */
    organizationsSyncTask ({ commit, state, dispatch }, config) {
      return http.post(`${AJAX_URL_PREFIX}/organizations/sync_task/`, config);
    },

    /**
         * 组织架构同步状态查询
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @return {Promise} promise 对象
         */
    getOrganizationsSyncTask ({ commit, state, dispatch }, config) {
      return http.get(`${AJAX_URL_PREFIX}/organizations/sync_task/`, config);
    },

    /**
         * 自动输入用户进行校验
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @return {Promise} promise 对象
         */
    verifyManualUser ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/organizations/users/query/`, params, config);
    },

    /**
         * 获取同步记录
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @return {Promise} promise 对象
         */
    getRecordsList ({ commit, state, dispatch }, params, config = {}) {
      return http.get(`${AJAX_URL_PREFIX}/organizations/sync_records/?${json2Query(params)}`, {}, config);
    },
    /**
         * 获取日志详情
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @return {Promise} promise 对象
         */
    getRecordsLog ({ commit, state, dispatch }, id, config) {
      return http.get(`${AJAX_URL_PREFIX}/organizations/sync_records/${id}/logs/`, config);
    },
    /**
         * 校验组织架构选择器部门/用户范围是否满足条件
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @return {Promise} promise 对象
         */
    getSubjectScopeCheck ({ commit, state, dispatch }, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/subject_scope_check/`, config);
    }
  }
};

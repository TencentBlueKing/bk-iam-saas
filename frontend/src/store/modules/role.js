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
  mutations: {},
  actions: {
    /**
         * 获取管理空间列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getRatingManagerList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/grade_managers/?${json2Query(params)}`, config);
    },

    /**
         * 创建管理空间
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addRatingManager ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/grade_managers/`, params, config);
    },

    /**
         * 获取管理空间详情
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params { id } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getRatingManagerDetail ({ commit, state, dispatch }, { id }, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/grade_managers/${id}/`, config);
    },

    /**
         * 退出角色
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params { id } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deleteRatingManager ({ commit, state, dispatch }, { id }, config) {
      return http.delete(`${AJAX_URL_PREFIX}/roles/${id}/members/`, { data: {} }, config);
    },

    /**
         * 操作聚合
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    actionAggregation ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/actions/aggregation/`, params, config);
    },

    /**
         * 用户角色切换
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    updateCurrentRole ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/accounts/user/roles/`, params, config);
    },

    /**
         * 获取角色的subject授权范围
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getRoleSubjectScope ({ commit, state, dispatch }, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/subject_scope/`, config);
    },

    /**
         * 根据批量username查询用户信息
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    queryRolesUsers ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/users/query/`, params, config);
    },

    /**
         * 获取超级管理员成员列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getSuperManager ({ commit, state, dispatch }, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/super_manager/members/`, config);
    },

    /**
         * 添加超级管理员成员列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addSuperManager ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/super_manager/members/`, params, config);
    },

    /**
         * 修改超级管理员成员拥有的权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    editSuperManager ({ commit, state, dispatch }, params, config) {
      return http.put(`${AJAX_URL_PREFIX}/roles/super_manager/members/`, params, config);
    },

    /**
         * 删除超级管理员成员
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deleteSuperManager ({ commit, state, dispatch }, params, config) {
      return http.delete(`${AJAX_URL_PREFIX}/roles/super_manager/members/`, { data: params }, config);
    },

    /**
         * 获取系统管理员列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getSystemManager ({ commit, state, dispatch }, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/system_manager/`, config);
    },

    /**
         * 修改系统管理员成员
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    editSystemManagerMember ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.put(`${AJAX_URL_PREFIX}/roles/system_manager/${id}/members/`, requestParams, config);
    },

    /**
         * 修改系统管理员成员拥有的权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    editSystemManagerPerm ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.put(
        `${AJAX_URL_PREFIX}/roles/system_manager/${id}/member_system_permissions/`,
        requestParams,
        config
      );
    },

    /**
         * 编辑管理空间
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    editRatingManager ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.put(`${AJAX_URL_PREFIX}/roles/grade_managers/${id}/`, requestParams, config);
    },

    /**
         * 普通身份创建管理空间
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addRatingManagerWithGeneral ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/grade_manager/`, params, config);
    },

    /**
         * 更新管理空间
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    updateRatingManager ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.patch(`${AJAX_URL_PREFIX}/roles/grade_managers/${id}/`, requestParams, config);
    },

    /**
         * 普通用户编辑管理空间
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    editRatingManagerWithGeneral ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/grade_manager_updated/`, params, config);
    },

    /**
         * 获取角色的成员列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getGradeMembers ({ commit, state, dispatch }, { id }, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/${id}/members/`, config);
    },

    /**
         * 查询授权范围包含用户的角色
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getScopeHasUser ({ commit, state, dispatch }, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/auth_scope_include_user_roles/`, config);
    }
  }
};

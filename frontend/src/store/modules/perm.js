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
    // 切换 tab 的 loading
    toggleTabLoading: false
  },
  getters: {
    toggleTabLoading: state => state.toggleTabLoading
  },
  mutations: {
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
         * 获取用户系统列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getCurrentSystemList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/principals/users/${params.userId}/systems/`, {}, config);
    },

    /**
         * 获取用户部门列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserDepartments ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/principals/users/${params.userId}/departments/`, {}, config);
    },

    /**
         * 获取用户用户组列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserGroups ({ commit, state, dispatch }, params, config) {
      const userId = params.userId;
      delete params.userId;
      return http.get(`${AJAX_URL_PREFIX}/principals/users/${userId}/groups/?${json2Query(params)}`, {}, config);
    },

    /**
         * 获取用户权限列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserPermission ({ commit, state, dispatch }, params, config) {
      const userId = params.userId;
      delete params.userId;
      return http.get(
        `${AJAX_URL_PREFIX}/principals/users/${userId}/permissions/?${json2Query(params)}`,
        {},
        config
      );
    },

    /**
         * 获取用户组权限列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getGroupPermission ({ commit, state, dispatch }, params, config) {
      const groupId = params.group_id;
      delete params.group_id;
      const userId = params.userId;
      delete params.userId;

      const url = userId
        ? `${AJAX_URL_PREFIX}/principals/users/${userId}/groups/${groupId}/permissions/?${json2Query(params)}`
        : `${AJAX_URL_PREFIX}/principals/groups/${groupId}/permissions/?${json2Query(params)}`;
      return http.get(url, {}, config);
    },

    /**
         * 获取用户权限可过滤字段列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserPermissionFilterParamsList ({ commit, state, dispatch }, params, config) {
      const userId = params.userId;
      delete params.userId;
      return http.get(
        `${AJAX_URL_PREFIX}/principals/users/${userId}/permissions/fields/?${json2Query(params)}`,
        {},
        config
      );
    },

    /**
         * 退出用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    quitGroup ({ commit, state, dispatch }, params, config) {
      const userId = params.userId;
      delete params.userId;
      return http.delete(`${AJAX_URL_PREFIX}/principals/users/${userId}/groups/`, { data: params }, config);
    },

    /**
         * 获取用户组织的系统列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getDepartmentSystem ({ commit, state, dispatch }, params, config) {
      const userId = params.userId;
      const departmentId = params.departmentId;
      return http.get(
        `${AJAX_URL_PREFIX}/principals/users/${userId}/departments/${departmentId}/systems/`,
        {},
        config
      );
    },

    /**
         * 获取用户组织权限列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserDepartmentPermission ({ commit, state, dispatch }, params, config) {
      const paramsTemp = Object.assign({}, params);
      const userId = paramsTemp.userId;
      const departmentId = paramsTemp.departmentId;
      delete paramsTemp.userId;
      delete paramsTemp.departmentId;
      return http.get(
        `${AJAX_URL_PREFIX}/principals/users/${userId}/departments/${departmentId}/permissions/?`
                    + json2Query(paramsTemp),
        {},
        config
      );
    },

    /**
         * 获取用户组织的权限可过滤字段列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserDepartmentPermissionFilterParamsList ({ commit, state, dispatch }, params, config) {
      const paramsTemp = Object.assign({}, params);
      const userId = paramsTemp.userId;
      const departmentId = paramsTemp.departmentId;
      delete paramsTemp.userId;
      delete paramsTemp.departmentId;
      return http.get(
        `${AJAX_URL_PREFIX}/principals/users/${userId}/departments/${departmentId}/permissions/fields/?`
                    + json2Query(paramsTemp),
        {},
        config
      );
    },

    /**
         * 删除用户权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    batchDeleteUserPermission ({ commit, state, dispatch }, params, config) {
      const paramsTemp = Object.assign({}, params);
      const userId = paramsTemp.userId;
      delete paramsTemp.userId;
      return http.delete(
        `${AJAX_URL_PREFIX}/principals/users/${userId}/permissions/`,
        { data: paramsTemp },
        config
      );
    },

    /**
         * 模板申请的权限 权限模板列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getPermTemplates ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        // `/app/index?${json2Query(params)}&invoke=getPermTemplates`,
        `${AJAX_URL_PREFIX}/subjects/${params.subjectType}/${params.subjectId}/templates/`,
        {},
        config
      );
    },

    /**
         * 模板详情
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getTemplateDetail ({ commit, state, dispatch }, params = {}, config) {
      const id = params.id;
      delete params.id;
      return http.get(`${AJAX_URL_PREFIX}/templates/${id}/?${json2Query(params)}`, {}, config);
    },

    /**
         * 加入用户组的权限 用户组列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getPermGroups ({ commit, state, dispatch }, params = {}, config) {
      const pageParas = {
        page_size: params.limit,
        page: params.offset
      };
      return http.get(
        // `/app/index?${json2Query(params)}&invoke=getPermGroups`,
        `${AJAX_URL_PREFIX}/subjects/${params.subjectType}/${params.subjectId}/groups/?${json2Query(pageParas)}`,
        config
      );
    },

    /**
         * 加入部门用户组的权限 用户组列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getDepartPermGroups ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        `${AJAX_URL_PREFIX}/subjects/${params.subjectType}/${params.subjectId}/departments/-/groups/`,
        config
      );
    },

    /**
         * 用户组拥有的权限模板列表 权限模板列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getGroupTemplates ({ commit, state, dispatch }, params = {}, config) {
      const id = params.id;
      delete params.id;

      return http.get(
        // `/app/index?${json2Query(params)}&id=${id}&invoke=getGroupTemplates`,
        `${AJAX_URL_PREFIX}/groups/${id}/templates/`,
        {},
        config
      );
    },

    /**
         * 加入用户组的权限 用户组列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getPermOrgs ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        // `/app/index?${json2Query(params)}&invoke=getPermOrgs`,
        `${AJAX_URL_PREFIX}/subjects/${params.subjectType}/${params.subjectId}/departments/`,
        {},
        config
      );
    },

    /**
         * 加入组织的权限 权限模板列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getOrgTemplates ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        // `/app/index?${json2Query(params)}&invoke=getOrgTemplates`,
        `${AJAX_URL_PREFIX}/subjects/${params.subjectType}/${params.subjectId}/templates/`,
        {},
        config
      );
    },

    /**
         * Subject 权限列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getPersonalPolicy ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        `${AJAX_URL_PREFIX}/subjects/${params.subjectType}/${params.subjectId}/policies/?system_id=${params.systemId}`,
        {},
        config
      );
    },

    /**
         * Subject 临时权限列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getTeporaryPersonalPolicy ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        `${AJAX_URL_PREFIX}/subjects/${params.subjectType}/${params.subjectId}/temporary_policies/?system_id=${params.systemId}`,
        {},
        config
      );
    },

    /**
         * 模板申请的权限 脱离模板
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    quitPermTemplates ({ commit, state, dispatch }, params = {}, config) {
      const subjectType = params.subjectType;
      delete params.subjectType;
      const subjectId = params.subjectId;
      delete params.subjectId;

      return http.delete(
        `${AJAX_URL_PREFIX}/subjects/${subjectType}/${subjectId}/templates/?${json2Query(params)}`,
        {},
        config
      );
    },

    /**
         * 加入用户组的权限 退出该组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    quitGroupTemplates ({ commit, state, dispatch }, params = {}, config) {
      const subjectType = params.subjectType;
      delete params.subjectType;
      const subjectId = params.subjectId;
      delete params.subjectId;

      return http.delete(
        `${AJAX_URL_PREFIX}/subjects/${subjectType}/${subjectId}/groups/?${json2Query(params)}`,
        // ?type=group&id=groupid
        {},
        config
      );
    },

    /**
         * 加入用户组的权限 退出该组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    quitGroupPerm ({ commit, state, dispatch }, params = {}, config) {
      return http.delete(
        `${AJAX_URL_PREFIX}/users/groups/?${json2Query(params)}`,
        // ?type=group&id=groupid
        {},
        config
      );
    },

    /**
         * 组织添加权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addDepartTemplates ({ commit, state, dispatch }, params = {}, config) {
      const requestParams = Object.assign({}, params);
      const subjectType = requestParams.subjectType;
      delete requestParams.subjectType;
      const subjectId = requestParams.subjectId;
      delete requestParams.subjectId;

      return http.post(
        `${AJAX_URL_PREFIX}/subjects/${subjectType}/${subjectId}/templates/`,
        requestParams,
        config
      );
    },

    /**
         *  个人用户的项目列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getPersonalProject ({ commit, state, dispatch }, params, config) {
      const { system_id } = params;
      delete params.system_id;
      return http.get(
        // eslint-disable-next-line camelcase
        `${AJAX_URL_PREFIX}/systems/${system_id}/grade_managers/?${json2Query(params)}`,
        {},
        config
      );
    },

    /**
         *  根据角色id和系统id过滤的用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getRoleGroups ({ commit, state, dispatch }, params, config) {
      const { system_id, role_id } = params;
      delete params.system_id;
      delete params.role_id;
      delete params.action_id;
      return http.get(
        // eslint-disable-next-line camelcase
        `${AJAX_URL_PREFIX}/systems/${system_id}/grade_managers/${role_id}/groups/?${json2Query(params)}`,
        {},
        config
      );
    },

    /**
         *  个人用户的项目列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getPersonalGroups ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/users/groups/?${json2Query(params)}`, {}, config);
    },

    /**
         *  所属部门的的用户组列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getDepartMentsPersonalGroups ({ commit, state, dispatch }, params, config) {
      const queryParams = params ? `?${json2Query(params)}` : '';
      return http.get(`${AJAX_URL_PREFIX}/users/departments/-/groups/${queryParams}`, {}, config);
    },

    /**
         * 权限交接
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    permTransfer ({ commit, state, dispatch }, params = {}, config) {
      return http.post(
        `${AJAX_URL_PREFIX}/handover/`,
        params,
        config
      );
    },

    /**
         * 权限交接历史记录
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getTransferHistory ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        `${AJAX_URL_PREFIX}/handover/records/?${json2Query(params)}`,
        // `/handover/records/?mock-file=index&invoke=getTransferHistory`,
        {},
        config
      );
    },

    /**
         * 权限交接历史记录详情
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getTransferHistoryDetail ({ commit, state, dispatch }, params = {}, config) {
      const id = params.id;
      delete params.id;
      return http.get(
        `${AJAX_URL_PREFIX}/handover/records/${id}/tasks/?${json2Query(params)}`,
        // `/handover/records/?mock-file=index&invoke=getTransferHistoryDetail&id=${id}`,
        {},
        config
      );
    },

    /**
         *  推荐列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getRecommended ({ commit, state, dispatch }, params = {}, config) {
      return http.get(
        `${AJAX_URL_PREFIX}/policies/recommended/?${json2Query(params)}`,
        {},
        config
      );
    }
  }
};

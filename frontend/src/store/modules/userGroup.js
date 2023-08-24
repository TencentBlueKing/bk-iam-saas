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
         * 获取用户组列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserGroupList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/groups/?${json2Query(params)}`, config);
    },

    /**
         * 获取用户组详情
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserGroupDetail ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      // return http.get(`${AJAX_URL_PREFIX}/groups/${id}/`, config);
      const queryParams = Object.keys(requestParams).length ? `${id}/?${json2Query(requestParams)}` : `${id}/`;
      return http.get(`${AJAX_URL_PREFIX}/groups/${queryParams}`, {}, config);
    },

    /**
         * 添加用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addUserGroup ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/groups/`, params, config);
    },

    /**
         * 修改用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    editUserGroup ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const { id } = requestParams;
      delete requestParams.id;
      return http.put(`${AJAX_URL_PREFIX}/groups/${id}/`, requestParams, config);
    },

    /**
         * 删除用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deleteUserGroup ({ commit, state, dispatch }, params, config) {
      const { id } = params;
      return http.delete(`${AJAX_URL_PREFIX}/groups/${id}/`, config);
    },

    /**
         * 获取用户组成员列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserGroupMemberList ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const { id } = requestParams;
      delete requestParams.id;
      return http.get(`${AJAX_URL_PREFIX}/groups/${id}/members/?${json2Query(requestParams)}`, config);
    },

    /**
         * 用户组添加成员
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addUserGroupMember ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const { id } = requestParams;
      delete requestParams.id;
      return http.post(`${AJAX_URL_PREFIX}/groups/${id}/members/`, requestParams, config);
    },

    /**
         * 用户组批量添加成员
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    batchAddUserGroupMember ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      return http.post(`${AJAX_URL_PREFIX}/groups/members/`, requestParams, config);
    },

    /**
         * 用户组删除成员
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deleteUserGroupMember ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const { id } = requestParams;
      delete requestParams.id;
      return http.delete(`${AJAX_URL_PREFIX}/groups/${id}/members/`, { data: requestParams }, config);
    },

    /**
         * 获取用户组权限模板列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params { id, systemId } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserGroupTemplateList ({ commit, state, dispatch }, { id, systemId }, config) {
      return http.get(`${AJAX_URL_PREFIX}/groups/${id}/templates/?system_id=${systemId}`, config);
    },

    /**
         * 用户组添加权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addUserGroupPerm ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const { id } = requestParams;
      delete requestParams.id;
      return http.post(`${AJAX_URL_PREFIX}/groups/${id}/templates/`, requestParams, config);
    },

    /**
         * 用户组转出
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    userGroupTransfer ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/groups/transfer/`, params, config);
    },

    /**
         * 分配(二级管理空间)
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    userGroupDistribute ({ commit, state, dispatch }, params, config) {
      const { id } = params;
      return http.post(`${AJAX_URL_PREFIX}/groups/${id}/transfer/`, params, config);
    },

    /**
         * 获取用户组有权限的系统列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getGroupSystems ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const { id } = requestParams;
      delete requestParams.id;
      const queryParams = Object.keys(requestParams).length ? `${id}/systems/?${json2Query(requestParams)}` : `${id}/systems/`;
      return http.get(`${AJAX_URL_PREFIX}/groups/${queryParams}`, {}, config);
    },

    /**
         * 获取用户组权限模板授权信息
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id, templateId } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getGroupTemplateDetail ({ commit, state, dispatch }, { id, templateId }, config) {
      return http.get(`${AJAX_URL_PREFIX}/groups/${id}/templates/${templateId}/`, config);
    },

    /**
         * 获取用户组自定义权限列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id, systemId } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getGroupPolicy ({ commit, state, dispatch }, { id, systemId }, config) {
      return http.get(`${AJAX_URL_PREFIX}/groups/${id}/policies/?system_id=${systemId}`, config);
    },

    /**
         * 用户组权限修改
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id, systemId } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    updateGroupPolicy ({ commit, state, dispatch }, { id, data }, config) {
      return http.put(`${AJAX_URL_PREFIX}/groups/${id}/policies/`, data, config);
    },

    /**
         * 用户组删除自定义权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id, data } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deleteGroupPolicy ({ commit, state, dispatch }, { id, data }, config) {
      return http.delete(`${AJAX_URL_PREFIX}/groups/${id}/policies/`, { data }, config);
    },

    /**
         * 条件差异对比
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id, data } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    groupPolicyCompare ({ commit, state, dispatch }, { id, data }, config) {
      return http.post(`${AJAX_URL_PREFIX}/groups/${id}/policies/condition_compare/`, data, config);
    },

    /**
         * 权限模板操作条件对比
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id, templateId, data } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    groupTemplateCompare ({ commit, state, dispatch }, { id, templateId, data }, config) {
      return http.post(
        `${AJAX_URL_PREFIX}/groups/${id}/templates/${templateId}/condition_compare/`,
        data,
        config
      );
    },

    /**
         * 用户组添加权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} { id, data } 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    addUserGroupPolicy ({ commit, state, dispatch }, { id, data }, config) {
      return http.post(`${AJAX_URL_PREFIX}/groups/${id}/policies/`, data, config);
    }
  }
};

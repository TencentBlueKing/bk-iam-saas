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
     * 分级管理员查看有权限的用户组成员列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getUserGroupMemberList ({ commit, state, dispatch }, params = {}, config) {
      Object.keys(params).forEach((item) => {
        if (['offset', 'limit'].includes(item) || params[item] === '') {
          delete params[item];
        }
      });
      // const queryParams = Object.keys(params).length ? `/?${json2Query(params)}` : '/';
      // return http.get(`${AJAX_URL_PREFIX}/roles/group_members${queryParams}`, config);
      const { page, page_size, hidden } = params;
      const queryParams = Object.assign({}, { page, page_size });
      if (params.hasOwnProperty('hidden')) {
        queryParams.hidden = hidden;
      }
      return http.post(`${AJAX_URL_PREFIX}/roles/group_members/?${json2Query(queryParams)}`, params, config);
    },

    /**
     * 角色用户组成员-用户组列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getUserOrDepartGroupList ({ commit, state, dispatch }, params, config) {
      const { offset, limit, hidden } = params;
      const requestParams = Object.assign({}, params);
      const queryParams = Object.assign({}, { offset, limit });
      if (params.hasOwnProperty('hidden')) {
        queryParams.hidden = hidden;
      }
      Object.keys(params).forEach((item) => {
        if (['subject_type', 'subject_id'].includes(item) || params[item] === '') {
          delete params[item];
        }
      });
      return http.post(`${AJAX_URL_PREFIX}/roles/group_members/${requestParams.subject_type}/${requestParams.subject_id}/groups/?${json2Query(queryParams)}`, params, config);
    },

    /**
     * 角色用户组成员-部门用户组列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getUserGroupByDepartList ({ commit, state, dispatch }, params, config) {
      const { offset, limit, hidden } = params;
      const requestParams = Object.assign({}, params);
      const queryParams = Object.assign({}, { offset, limit });
      if (params.hasOwnProperty('hidden')) {
        queryParams.hidden = hidden;
      }
      Object.keys(params).forEach((item) => {
        if (['subject_type', 'subject_id'].includes(item) || params[item] === '') {
          delete params[item];
        }
      });
      return http.post(`${AJAX_URL_PREFIX}/roles/group_members/${requestParams.subject_type}/${requestParams.subject_id}/departments/-/groups/?${json2Query(queryParams)}`, params, config);
    },

    /**
     * 角色用户组成员-人员模版用户组列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getUserMemberTempList ({ commit, state, dispatch }, params, config) {
      const { offset, limit, hidden } = params;
      const requestParams = Object.assign({}, params);
      const queryParams = Object.assign({}, { offset, limit });
      if (params.hasOwnProperty('hidden')) {
        queryParams.hidden = hidden;
      }
      Object.keys(params).forEach((item) => {
        if (['subject_type', 'subject_id'].includes(item) || params[item] === '') {
          delete params[item];
        }
      });
      return http.post(`${AJAX_URL_PREFIX}/roles/group_members/${requestParams.subject_type}/${requestParams.subject_id}/subject_template_groups/?${json2Query(queryParams)}`, params, config);
    },

    /**
     * 角色用户组成员-部门人员模版用户组列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getDepartMemberTempList ({ commit, state, dispatch }, params, config) {
      const { offset, limit, hidden } = params;
      const requestParams = Object.assign({}, params);
      const queryParams = Object.assign({}, { offset, limit });
      if (params.hasOwnProperty('hidden')) {
        queryParams.hidden = hidden;
      }
      Object.keys(params).forEach((item) => {
        if (['subject_type', 'subject_id'].includes(item) || params[item] === '') {
          delete params[item];
        }
      });
      return http.post(`${AJAX_URL_PREFIX}/roles/group_members/${requestParams.subject_type}/${requestParams.subject_id}/departments/-/subject_template_groups/?${json2Query(queryParams)}`, params, config);
    },

    /**
     * 批量用户组删除成员
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    deleteGroupMembers ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/groups/members/delete/`, params, config);
    },

    /**
     * 批量重置用户组成员
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    resetGroupMembers ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/group_members/reset/`, params, config);
    },

    /**
     * 批量清空用户组成员
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    cleanGroupMembers ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/group_members/clean/`, params, config);
    },

    /**
     * 批量加入用户组/批量续期
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    batchJoinOrRenewal ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/groups/members/renew/`, params, config);
    }
  }
};

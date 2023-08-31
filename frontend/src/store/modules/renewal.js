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
         * 用户组权限续期
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    groupPermRenewal ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/group_renew/`, params, config);
    },

    /**
         * 自定义权限续期
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    customPermRenewal ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/policy_renew/`, params, config);
    },

    /**
         * 获取即将过期的自定义权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getExpireSoonPerm ({ commit, state, dispatch }, params = {}, config) {
      const queryParams = Object.keys(params).length ? `/?${json2Query(params)}` : '/';
      return http.get(`${AJAX_URL_PREFIX}/policies/expire_soon${queryParams}`, config);
    },

    /**
         * 登录用户即将过期的用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getExpireSoonGroupWithUser ({ commit, state, dispatch }, params = {}, config) {
      return http.get(`${AJAX_URL_PREFIX}/users/groups_expire_soon/?${json2Query(params)}`, config);
    },

    /**
         * 用户组的成员续期
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    groupMemberPermRenewal ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const groupId = requestParams.groupId;
      delete requestParams.groupId;
      return http.post(`${AJAX_URL_PREFIX}/groups/${groupId}/members_renew/`, requestParams, config);
    },

    /**
         * 获取角色即将过期的用户组成员
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getExpireSoonGroup ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/group_members_renew/?${json2Query(params)}`, config);
    },

    /**
         * 角色即将过期的用户组成员权限续期
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    roleGroupsRenewal ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/roles/groups_renew/`, params, config);
    },

    /**
         * 查询角色即将过期的用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getExpiredGroups ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/roles/groups_renew/?${json2Query(params)}`, config);
    },

    /**
         * 获取用户组即将过期成员列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getExpireSoonGroupMembers ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      delete requestParams.id;
      return http.get(
        `${AJAX_URL_PREFIX}/roles/groups_renew/${params.id}/members/?${json2Query(requestParams)}`,
        config
      );
    }
  }
};

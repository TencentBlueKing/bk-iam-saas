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
         * 提交权限申请
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 提交参数
         *
         * @return {Promise} promise 对象
         */
    permTemporaryApply ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/temporary_policy/`, params, config);
    },

    /**
         * 删除权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params { policyIds, systemId } policyIds 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deletePerm ({ commit, state, dispatch }, { policyIds, systemId }, config) {
      return http.delete(`${AJAX_URL_PREFIX}/policies/?ids=${policyIds.join(',')}&system_id=${systemId}`, config);
    },

    /**
         * 删除资源组权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params { policyIds, systemId } policyIds 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */

    deleteRosourceGroupPerm ({ commit, state, dispatch }, { id, resourceGroupId }, config) {
      return http.delete(`${AJAX_URL_PREFIX}/policies/${id}/${resourceGroupId}/`, config);
    },

    /**
         * 组织架构删除权限
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params { policyIds, systemId } policyIds 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deleteSubjectPerm ({ commit, state, dispatch }, { policyIds, systemId, subjectId, subjectType }, config) {
      return http.delete(
        `${AJAX_URL_PREFIX}/subjects/${subjectType}/${subjectId}/policies/?`
                    + `ids=${policyIds.join(',')}&system_id=${systemId}`,
        config
      );
    },

    /**
         * 获取用户的关联权限列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 查询参数
         *
         * @return {Promise} promise 对象
         */
    getActionPolicies ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/policies/attach_policies/?${json2Query(params)}`, config);
    },

    /**
         * 条件对比差异
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 提交参数
         *
         * @return {Promise} promise 对象
         */
    conditionCompare ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/condition_compare/`, params, config);
    },

    /**
         * 关联操作对比差异
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 提交参数
         *
         * @return {Promise} promise 对象
         */
    attachActionCompare ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/topology_compare/`, params, config);
    },

    /**
         * 权限更新
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object}  params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    updatePerm ({ commit, state, dispatch }, params, config) {
      const { id, data } = params;
      return http.put(`${AJAX_URL_PREFIX}/policies/${id}/`, data, config);
    },

    /**
         * 组织架构个人权限更新
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object}  params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    updateSubjectPerm ({ commit, state, dispatch }, params, config) {
      const { id, subjectType, subjectId, data } = params;
      return http.put(`${AJAX_URL_PREFIX}/subjects/${subjectType}/${subjectId}/policies/${id}/`, data, config);
    },

    /**
         * 申请加入用户组
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object}  params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    applyJoinGroup ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/applications/group/`, params, config);
    },

    /**
         * 获取自定义申请常用操作
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getUserCommonAction ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/users/common_actions/?system_id=${params.systemId}`, config);
    },

    /**
         * 批量复制策略资源
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 提交参数
         *
         * @return {Promise} promise 对象
         */
    resourceBatchCopy ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/policies/resource_copy/`, params, config);
    },

    /**
         * 生成依赖操作
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 提交参数
         *
         * @return {Promise} promise 对象
         */
    getRelatedPolicy ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/policies/related/`, params, config);
    }
  }
};

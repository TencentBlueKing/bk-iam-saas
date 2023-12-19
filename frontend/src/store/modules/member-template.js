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
     * 获取人员模版列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getSubjectTemplateList ({ commit, state, dispatch }, params = {}, config) {
      const queryParams = Object.keys(params).length ? `/?${json2Query(params)}` : '/';
      return http.get(`${AJAX_URL_PREFIX}/subject_templates${queryParams}`, config);
    },

    /**
     * 人员模板详情
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    subjectTemplateDetail ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/subject_templates/${params.id}/`, config);
    },

    /**
     * 创建人员模版
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    createSubjectTemplate ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/subject_templates/`, params, config);
    },

    /**
     * 更新人员模版
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    updateSubjectTemplate ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.put(`${AJAX_URL_PREFIX}/subject_templates/${id}/`, requestParams, config);
    },
    
    /**
     * 删除人员模版
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    deleteSubjectTemplate ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.delete(`${AJAX_URL_PREFIX}/subject_templates/${id}/`, requestParams, config);
    },

    /**
     * 批量人员模版添加成员
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    addBatchSubjectTemplateMembers ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/subject_templates/members/`, params, config);
    },

    /**
     * 人员模版关联用户组列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getSubjectTemplatesGroups ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.get(`${AJAX_URL_PREFIX}/subject_templates/${id}/groups/?${json2Query(requestParams)}`, requestParams, config);
    },
    
    /**
     * 删除人员模板用户关联
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    deleteSubjectTemplateGroups ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.delete(`${AJAX_URL_PREFIX}/subject_templates/${id}/groups/`, { data: requestParams }, config);
    },

    /**
     * 人员模板成员列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getSubjectTemplateMembers ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.get(`${AJAX_URL_PREFIX}/subject_templates/${id}/members/?${json2Query(requestParams)}`, requestParams, config);
    },

    /**
     * 添加人员模板成员
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    addSubjectTemplateMembers ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.post(`${AJAX_URL_PREFIX}/subject_templates/${id}/members/`, requestParams, config);
    },

    /**
     * 删除人员模版成员
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    deleteSubjectTemplateMembers ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.delete(`${AJAX_URL_PREFIX}/subject_templates/${id}/members/`, { data: requestParams }, config);
    },

    /**
     * 用户组拥有的人员模板列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getGroupSubjectTemplate ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.get(`${AJAX_URL_PREFIX}/groups/${id}/subject_templates/?${json2Query(requestParams)}`, requestParams, config);
    },

    /**
     * 模版用户组成员列表
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object} params 请求参数
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
    */
    getGroupSubjectTemplateMembers ({ commit, state, dispatch }, params, config) {
      const requestParams = Object.assign({}, params);
      const id = requestParams.id;
      delete requestParams.id;
      return http.get(`${AJAX_URL_PREFIX}/groups/${id}/template-members/?${json2Query(requestParams)}`, requestParams, config);
    }
  }
};

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
  },
  getters: {
  },
  mutations: {
  },
  actions: {
    /**
         * 获取用户页面接入构建模型列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getModelingList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/modeling/?${json2Query(params)}`, config);
    },

    /**
         * 获取用户页面接入构建模型数据
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getModeling ({ commit, state, dispatch }, params, config) {
      const { id, data = {} } = params;
      return http.get(`${AJAX_URL_PREFIX}/modeling/${id}/?${json2Query(data)}`, config);
    },

    /**
         * 校验系统ID唯一性
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    checkModelingId ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/modeling/is_id_exists/?${json2Query(params)}`, config);
    },

    /**
         * 检查模型中的某种资源的id是否已存在
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    checkResourceId ({ commit, state, dispatch }, params, config) {
      const { id, data = {} } = params;
      return http.get(`${AJAX_URL_PREFIX}/modeling/${id}/is_id_exists/?${json2Query(data)}`, config);
    },

    /**
         * 新建模型系统
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    createModeling ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/modeling/`, params, config);
    },

    /**
         * 根据 ID 更新模型中的部分数据
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object}  params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    updateModeling ({ commit, state, dispatch }, params, config) {
      const { id, data } = params;
      return http.put(`${AJAX_URL_PREFIX}/modeling/${id}/`, data, config);
    },

    /**
         * 拉取某个系统的资源列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getResourceTypeListBySystem ({ commit, state, dispatch }, params, config) {
      const { id, data = {} } = params;
      return http.get(`${AJAX_URL_PREFIX}/modeling/${id}/resource_types/?${json2Query(data)}`, config);
    },

    /**
         * 拉取某个系统的实例视图列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getInstanceSelectionsListBySystem ({ commit, state, dispatch }, params, config) {
      const { id, data = {} } = params;
      return http.get(`${AJAX_URL_PREFIX}/modeling/${id}/instance_selections/?${json2Query(data)}`, config);
    },

    /**
         * 根据 ID 删除模型中的部分数据
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    deleteModeling ({ commit, state, dispatch }, params, config) {
      const { id, data = {} } = params;
      return http.delete(`${AJAX_URL_PREFIX}/modeling/${id}/`, { data: data }, config);
    },

    /**
         * 拉取所有系统列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getSystemList ({ commit, state, dispatch }, params, config) {
      const { id } = params;
      return http.get(`${AJAX_URL_PREFIX}/modeling/${id}/systems/`, config);
    },

    /**
         * 生成json
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    downloadJSON ({ commit, state, dispatch }, params, config) {
      const { id, data } = params;
      return http.post(`${AJAX_URL_PREFIX}/modeling/${id}/json/`, data, config);
    }

    // /**
    //  * 更新模板
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // updateTemplate ({ commit, state, dispatch }, params, config) {
    //     const requestParams = Object.assign({}, params)
    //     const id = requestParams.id
    //     delete requestParams.id
    //     return http.patch(`${AJAX_URL_PREFIX}/templates/${id}/`, requestParams, config)
    // },

    // /**
    //  * 获取模板详情
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params { id, grouping } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // getTemplateDetail ({ commit, state, dispatch }, { id, grouping }, config) {
    //     return http.get(`${AJAX_URL_PREFIX}/templates/${id}/?grouping=${grouping}`, config)
    // },

    // /**
    //  * 获取模板成员
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // getTemplateMember ({ commit, state, dispatch }, params, config) {
    //     const id = params.id
    //     const requestParams = Object.assign({}, params)
    //     delete requestParams.id
    //     return http.get(`${AJAX_URL_PREFIX}/templates/${id}/members/?${json2Query(requestParams)}`, config)
    // },

    // /**
    //  * 模板添加成员
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // addTemplateMember ({ commit, state, dispatch }, params, config) {
    //     const id = params.id
    //     const requestParams = Object.assign({}, params)
    //     delete requestParams.id
    //     return http.post(`${AJAX_URL_PREFIX}/templates/${id}/members/`, requestParams, config)
    // },

    // /**
    //  * 模板删除成员
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // deleteTemplateMember ({ commit, state, dispatch }, params, config) {
    //     const id = params.id
    //     return http.delete(`${AJAX_URL_PREFIX}/templates/${id}/members/`, { data: params.data }, config)
    // },

    // /**
    //  * 模板删除
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params { id } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // deleteTemplate ({ commit, state, dispatch }, { id }, config) {
    //     return http.delete(`${AJAX_URL_PREFIX}/templates/${id}/`, {}, config)
    // },

    // /**
    //  * 权限模板版本对比
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params { templateId, version } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // templateCompare ({ commit, state, dispatch }, { templateId, version }, config) {
    //     return http.get(`${AJAX_URL_PREFIX}/templates/${templateId}/compare/?version=${version}`, {}, config)
    // },

    // /**
    //  * 权限模板操作条件对比
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // templateConditionCompare ({ commit, state, dispatch }, params, config) {
    //     const id = params.id
    //     const requestParams = Object.assign({}, params)
    //     delete requestParams.id
    //     return http.post(`${AJAX_URL_PREFIX}/templates/${id}/condition_compare/`, requestParams, config)
    // },

    // /**
    //  * 权限模板授权对象更新
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // templateAuthObjectSync ({ commit, state, dispatch }, params, config) {
    //     const id = params.templateId
    //     const requestParams = Object.assign({}, params)
    //     delete requestParams.templateId
    //     return http.post(`${AJAX_URL_PREFIX}/templates/${id}/sync/`, requestParams, config)
    // },

    // /**
    //  * 获取常用操作
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // getCommonAction ({ commit, state, dispatch }, params, config) {
    //     return http.get(`${AJAX_URL_PREFIX}/roles/common_actions/?system_id=${params.systemId}`, config)
    // },

    // /**
    //  * 新增常用操作
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // addCommonAction ({ commit, state, dispatch }, params, config) {
    //     return http.post(`${AJAX_URL_PREFIX}/roles/common_actions/`, params, config)
    // },

    // /**
    //  * 删除常用操作
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} params 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // deleteCommonAction ({ commit, state, dispatch }, params, config) {
    //     return http.delete(`${AJAX_URL_PREFIX}/roles/common_actions/${params.id}/`, {}, config)
    // },

    // /**
    //  * 获取常角色的授权范围
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // getAuthorizationScopeActions ({ commit, state, dispatch }, { systemId }, config) {
    //     return http.get(`${AJAX_URL_PREFIX}/roles/authorization_scope_actions/?system_id=${systemId}`, config)
    // },

    // /**
    //  * 获取模板预更新信息
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} { id } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // getPreUpdateInfo ({ commit, state, dispatch }, { id }, config) {
    //     return http.get(`${AJAX_URL_PREFIX}/templates/${id}/pre_update/`, config)
    // },

    // /**
    //  * 提交模板预更新信息
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} { id } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // addPreUpdateInfo ({ commit, state, dispatch }, { id, data }, config) {
    //     return http.post(`${AJAX_URL_PREFIX}/templates/${id}/pre_update/`, data, config)
    // },

    // /**
    //  * 获取模板用户组更新预览信息
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} { id } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // getGroupsPreview ({ commit, state, dispatch }, { id, data }, config) {
    //     return http.get(`${AJAX_URL_PREFIX}/templates/${id}/groups_preview/?${json2Query(data)}`, config)
    // },

    // /**
    //  * 模板更新确认
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} { id } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // updateCommit ({ commit, state, dispatch }, { id }, config) {
    //     return http.post(`${AJAX_URL_PREFIX}/templates/${id}/update_commit/`, config)
    // },

    // /**
    //  * 取消模板预更新
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} { id } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // cancelPreUpdate ({ commit, state, dispatch }, { id }, config) {
    //     return http.delete(`${AJAX_URL_PREFIX}/templates/${id}/pre_update/`, {}, config)
    // },

    // /**
    //  * 生成克隆的用户组策略
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} { id, data } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // getCloneAction ({ commit, state, dispatch }, { id, data }, config) {
    //     return http.post(`${AJAX_URL_PREFIX}/templates/${id}/clone_action/`, data, config)
    // },

    // /**
    //  * 同步模板预提交
    //  *
    //  * @param {Function} commit store commit mutation handler
    //  * @param {Object} state store state
    //  * @param {Function} dispatch store dispatch action handler
    //  * @param {Object} { id, data } 请求参数
    //  * @param {Object?} config http config
    //  *
    //  * @return {Promise} promise 对象
    //  */
    // preGroupSync ({ commit, state, dispatch }, { id, data }, config) {
    //     return http.post(`${AJAX_URL_PREFIX}/templates/${id}/pre_group_sync/`, data, config)
    // }
  }
};

import http from '@/api';
import { json2Query } from '@/common/util';

const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;

export default {
  namespaced: true,
  actions: {
    /**
         * 获取系统下操作的敏感等级数量
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getSensitivityLevelCount ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/approvals/sensitivity_level/count/?${json2Query(params)}`, config);
    },

    /**
         * 获取操作审批流程列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getProcessesActionsList ({ commit, state, dispatch }, params, config) {
      return http.get(`${AJAX_URL_PREFIX}/approvals/processes/actions/?${json2Query(params)}`, config);
    },

    /**
         * 批量配置操作的敏感等级
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    updateActionsSensitivityLevel ({ commit, state, dispatch }, params, config) {
      return http.post(`${AJAX_URL_PREFIX}/approvals/sensitivity_level/actions/`, params, config);
    }
  }
};

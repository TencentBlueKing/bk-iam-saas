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
import { getPlatformConfig, titleSeparator, setDocumentTitle, setShortcutIcon } from '@blueking/platform-config';

export default {
  namespaced: true,
  state: {
    initialConfig: {
      site: {
        name: '', // 网站名
        separator: '|' // 网站名称路由分隔符
      },
      name: '权限中心',
      nameEn: 'IAM',
      brandName: '蓝鲸智云',
      brandNameEn: 'Tencent BlueKing',
      appLogo: require('@/images/logo.svg'),
      favicon: require('@/images/logo.svg'),
      version: ''
    }
  },
  getters: {
    globalConfig: state => state.initialConfig
  },
  mutations: {
    setCurrentGlobalConfig (state, params) {
      state.initialConfig = Object.assign(state.initialConfig, params);
    }
  },
  actions: {
    /**
     *  获取当前用户的全局设置
     *
     * @param {Function} commit store commit mutation handler
     * @param {Object} state store state
     * @param {Function} dispatch store dispatch action handler
     * @param {Object?} config http config
     *
     * @return {Promise} promise 对象
     */
    async getCurrentGlobalConfig ({ commit, state, dispatch }) {
      let commitParams = {};
      if (window.BK_SHARED_RES_URL) {
        const repoUrl = window.BK_SHARED_RES_URL.endsWith('/') ? window.BK_SHARED_RES_URL : `${window.BK_SHARED_RES_URL}/`;
        try {
          commitParams = await getPlatformConfig(`${repoUrl}bk_iam/base.js`, state.initialConfig);
          if (commitParams && commitParams.site) {
            commitParams.site.separator = titleSeparator;
          }
        } catch (e) {
          console.error(e, '错误日志');
          commitParams = await getPlatformConfig(state.initialConfig);
        }
      } else {
        // 本地开发环境调试
        commitParams = await getPlatformConfig(state.initialConfig);
      }
      console.log(commitParams, '配置项数据');
      setDocumentTitle(commitParams.i18n || {});
      setShortcutIcon(commitParams.favicon);
      commit('setCurrentGlobalConfig', commitParams);
    }
  }
};

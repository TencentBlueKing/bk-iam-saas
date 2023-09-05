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

import Vue from 'vue';
import Vuex from 'vuex';
import http from '@/api';
import { unifyObjectStyle, json2Query } from '@/common/util';
import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';
import il8n from '@/language';

// 系统模块
import system from './modules/system';

// 权限模块
import perm from './modules/perm';

// 权限模板 模块
import permTemplate from './modules/permTemplate';

// 组织架构 模块
import organization from './modules/organization';

// 权限申请 模块
import permApply from './modules/permApply';

// 我的审批 模块
import approval from './modules/approval';

// 我的申请 模块
import myApply from './modules/myApply';

// 用户组 模块
import userGroup from './modules/userGroup';

// 一级管理空间模块
import role from './modules/role';

// 审批流程设置
import approvalProcess from './modules/approval-process';

// 操作聚合模块
import aggregate from './modules/aggregate';

// 续期模块
import renewal from './modules/renewal';

// 审计模块
import audit from './modules/audit';

// 系统接入模块
import access from './modules/access';

// 资源权限模块
import resourcePermiss from './modules/resource-permiss';

// 临时权限模块
import applyProvisionPerm from './modules/apply-provision-perm';

// 管理空间模块
import spaceManage from './modules/space-manage';

// 用户组设置模块
import userGroupSetting from './modules/user-group-setting';

Vue.use(Vuex);

const SITE_URL = window.SITE_URL;

const currentNav = [
  {
    icon: 'perm-manage',
    name: il8n('nav', '发起需求'),
    rkey: 'initiateDemand',
    children: [
      {
        icon: 'perm-apply',
        name: il8n('nav', '权限申请'),
        id: 'permApplyNav',
        rkey: 'applyJoinUserGroup',
        path: `${SITE_URL}apply-join-user-group`,
        disabled: false
      }
      // {
      //     icon: 'perm-apply',
      //     name: il8n('nav', '临时权限申请'),
      //     id: 'provisionPermApplyNav',
      //     rkey: 'applyProvisionPerm',
      //     path: `${SITE_URL}apply-provision-perm`,
      //     disabled: false
      // }
    ]
  },
  {
    icon: 'perm-manage',
    name: il8n('nav', '工作台'),
    rkey: 'initiateDemand',
    children: [
      {
        icon: 'my-apply',
        id: 'applyNav',
        rkey: 'apply',
        name: il8n('nav', '我的申请'),
        path: `${SITE_URL}apply`,
        disabled: false
      },
      {
        icon: 'my-approval',
        id: 'approvalNav',
        rkey: 'approval',
        name: il8n('nav', '我的审批')
      },
      {
        icon: 'my-perm',
        id: 'myPermNav',
        rkey: 'myPerm',
        name: il8n('nav', '我的权限'),
        path: `${SITE_URL}my-perm`,
        disabled: false
      },
      {
        icon: 'my-manage-space',
        id: 'myManageSpaceNav',
        rkey: 'myManageSpace',
        name: il8n('nav', '我的管理空间'),
        path: `${SITE_URL}my-manage-space`,
        disabled: false
      }
    ]
  },
  {
    icon: 'perm-manage',
    name: il8n('nav', '权限管理'),
    rkey: 'managePermission',
    children: [
      {
        icon: 'user-group',
        id: 'userGroupNav',
        rkey: 'userGroup',
        name: il8n('nav', '用户组'),
        path: `${SITE_URL}user-group`,
        disabled: false
      },
      {
        icon: 'perm-template',
        id: 'permTemplateNav',
        rkey: 'permTemplate',
        name: il8n('nav', '权限模板'),
        path: `${SITE_URL}perm-template`,
        disabled: false
      },
      {
        icon: 'personal-user',
        id: 'userNav',
        rkey: 'user',
        name: il8n('nav', '用户'),
        path: `${SITE_URL}user`,
        disabled: false
      }
    ]
  },
  {
    icon: 'perm-manage',
    name: il8n('nav', '管理空间'),
    rkey: 'manageSpaces',
    children: [
      {
        icon: 'auth-scope',
        id: 'authorBoundaryNav',
        rkey: 'authorBoundary',
        name: il8n('nav', '授权边界-nav'),
        path: `${SITE_URL}manage-spaces/authorization-boundary`,
        disabled: false
      },
      {
        icon: 'level-two-manage-space',
        id: 'secondaryManageSpaceNav',
        rkey: 'secondaryManageSpace',
        name: il8n('nav', '二级管理空间'),
        path: `${SITE_URL}manage-spaces/secondary-manage-space`,
        disabled: false
      }
    ]
  },
  {
    icon: 'level-one-manage-space',
    id: 'gradingAdminNav',
    rkey: 'ratingManager',
    name: il8n('nav', '管理空间'),
    path: `${SITE_URL}rating-manager`,
    disabled: false
  },
  // {
  //     icon: 'grade-admin',
  //     id: 'firstManageSpaceNav',
  //     rkey: 'firstManageSpace',
  //     name: il8n('nav', '一级管理空间'),
  //     path: `${SITE_URL}first-manage-space`,
  //     disabled: false
  // },
  {
    icon: 'resource-perm-manage',
    id: 'resourcePermissNav',
    rkey: 'resourcePermiss',
    name: il8n('nav', '资源权限管理'),
    path: `${SITE_URL}resource-permiss`,
    disabled: false
  },
  {
    icon: 'perm-manage',
    name: il8n('common', '设置'),
    rkey: 'set',
    children: [
      {
        icon: 'super-admin',
        name: il8n('common', '管理员'),
        id: 'settingNav',
        rkey: 'administrator',
        path: `${SITE_URL}administrator`,
        disabled: false
      },
      {
        icon: 'approval-process-manage',
        name: il8n('myApply', '审批流程'),
        id: 'approvalProcessNav',
        rkey: 'approvalProcess',
        path: `${SITE_URL}approval-process`,
        disabled: false
      },
      {
        icon: 'operate-audit',
        name: il8n('nav', '审计'),
        id: 'auditNav',
        rkey: 'audit',
        path: `${SITE_URL}audit`,
        disabled: false
      },
      {
        icon: 'setting-fill',
        name: il8n('nav', '用户组设置'),
        id: 'userGroupSettingNav',
        rkey: 'userGroupSetting',
        path: `${SITE_URL}user-group-setting`,
        disabled: false
      }
    ]
  }
];

if (window.ENABLE_MODEL_BUILD.toLowerCase() === 'true') {
  currentNav.push({
    icon: 'perm-manage',
    name: il8n('nav', '开发者'),
    rkey: 'Developers',
    children: [
      {
        icon: 'system-access',
        id: 'systemAccessNav',
        rkey: 'systemAccess',
        name: il8n('nav', '系统接入'),
        path: `${SITE_URL}system-access`,
        disabled: true
      }
    ]
  });
}

if (window.ENABLE_TEMPORARY_POLICY.toLowerCase() === 'true') {
  currentNav[0].children.push({
    icon: 'tempora-perm-apply',
    name: il8n('nav', '临时权限申请'),
    id: 'provisionPermApplyNav',
    rkey: 'applyProvisionPerm',
    path: `${SITE_URL}apply-provision-perm`,
    disabled: false
  });
}

const store = new Vuex.Store({
  modules: {
    system,
    perm,
    approval,
    permTemplate,
    organization,
    permApply,
    myApply,
    userGroup,
    role,
    approvalProcess,
    aggregate,
    renewal,
    audit,
    access,
    resourcePermiss,
    applyProvisionPerm,
    spaceManage,
    userGroupSetting
  },
  state: {
    mainContentLoading: false,
    nav: {
      stick: window.localStorage.getItem('navStick') !== 'false',
      fold: window.localStorage.getItem('navStick') === 'false'
    },
    group: {
      hasPerm: false,
      hasMember: false,
      systems: []
    },
    header: {
      title: '',
      // 顶导的指示的索引，如果为空，即不显示指示
      indicatorIndex: '',
      // 返回的 router 名字，如果有，那么就显示返回
      backRouter: ''
    },
    // 系统当前登录用户
    user: {},
    users: [],
    versionLogs: [],
    isSync: false,
    routerDiff: [],
    currentNav: currentNav,
    roleCount: 0,
    roleList: [],
    noviceGuide: {
      rating_manager_authorization_scope: true,
      rating_manager_subject_scope: true,
      rating_manager_merge_action: true,
      switch_role: true,
      create_perm_template: true,
      create_group: true,
      set_group_approval_process: true,
      add_group_member: true,
      add_group_perm_template: true,
      grade_manager_upgrade: true
    },
    loadingConf: {
      speed: 2,
      primaryColor: '#f5f6fa',
      secondaryColor: '#FAFAFC'
    },
    // 系统回调地址
    host: '',
    // 前置路由
    fromRouteName: '',

    // nav导航
    navData: [],

    index: 0,

    navCurRoleId: 0,

    showNoviceGuide: false,

    curRoleId: 0,

    externalSystemsLayout: {
      hideIamHeader: false, // 第一层级头部导航
      hideIamSlider: false, // 第一层级侧边导航
      hideIamBreadCrumbs: false, // 第一层级面包屑
      hideIamGuide: false, // 隐藏所有guide的tooltip
      myPerm: { // 我的权限
        hideCustomTab: false, // 自定义权限tab - 1
        hideApplyBtn: false, // 申请权限按钮 - 1
        hideTemporaryCustomTab: false, // 临时权限tab -1
        renewal: { // 我的权限-权限续期
          hideCustomTab: false // 自定义权限tab - 2
        },
        transfer: { // 我的权限-权限交接
          hideTextBtn: false, // 交接历史文本按钮 - 3
          hideCustomData: false, // 自定义权限交接-3
          hideManagerData: false, // 管理员交接数据-3
          showUserGroupSearch: false, // 显示权限交接用户组查询-3
          setFooterBtnPadding: false // 设置内嵌页面权限交接底部按钮你编剧
        }
      },
      userGroup: { // 用户组
        addGroup: { // 用户组 - 添加用户组 - 添加权限抽屉
          hideAddTemplateTextBtn: false, // 右侧抽屉新增文本按钮-7.1
          AddUserGroupDiaLogUrl: '' // 用户组 - 添加用户组 - 组成员链接跳转
        },
        groupDetail: { // 用户组 - 组详情
          hideAddBtn: false, // 用户组-组权限-添加权限按钮-6
          hideEditBtn: false, // 用户组-组权限-编辑权限按钮-6
          hideDeleteBtn: false, // 用户组-组权限-删除权限按钮-6
          hideGroupName: false, // 用户组-组详情-组名称-6
          hideGroupDescEdit: false, // 用户组-组详情-组描述编辑-6
          hideCustomPerm: false, // 用户组-组权限-自定义权限相关信息-6
          hideGroupPermExpandTitle: false, // 用户组-组权限-隐藏自定义权限标题
          setMainLayoutHeight: false // 用户组-详情页面-区分主体高度
        }
      },
      // 我的申请
      myApply: {
        leftLayoutHeight: false, // 设置外部嵌套我的申请页面左侧主体内容高度
        rightLayoutHeight: false, // 设置外部嵌套我的申请页面右侧主体内容高度
        externalSystemParams: false // 设置获取我的申请嵌套页面url传参，根据id自动选中当前数据
      },
      // 设置项目最大可授权范围
      addMemberBoundary: {
        customFooterClass: false, // 设置项目最大可授权范围, 底部插槽自定义样式
        hideInfiniteTreeCount: false // 隐藏设置项目最大可授权范围左边拓扑树显示成员个数
      }
    }
  },
  getters: {
    mainContentLoading: state => state.mainContentLoading,
    navStick: state => state.nav.stick,
    navFold: state => state.nav.fold,
    headerTitle: state => state.header.title,
    indicatorIndex: state => state.header.indicatorIndex,
    backRouter: state => state.header.backRouter,
    user: state => state.user,
    users: state => state.users,
    versionLogs: state => state.versionLogs,
    currentNav: state => state.currentNav,
    group: state => state.group,
    isSync: state => state.isSync,
    roleList: state => state.roleList,
    roleCount: state => state.roleCount,
    routerDiff: state => state.routerDiff,
    noviceGuide: state => state.noviceGuide,
    loadingConf: state => state.loadingConf,
    host: state => state.host,
    fromRouteName: state => state.fromRouteName,
    navData: state => state.navData,
    index: state => state.index,
    navCurRoleId: state => state.navCurRoleId,
    showNoviceGuide: state => state.showNoviceGuide,
    curRoleId: state => state.curRoleId,
    externalSystemsLayout: state => state.externalSystemsLayout,
    externalSystemId: state => state.externalSystemId
  },
  mutations: {
    updateHost (state, params) {
      state.host = params;
    },
    updateRoute (state, params) {
      state.fromRouteName = params;
    },
    updateGroup (state, obj) {
      if (obj.hasOwnProperty('hasPerm')) {
        state.group.hasPerm = obj.hasPerm;
      }
      if (obj.hasOwnProperty('hasMember')) {
        state.group.hasMember = obj.hasMember;
      }
      if (obj.hasOwnProperty('systems')) {
        state.group.systems = [...obj.systems];
      }
    },

    updateSync (state, flag) {
      state.isSync = !!flag;
    },

    setNoviceGuide (state, payload) {
      payload.forEach((item) => {
        if (state.noviceGuide.hasOwnProperty(item.scene)) {
          state.noviceGuide[item.scene] = item.status;
        }
      });
    },

    updateNoviceGuide (state, type, flag = true) {
      state.noviceGuide[type] = flag;
    },

    /**
         * 设置 backRouter
         *
         * @param {Object} state store state
         * @param {string} backRouter backRouter
         */
    setBackRouter (state, backRouter) {
      state.header.backRouter = backRouter;
    },

    /**
         * 设置 header title
         *
         * @param {Object} state store state
         * @param {string} title title
         */
    setHeaderTitle (state, title) {
      state.header.title = title;
    },

    /**
         * 设置 indicator index
         *
         * @param {Object} state store state
         * @param {number} index index
         */
    setHeaderIndicatorIndex (state, index) {
      state.header.indicatorIndex = index;
    },

    /**
         * 设置内容区的 loading 是否显示
         *
         * @param {Object} state store state
         * @param {boolean} loading 是否显示 loading
         */
    setMainContentLoading (state, loading) {
      state.mainContentLoading = loading;
    },

    /**
         * 设置左侧导航的状态
         *
         * @param {Object} state store state
         * @param {Object} status 左侧导航状态
         */
    setNavStatus (state, status) {
      state.nav = Object.assign(state.nav, status);
    },

    /**
         * 更新当前用户 user
         *
         * @param {Object} state store state
         * @param {Object} user user 对象
         */
    updateUser (state, user) {
      state.user = Object.assign({}, user);
    },

    /**
         * 更新当前用户身份
         *
         * @param {Object} state store state
         * @param {Object} data
         */
    updateIdentity (state, data) {
      state.user.role = Object.assign({}, data);
    },

    /**
         * 记录当前下拉框身份
         *
         * @param {Object} state store state
         * @param {Object} data
         */
    updateNavId (state, id) {
      state.navCurRoleId = id;
    },

    /**
         * 更新版本日志
         *
         * @param {Object} state store state
         * @param {Object} version version 对象
         */
    updateVersion (state, version) {
      state.versionLogs.splice(0, state.versionLogs.length, ...version);
    },

    /**
         * 更新所有用户 users
         *
         * @param {Object} state store state
         * @param {Array} users users 对象
         */
    updateUsers (state, users) {
      state.users = [];
      if (users.length) {
        for (let i = 0; i < users.length; i++) {
          state.users.push(users[i]);
        }
      }
    },

    updataRouterDiff (state, role) {
      state.routerDiff = [...getRouterDiff(role)];
    },

    updataNavRouterDiff (state, index) {
      state.routerDiff = [...getNavRouterDiff(index)];
    },

    updateRoleList (state, payload) {
      state.roleList.splice(0, state.roleList.length, ...payload);
      // bus.$emit('roleList-update', payload.length);
    },

    updateRoleListTotal (state, payload) {
      state.roleCount = payload;
    },

    updateNavData (state, payload) {
      state.navData.splice(0, state.navData.length, ...payload);
    },

    updateIndex (state, payload) {
      state.index = payload;
    },

    updateSelectManager (state, payload) {
      state.showNoviceGuide = payload;
    },

    updateCurRoleId (state, id) {
      state.curRoleId = id;
    },

    setExternalSystemsLayout (state, payload) {
      state.externalSystemsLayout = payload;
    },

    updateSystemId (state, payload) {
      state.externalSystemId = payload;
    },

    setGuideShowByField (state, payload) {

    }
  },
  actions: {
    /**
         * 获取用户信息
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    userInfo ({ commit, state, dispatch }, config) {
      // const data = {
      //     'timestamp': 1623032422,
      //     'username': 'admin',
      //     'role': {
      //         'type': 'staff',
      //         'id': 0,
      //         'name': 'STAFF'
      //     }
      // }
      // if (data.role.type === 'system_manager') {
      //     data.role.name = `${data.role.name}${il8n('nav', '系统管理员')}`
      // }
      // commit('updateUser', data)

      // if (Object.keys(data).length > 0) {
      //     const role = data.role.type
      //     commit('updataRouterDiff', role)
      // }
      // return data
      const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;
      return http.get(`${AJAX_URL_PREFIX}/accounts/user/`, config).then((response) => {
        const data = response ? response.data : {};
        // 由于现有搜索改成后端接口搜索，去掉之前前端自定义的内容
        // if (data.role.type === 'system_manager') {
        //   const langManager = ['zh-cn'].includes(window.CUR_LANGUAGE) ? '系统管理员' : ' system administrator';
        //   data.role.name = `${data.role.name}${langManager}`;
        // }
        commit('updateUser', data);

        if (Object.keys(data).length > 0) {
          const role = data.role.type;
          if (role === 'staff') {
            commit('updateIndex', 0);
          }
          state.index = state.index || Number(window.localStorage.getItem('index'));
          if (state.index && state.index > 1) {
            commit('updataNavRouterDiff', state.index);
          } else {
            commit('updataRouterDiff', role);
          }
        }
        return data;
      });
    },

    /**
         * 获取角色列表
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    async roleList ({ commit, state, dispatch }, params, config) {
      const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;
      // return http.get(`${AJAX_URL_PREFIX}/accounts/user/roles/`, config).then((response) => {
      const queryParams = {
        ...{
          with_super: true,
          offset: 0,
          limit: 20
        },
        ...params
      };
      return http.get(`${AJAX_URL_PREFIX}/roles/grade_managers/?${json2Query(queryParams)}`).then(({ data }) => {
        const results = data.results || [];
        // results.forEach((item) => {
        //   if (item.type === 'system_manager') {
        //     const langManager = ['zh-cn'].includes(window.CUR_LANGUAGE) ? '系统管理员' : ' system administrator';
        //     item.name = `${item.name}${langManager}`;
        //   }
        // });
        commit('updateRoleListTotal', data.count || 0);
        commit('updateRoleList', results);
        return results;
      });
    },

    /**
         * 获取版本日志信息
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    versionLogInfo ({ commit, state, dispatch }, config) {
      const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;
      return http.get(`${AJAX_URL_PREFIX}/version_log/`, config).then((response) => {
        commit('updateVersion', response.data);
        return response.data;
      });
    },

    /**
         * 获取用户信息
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    allUserInfo ({ commit, state, dispatch }, config) {
      const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;
      return http.get(`${AJAX_URL_PREFIX}/accounts/users/`, config).then((response) => {
        commit('updateUsers', response.data);
        return response.data;
      });
    },

    /**
         * 获取新手指引
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getNoviceGuide ({ commit, state, dispatch }, config) {
      if (!store.getters.externalSystemsLayout.hideIamGuide) {
        const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;
        return http.get(`${AJAX_URL_PREFIX}/users/profile/newbie/`, config).then((response) => {
          commit('setNoviceGuide', response.data);
          return response.data;
        });
      }
    },

    /**
         * 新手指引的更改
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         * @param {Object} params
         *
         * @return {Promise} promise 对象
         */
    editNoviceGuide ({ commit, state, dispatch }, params, config) {
      const AJAX_URL_PREFIX = window.AJAX_URL_PREFIX;
      return http.post(`${AJAX_URL_PREFIX}/users/profile/newbie/`, params, config);
    },

    /**
         * get 请求
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object} params 请求参数
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    get ({ commit, state, dispatch }, params, config) {
      return http.get(`/app/index?invoke=get&${json2Query(params)}`, config);
    },

    /**
         * 获取需要动态展示的按钮或文案
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         * @param {Object?} config http config
         *
         * @return {Promise} promise 对象
         */
    getExternalSystemsLayout ({ commit, state, dispatch }, params, config) {
      const externalSystemsLayout = {
        hideIamHeader: true, // 第一层级头部导航
        hideIamSlider: true, // 第一层级侧边导航
        hideIamBreadCrumbs: true, // 第一层级面包屑
        hideIamGuide: true, // 隐藏所有guide的tooltip
        myPerm: { // 我的权限
          hideCustomTab: true, // 自定义权限tab - 1
          hideApplyBtn: true, // 申请权限按钮 - 1
          hideTemporaryCustomTab: true, // 临时权限tab -1
          renewal: { // 我的权限-权限续期
            hideCustomTab: true // 自定义权限tab - 2
          },
          transfer: { // 我的权限-权限交接
            hideTextBtn: true, // 交接历史文本按钮 - 3
            hideCustomData: true, // 自定义权限交接-3
            hideManagerData: true, // 管理员交接数据-3
            showUserGroupSearch: true, // 显示权限交接用户组查询-3
            setFooterBtnPadding: true // 设置内嵌页面权限交接底部按钮你编剧
          }
        },
        userGroup: { // 用户组
          addGroup: { // 用户组 - 添加用户组 - 添加权限抽屉
            hideAddTemplateTextBtn: true, // 右侧抽屉新增文本按钮-7.1
            AddUserGroupDiaLogUrl: '' // 用户组 - 添加用户组 - 组成员链接跳转
          },
          groupDetail: { // 用户组 - 组详情
            hideAddBtn: true, // 用户组-组权限-添加权限按钮-6
            hideEditBtn: true, // 用户组-组权限-编辑权限按钮-6
            hideDeleteBtn: true, // 用户组-组权限-删除权限按钮-6
            hideGroupName: true, // 用户组-组详情-隐藏组名称
            hideGroupDescEdit: true, // 用户组-组详情-隐藏组描述编辑
            hideCustomPerm: false, // 用户组-组权限-隐藏自定义权限相关信息
            hideGroupPermExpandTitle: true, // 用户组-组权限-隐藏自定义权限标题
            setMainLayoutHeight: true // 用户组-详情页面-区分主体高度
          }
        },
        // 我的申请
        myApply: {
          leftLayoutHeight: true, // 设置外部嵌套我的申请页面左侧主体内容高度
          rightLayoutHeight: true, // 设置外部嵌套我的申请页面右侧主体内容高度
          externalSystemParams: true // 设置获取我的申请嵌套页面url传参，根据id自动选中当前数据
        },
        // 设置项目最大可授权范围
        addMemberBoundary: {
          customFooterClass: true, // 设置项目最大可授权范围, 底部插槽自定义样式
          hideInfiniteTreeCount: true// 隐藏设置项目最大可授权范围左边拓扑树显示成员个数
        }
      };
      commit('setExternalSystemsLayout', externalSystemsLayout);
      const { externalSystemId } = params;
      return http.get(`${AJAX_URL_PREFIX}/systems/${externalSystemId}/custom_frontend_settings/`, config).then(response => {
        if (Array.from(response.data).length) {
          commit('setExternalSystemsLayout', response.data);
        } else {
          commit('setExternalSystemsLayout', externalSystemsLayout);
        }
        return response.data;
      });
    }
  }
});

/**
 * hack vuex dispatch, add third parameter `config` to the dispatch method
 *
 * @param {Object|string} _type vuex type
 * @param {Object} _payload vuex payload
 * @param {Object} config config 参数，主要指 http 的参数，详见 src/api/index initConfig
 *
 * @return {Promise} 执行请求的 promise
 */
store.dispatch = function (_type, _payload, config = {}) {
  const { type, payload } = unifyObjectStyle(_type, _payload);

  const action = { type, payload, config };
  const entry = store._actions[type];
  if (!entry) {
    if (NODE_ENV !== 'production') {
      console.error(`[vuex] unknown action type: ${type}`);
    }
    return;
  }

  store._actionSubscribers.forEach((sub) => {
    return sub(action, store.state);
  });

  return entry.length > 1 ? Promise.all(entry.map((handler) => handler(payload, config))) : entry[0](payload, config);
};

export default store;

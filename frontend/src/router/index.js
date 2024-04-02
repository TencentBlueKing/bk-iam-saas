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
import VueRouter from 'vue-router';

import store from '@/store';
import http from '@/api';
// import il8n from '@/language';
import preload from '@/common/preload';
import { bus } from '@/common/bus';
// import { existValue, getParamsValue, getTreeNode } from '@/common/util';
import { existValue, getParamsValue, getManagerMenuPerm } from '@/common/util';
import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';
import { messageError } from '@/common/bkmagic';

const SITE_URL = window.SITE_URL;

Vue.use(VueRouter);

let routes = [];

if (NODE_ENV === 'development') {
  routes = require('./ieod').routes;
} else {
  // eslint-disable-next-line
    routes = require(`./${VERSION}`).routes;
}

const router = new VueRouter({
  mode: 'history',
  routes: routes
});

const cancelRequest = async () => {
  const allRequest = http.queue.get();
  const requestQueue = allRequest.filter((request) => request.cancelWhenRouteChange);
  await http.cancel(requestQueue.map((request) => request.requestId));
};

let preloading = true;
let canceling = true;
let pageMethodExecuting = true;

/**
 * beforeEach 钩子函数
 */
export const beforeEach = async (to, from, next) => {
  // 外部嵌入页面需要请求配置项
  if (existValue('externalApp')) {
    const externalSystemId = getParamsValue('system_id');
    store.commit('updateSystemId', externalSystemId);
    await fetchExternalSystemsLayout(externalSystemId);
  }

  bus.$emit('close-apply-perm-modal');

  canceling = true;
  await cancelRequest();
  canceling = false;

  let curRole = store.state.user.role.type;
  let navIndex = store.state.index || Number(window.localStorage.getItem('index') || 0);
  let currentRoleId = String(to.query.current_role_id || '').trim();
  let curRoleId = store.state.curRoleId;
  // 检验有系管没超管身份
  let hasManagerPerm = '';
  let defaultRoute = ['my-perm', 'user-group', 'audit', 'user'];

  async function getExternalRole () {
    const { role_id: externalRoleId } = to.query;
    currentRoleId = externalRoleId;
    curRoleId = externalRoleId;
    try {
      await store.dispatch('role/updateCurrentRole', { id: Number(externalRoleId) });
      await store.dispatch('userInfo');
      next();
    } catch (error) {
      const { data, message, statusText } = error;
      messageError(message || data.msg || statusText);
    }
    // const currentRole = await getTreeNode(+externalRoleId, roleList);
    // 内嵌页面会直接屏蔽
    // if (currentRole) {
    //     await store.dispatch('role/updateCurrentRole', { id: +externalRoleId });
    //     await store.dispatch('userInfo');
    //     curRole = currentRole.type;
    //     next();
    // } else {
    //     messageError(il8n('common', '您没有该角色权限，无法切换到该角色'));
    // }
  }

  async function getManagerInfo () {
    const { code } = await store.dispatch('role/updateCurrentRole', { id: Number(currentRoleId) });
    if (code === 0) {
      const { role } = await store.dispatch('userInfo');
      curRole = role.type;
    } else {
      next({ path: `${SITE_URL}${defaultRoute[navIndex]}` });
    }
  }

  // 处理平台管理超管和系管都可以进入，但访问菜单权限不一致
  async function getPlatManageMenu () {
    hasManagerPerm = '';
    let roleList = store.state.roleList;
    if (roleList.length > 0) {
      // 有系统管理员身份没超管身份
      hasManagerPerm = getManagerMenuPerm(roleList);
    } else {
      roleList = await store.dispatch('roleList', {
        cancelWhenRouteChange: false,
        cancelPrevious: false
      });
    }
    // 有系统管理员身份没超管身份
    hasManagerPerm = getManagerMenuPerm(roleList);
    if (['hasSystemNoSuperManager'].includes(hasManagerPerm)) {
      hasManagerPerm = 'hasSystemNoSuperManager';
      defaultRoute = ['my-perm', 'user-group', 'audit', 'resourcePermiss'];
    }
  }

  // 根据不同权限处理不同的导航栏索引
  function navDiffMenuIndex (index) {
    navIndex = index;
    store.commit('updateIndex', index);
    window.localStorage.setItem('index', index);
  }

  // 如果进入没有权限，重新找roleList, 蓝盾交互不需要判断
  const isEXternal = !(existValue('externalApp') || to.query.hasOwnProperty('role_id'));
  if (['', 'staff'].includes(curRole) && navIndex > 0 && isEXternal) {
    const roleList = await store.dispatch('roleList', {
      cancelWhenRouteChange: false,
      cancelPrevious: false
    });
    if (roleList.length) {
      const { id } = roleList[0];
      currentRoleId = id;
      curRoleId = id;
      store.commit('updateCurRoleId', id);
      await getManagerInfo();
    }
  }

  if (['applyJoinUserGroup', 'applyCustomPerm', 'myManageSpace', 'myPerm', 'permTransfer', 'permRenewal'].includes(to.name)
      || (['permRenewal'].includes(to.name) && to.query.source === 'email')) {
    await store.dispatch('role/updateCurrentRole', { id: 0 });
    await store.dispatch('userInfo');
    curRole = 'staff';
    navDiffMenuIndex(0);
  }
 
  if (['userGroup', 'permTemplate', 'approvalProcess'].includes(to.name)) {
    await store.dispatch('role/updateCurrentRole', { id: curRoleId });
    navDiffMenuIndex(1);
  }

  if (to.name === 'userGroupDetail') {
    navDiffMenuIndex(1);
    store.dispatch('versionLogInfo');
    if (existValue('externalApp') && to.query.hasOwnProperty('role_id')) {
      getExternalRole();
    } else {
      if (currentRoleId) {
        // const currentRole = roleList.find((item) => String(item.id) === currentRoleId);
        // 从之前的拓扑接口更换成一级、二级接口
        // const currentRole = getTreeNode(+currentRoleId, roleList);
        await getManagerInfo();
      } else {
        const noFrom = !from.name;
        // 说明是刷新页面
        if (noFrom) {
          if (existValue('externalApp') || to.query.noFrom) {
            next();
          } else {
            // next();
            next({ path: `${SITE_URL}${defaultRoute[navIndex]}` });
          }
        } else {
          next();
        }
      }
    }
  } else if (to.name === 'userGroup') {
    store.dispatch('versionLogInfo');
    if (currentRoleId) {
      await getManagerInfo();
    } else {
      if (existValue('externalApp')) { // 外部嵌入页面
        next();
      } else {
        if (curRole === 'staff') {
          // 单独处理返回个人staff不需要重定向我的权限的路由
          const routeNavMap = [
            [(name) => ['myManageSpace'].includes(name), () => next()],
            [(name) => ['ratingManager'].includes(name), () => next({ path: `${SITE_URL}${to.fullPath}` })]
          ];
          const getRouteNav = routeNavMap.find((item) => item[0](to.name));
          getRouteNav ? getRouteNav[1]() : next({ path: `${SITE_URL}my-perm` });
          // next({ path: `${SITE_URL}my-perm` });
        } else {
          next();
        }
      }
    }
  } else {
    // 邮件点击续期跳转过来的链接需要做身份的前置判断
    if (to.name === 'groupPermRenewal' && to.query.source === 'email' && currentRoleId) {
      // await store.dispatch('role/updateCurrentRole', { id: +currentRoleId });
      // const { role } = await store.dispatch('userInfo');
      // curRole = role.type;
      await getManagerInfo();
      navDiffMenuIndex(1);
    }

    if (existValue('externalApp') && to.query.hasOwnProperty('role_id')) {
      if (['groupPermRenewal', 'userGroup', 'userGroupDetail', 'createUserGroup', 'userGroupPermDetail'].includes(to.name)) {
        navDiffMenuIndex(1);
      }
      getExternalRole();
    }

    let difference = [];
    if (navIndex === 1) {
      difference = getRouterDiff(curRole);
    } else {
      // 目前只有平台管理需要根据管理员最大身份处理路由权限
      if ([3, '3'].includes(navIndex)) {
        await getPlatManageMenu();
      }
      difference = getNavRouterDiff(navIndex, hasManagerPerm);
    }
    if (difference.length) {
      store.dispatch('versionLogInfo');
      if (difference.includes(to.name)) {
        store.commit('setHeaderTitle', '');
        window.localStorage.removeItem('iam-header-title-cache');
        window.localStorage.removeItem('iam-header-name-cache');
        if (curRole === 'staff' || curRole === '') {
          if (existValue('externalApp')) { // 外部嵌入页面
            next();
          } else {
            // 单独处理返回个人staff不需要重定向我的权限的路由
            const routeNavMap = [
              [(name) => ['myManageSpace'].includes(name), () => next()],
              [(name) => ['ratingManager'].includes(name), () => next({ path: `${SITE_URL}${to.fullPath}` })]
            ];
            const getRouteNav = routeNavMap.find((item) => item[0](to.name));
            getRouteNav ? getRouteNav[1]() : next({ path: `${SITE_URL}my-perm` });
          }
        } else {
          if (['groupPermRenewal', 'userGroup', 'userGroupDetail', 'createUserGroup', 'userGroupPermDetail'].includes(to.name)) {
            store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
            next();
          }
                    
          if (to.name === 'apply') {
            store.commit('updateIndex', 0);
            window.localStorage.setItem('index', 0);
            next();
          } else {
            if (existValue('externalApp')) {
              next();
            } else {
              next({ path: `${SITE_URL}${defaultRoute[navIndex]}` });
            }
            // next({ path: `${SITE_URL}user-group` });
          }
        }
        // next();
      } else {
        const noFrom = !from.name;
        // permTemplateCreate
        if (['permTemplateDetail', 'permTemplateEdit', 'permTemplateDiff'].includes(to.name) && noFrom) {
          next({ path: `${SITE_URL}perm-template` });
          // } else if (['createUserGroup', 'userGroupDetail'].includes(to.name) && noFrom) {
          // } else if (['createUserGroup'].includes(to.name) && noFrom) {
        } else if (['createUserGroup'].includes(to.name)) {
          if (noFrom) {
            if (existValue('externalApp')) {
              next();
            } else {
              next({ path: `${SITE_URL}${defaultRoute[navIndex]}` });
            }
          } else {
            next();
          }
          // if (existValue('externalApp')) { // 如果是外部嵌入的页面
          //     next();
          // } else {
          //     next({ path: `${SITE_URL}user-group` });
          // }
          // 这里刷新staff菜单会跳转分级管理员列表，所以单独处理
        } else if (['gradingAdminDetail', 'gradingAdminCreate'].includes(to.name) && !['', 'staff'].includes(curRole)) {
          if (noFrom) {
            next({ path: `${SITE_URL}rating-manager` });
          } else {
            next();
          }
        } else if (['gradingAdminEdit', 'myPerm'].includes(to.name)) {
          next();
        } else {
          next();
        }
      }
    } else {
      next();
    }
  }

  // 解决 sideslider 组件跳转后导致滚动条失效
  const node = document.documentElement;
  const className = 'bk-sideslider-show has-sideslider-padding';
  const classNames = className.split(' ');
  const rtrim = /^\s+|\s+$/;
  /* eslint-disable */
    let setClass = ' ' + node.className + ' ';

    classNames.forEach((cl) => {
        /* eslint-disable */
        setClass = setClass.replace(' ' + cl + ' ', ' ');
    });
    node.className = setClass.replace(rtrim, '');

    setTimeout(() => {
        window.scroll(0, 0);
    }, 100);
};

export const afterEach = async (to, from) => {
    // permTemplateDetail 和 permTransfer 不需要统一处理 mainContentLoading
    store.commit('setMainContentLoading', true && !['permTemplateDetail', 'permTransfer'].includes(to.name));
    store.commit('setBackRouter', '');
    preloading = true;
    if (to.query.role_id && !existValue('externalApp')) {
        await store.dispatch('role/updateCurrentRole', { id: Number(to.query.role_id) });
    }
    await preload();
    preloading = false;
    const pageDataMethods = [];
    const routerList = to.matched;
    routerList.forEach((r) => {
        const fetchPageData = r.instances.default && r.instances.default.fetchPageData;
        if (fetchPageData && typeof fetchPageData === 'function') {
            pageDataMethods.push(r.instances.default.fetchPageData());
        }
    });

    pageMethodExecuting = true;

    const headerTitle = window.localStorage.getItem('iam-header-title-cache');

    store.commit('setHeaderTitle', (to.meta && to.meta.headerTitle) || store.getters.headerTitle || headerTitle || '');

    store.commit('setBackRouter', (to.meta && to.meta.backRouter) || store.getters.backRouter || '');

    await Promise.all(pageDataMethods);

    pageMethodExecuting = false;

    if (!preloading && !canceling && !pageMethodExecuting && to.name !== 'permTemplateDetail') {
        store.commit('setMainContentLoading', false);
    }
};

const fetchExternalSystemsLayout = async (externalSystemId) => {
    await store.dispatch('getExternalSystemsLayout', {externalSystemId});
}

router.beforeEach(beforeEach);
router.afterEach(afterEach);

export default router;

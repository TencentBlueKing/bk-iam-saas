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
import { existValue, getParamsValue, getRoutePath } from '@/common/util';
// import { existValue, getParamsValue, getManagerMenuPerm } from '@/common/util';
import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';
import { messageError } from '@/common/bkmagic';
import { connectToMain } from '@blueking/sub-saas/dist/main.js';

const SITE_URL = getRoutePath(window.SITE_URL);

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
  const storeRoleId = store.state.user.role.id;
  let navIndex = store.state.index || Number(window.localStorage.getItem('index') || 0);
  let currentRoleId = String(to.query.current_role_id || '').trim();
  let curRoleId = store.state.curRoleId;
  // 检验有系管没超管身份
  const hasManagerPerm = '';
  const defaultRoute = ['my-perm', 'user-group', 'audit', 'user'];

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
    if (Number(currentRoleId) === Number(storeRoleId)) {
      return;
    }
    const { code } = await store.dispatch('role/updateCurrentRole', { id: Number(currentRoleId) });
    if (code === 0) {
      const { role } = await store.dispatch('userInfo');
      curRole = role.type;
    } else {
      next({ path: `${SITE_URL}${defaultRoute[navIndex]}` });
    }
  }

  // 处理平台管理超管和系管都可以进入，但访问菜单权限不一致
  // 暂时注释掉后期开放
  // async function getPlatManageMenu () {
  //   hasManagerPerm = '';
  //   let roleList = store.state.roleList;
  //   if (roleList.length > 0) {
  // 有系统管理员身份没超管身份
  //     hasManagerPerm = getManagerMenuPerm(roleList);
  //   } else {
  //     roleList = await store.dispatch('roleList', {
  //       cancelWhenRouteChange: false,
  //       cancelPrevious: false
  //     });
  //   }
  // 有系统管理员身份没超管身份
  //   hasManagerPerm = getManagerMenuPerm(roleList);
  //   if (['hasSystemNoSuperManager'].includes(hasManagerPerm)) {
  //     hasManagerPerm = 'hasSystemNoSuperManager';
  //     defaultRoute = ['my-perm', 'user-group', 'audit', 'resourcePermiss'];
  //   }
  // }

  // 根据不同权限处理不同的导航栏索引
  function navDiffMenuIndex (index) {
    navIndex = index;
    store.commit('updateIndex', index);
    window.localStorage.setItem('index', index);
  }

  // 设置roleList里查找不到的管理员身份
  function setStaffOrSubSet ({ roleId, index }) {
    [curRoleId, currentRoleId] = [roleId, roleId];
    store.commit('updateCurRoleId', roleId);
    store.commit('updateNavId', roleId);
    navDiffMenuIndex(index);
  }

  let curRoleList = [];
  const noFrom = !from.name;
  // 是否是嵌入系统
  const isNoIframe = !(existValue('externalApp') || to.query.hasOwnProperty('role_id'));
  // 如果进入没有权限
  const isNoPerm = ['', 'staff'].includes(curRole) && navIndex > 0;
  // 跳转的页面是否需要非管理员用户界面
  let isStaff = !getNavRouterDiff(0).includes(to.name) || (['permRenewal'].includes(to.name) && ['email', 'notification'].includes(to.query.source));
  // 跳转的页面是否需要非超级管理员用户界面
  const isAudit = !getNavRouterDiff(2).includes(to.name);
  const isPlatForm = !getNavRouterDiff(3).includes(to.name);
  // 处理新标签页链接是管理员页面 ，但是上次用户信息是staff
  let isManagerPage = !isStaff && noFrom && navIndex < 1;
  // 如果进入没有权限或者是拿到的上次用户信息是非管理员身份但是新开标签页是管理员页面， 蓝盾交互不需要判断
  if ((isNoPerm || isManagerPage || to.query.role_name) && isNoIframe) {
    const roleList = await store.dispatch('roleList', {
      cancelWhenRouteChange: false,
      cancelPrevious: false,
      limit: 100,
      name: to.query.role_name
    });
    // roleList只能查找根节点的管理空间，比如系管、超管、分管，如果不存在roleList代表是个人用户或者是二级管理空间
    const isManager = roleList && roleList.length > 0;
    if (isManager) {
      curRoleList = [...roleList];
      // 只有管理员页面才需要提供默认管理员身份
      if (navIndex > 0 && !isStaff) {
        const { id } = roleList[0];
        [curRoleId, currentRoleId] = [id, id];
        store.commit('updateCurRoleId', id);
        store.commit('updateNavId', id);
        await getManagerInfo();
      }
    } else {
      // 如果不存在roleList，查找是不是属于二级管理空间
      const res = await store.dispatch('spaceManage/getSearchManagerList', {
        page: 1,
        page_size: 100,
        name: to.query.role_name
      });
      const { code, data = {} } = res || {};
      if (code === 0 && data.count > 0) {
        isStaff = false;
        isManagerPage = true;
        setStaffOrSubSet({ roleId: data.results[0].id, index: 1 });
        await getManagerInfo();
      } else {
        isStaff = true;
        isManagerPage = false;
        setStaffOrSubSet({ roleId: 0, index: 0 });
        next({ path: `${SITE_URL}${defaultRoute[0]}` });
      }
    }
  }
  // 因为管理空间下菜单还需要细分具体管理员身份，所以getRouterDiff用于分配管理空间导航栏下的路由，getNavRouterDiff用于分配其他几个导航栏的路由
  // 处理非管理空间模块路由跳转校验
  if (navIndex !== 1 || (navIndex > 0 && isStaff)) {
    if (isStaff) {
      curRoleId = 0;
      navIndex = 0;
      store.commit('updateCurRoleId', 0);
      store.commit('updateNavId', 0);
    }
    currentRoleId = curRoleId;
    navDiffMenuIndex(navIndex);
    await getManagerInfo();
  } else {
    //  处理管理空间模块路由跳转校验
    if (!['', 'staff'].includes(curRole) && curRoleId > 0) {
      // 查找当页面是否在管理空间模块
      const isManageSpace = !getRouterDiff(curRole).includes(to.name);
      if (!isManageSpace) {
        const allNavIndex = [0, 2, 3];
        // 根据路由名称筛选当前页面所在模块位置
        const curPageIndex = allNavIndex.findIndex((v) => !getNavRouterDiff(v).includes(to.name));
        if (curPageIndex > -1) {
          if (curPageIndex === 0) {
            curRoleId = 0;
            currentRoleId = 0;
          }
          navIndex = allNavIndex[curPageIndex];
        }
      }
      currentRoleId = curRoleId;
      navDiffMenuIndex(navIndex);
      await getManagerInfo();
    }
  }
  if (to.name === 'userGroupDetail') {
    navDiffMenuIndex(1);
    if (existValue('externalApp') && to.query.hasOwnProperty('role_id')) {
      getExternalRole();
    } else {
      // 说明是刷新页面
      if (noFrom) {
        if (existValue('externalApp') || to.query.noFrom) {
          next();
        } else {
          // 处理从staff界面跳转到用户组详情，需要提供默认管理员身份
          if ((curRoleId === 0 || ['', 'staff'].includes(curRole)) && curRoleList.length > 0) {
            const { id } = curRoleList[0];
            [curRoleId, currentRoleId] = [id, id];
            store.commit('updateCurRoleId', id);
            store.commit('updateNavId', id);
            await getManagerInfo();
          }
          next();
          // next({ path: `${SITE_URL}${defaultRoute[navIndex]}` });
        }
      } else {
        next();
      }
    }
  } else {
    // 邮件点击续期跳转过来的链接需要做身份的前置判断
    if (to.name === 'groupPermRenewal' && ['email', 'notification'].includes(to.query.source) && currentRoleId) {
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
      // if ([3].includes(Number(navIndex))) {
      //   await getPlatManageMenu();
      // }
      difference = getNavRouterDiff(navIndex, hasManagerPerm);
    }
    if (difference.length) {
      if (difference.includes(to.name)) {
        store.commit('setHeaderTitle', '');
        window.localStorage.removeItem('iam-header-title-cache');
        window.localStorage.removeItem('iam-header-name-cache');
        if (['', 'staff'].includes(curRole)) {
          if (existValue('externalApp')) { // 外部嵌入页面
            next();
          } else {
            // 单独处理返回个人staff不需要重定向我的权限的路由
            const routeNavMap = [
              [(name) => !getNavRouterDiff(0).includes(name), () => next()]
            ];
            const getRouteNav = routeNavMap.find((item) => item[0](to.name));
            if (getRouteNav) {
              getRouteNav[1]();
              return;
            }
            if (isManagerPage) {
              const superData = curRoleList.find((v) => ['super_manager'].includes(v.type));
              const managerData = curRoleList.find((v) => !['staff'].includes(v.type));
              // 如果跳转的页面必须是超管身份才能访问
              if (superData && (isAudit || isPlatForm)) {
                const { id } = superData;
                [currentRoleId, curRoleId] = [id, id];
                navDiffMenuIndex(isAudit ? 2 : 3);
                await getManagerInfo();
                next();
                return;
              }
              // 如果跳转的页面只需要是管理员即可访问
              if (managerData) {
                const { type } = managerData;
                let isManageSpace = false;
                let curManagerData = {};
                isManageSpace = !getRouterDiff(type).includes(to.name);
                curManagerData = Object.assign({}, managerData);
                // 没找到这个页面也可能是管理空间导航栏下页面限制了具体管理员身份才能访问
                const systemManagerData = curRoleList.find((v) => ['system_manager'].includes(v.type));
                const ratingManagerData = curRoleList.find((v) => ['rating_manager'].includes(v.type));
                const subSetManager = curRoleList.find((v) => ['subset_manager'].includes(v.type));
                if (systemManagerData && !isManageSpace) {
                  curManagerData = Object.assign({}, systemManagerData);
                  isManageSpace = !getRouterDiff(systemManagerData.type).includes(to.name);
                }
                if (ratingManagerData && !isManageSpace) {
                  curManagerData = Object.assign({}, ratingManagerData);
                  isManageSpace = !getRouterDiff(ratingManagerData.type).includes(to.name);
                }
                if (subSetManager && !isManageSpace) {
                  curManagerData = Object.assign({}, subSetManager);
                  isManageSpace = !getRouterDiff(ratingManagerData.type).includes(to.name);
                }
                if (isManageSpace && curManagerData.id) {
                  [currentRoleId, curRoleId] = [curManagerData.id, curManagerData.id];
                  navDiffMenuIndex(1);
                  await getManagerInfo();
                  next();
                  return;
                }
              }
            }
            // getRouteNav ? getRouteNav[1]() : next({ path: `${SITE_URL}my-perm` });
          }
        } else {
          if (['groupPermRenewal', 'userGroup', 'userGroupDetail', 'createUserGroup', 'userGroupPermDetail'].includes(to.name)) {
            store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
            next();
          }
          if (existValue('externalApp')) {
            next();
          } else {
            next({ path: `${SITE_URL}${defaultRoute[navIndex]}` });
          }
          // next({ path: `${SITE_URL}user-group` });
        }
        // next();
      } else {
        if (['permTemplateDetail', 'permTemplateEdit', 'permTemplateDiff'].includes(to.name) && noFrom) {
          next({ path: `${SITE_URL}perm-template` });
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

connectToMain(router);

export default router;
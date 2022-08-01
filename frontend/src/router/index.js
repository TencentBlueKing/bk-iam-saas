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

import { bus } from '@/common/bus';
import store from '@/store';
import http from '@/api';
import preload from '@/common/preload';
import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';

const SITE_URL = window.SITE_URL;

Vue.use(VueRouter);

let routes = [];

if (NODE_ENV === 'development') {
    routes = require('./ieod').routes;
} else {
    // eslint-disable-next-line
    routes = require(`./${VERSION}`).routes
}

const router = new VueRouter({
    mode: 'history',
    routes: routes
});

const cancelRequest = async () => {
    const allRequest = http.queue.get();
    const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange);
    await http.cancel(requestQueue.map(request => request.requestId));
};

let preloading = true;
let canceling = true;
let pageMethodExecuting = true;

/**
 * beforeEach 钩子函数
 */
export const beforeEach = async (to, from, next) => {
    bus.$emit('close-apply-perm-modal');

    canceling = true;
    await cancelRequest();
    canceling = false;

    let curRole = store.state.user.role.type;
    const navIndex = store.state.index || Number(window.localStorage.getItem('index') || 0);
    const currentRoleId = String(to.query.current_role_id || '').trim();

    if (to.name === 'userGroupDetail') {
        store.dispatch('versionLogInfo');
        if (currentRoleId) {
            const roleList = await store.dispatch('roleList', {
                cancelWhenRouteChange: false,
                cancelPrevious: false
            });
            const currentRole = roleList.find(item => String(item.id) === currentRoleId);
            if (currentRole) {
                await store.dispatch('role/updateCurrentRole', { id: currentRoleId });
                await store.dispatch('userInfo');
                curRole = currentRole.type;
                next();
            } else {
                next({ path: `${SITE_URL}user-group` });
            }
        } else {
            const noFrom = !from.name;
            // 说明是刷新页面
            if (noFrom) {
                next({ path: `${SITE_URL}user-group` });
            } else {
                next();
            }
        }
    } else if (to.name === 'userGroup') {
        store.dispatch('versionLogInfo');
        if (currentRoleId) {
            const roleList = await store.dispatch('roleList', {
                cancelWhenRouteChange: false,
                cancelPrevious: false
            });
            const currentRole = roleList.find(item => String(item.id) === currentRoleId);
            if (currentRole) {
                await store.dispatch('role/updateCurrentRole', { id: currentRoleId });
                await store.dispatch('userInfo');
                curRole = currentRole.type;
                next();
            } else {
                next({ path: `${SITE_URL}user-group` });
            }
        } else {
            if (curRole === 'staff') {
                next({ path: `${SITE_URL}my-perm` });
            } else {
                next();
            }
        }
    } else {
        // 邮件点击续期跳转过来的链接需要做身份的前置判断
        if (to.name === 'groupPermRenewal' && to.query.source === 'email' && currentRoleId) {
            await store.dispatch('role/updateCurrentRole', { id: currentRoleId });
            await store.dispatch('userInfo');
            curRole = to.query.role_type;
        }

        if (to.name === 'permRenewal' && to.query.source === 'email') {
            await store.dispatch('role/updateCurrentRole', { id: 0 });
            await store.dispatch('userInfo');
            curRole = 'staff';
        }

        if (to.name === 'applyCustomPerm') {
            await store.dispatch('role/updateCurrentRole', { id: 0 });
            await store.dispatch('userInfo');
            curRole = 'staff';
        }

        if (curRole === 'staff') {
            store.commit('updateIndex', 0);
            window.localStorage.setItem('index', 0);
        }

        if (to.name === 'gradingAdminEdit') {
            await store.dispatch('role/updateCurrentRole', { id: 0 });
            await store.dispatch('userInfo');
            if (to.params.id) {
                store.commit('updateNavId', to.params.id);
            }
            curRole = 'staff';
        }

        let difference = [];
        if (navIndex === 1) {
            difference = getRouterDiff(curRole);
        } else {
            difference = getNavRouterDiff(navIndex);
        }
        
        if (difference.length) {
            console.log('to', to);
            store.dispatch('versionLogInfo');
            if (difference.includes(to.name)) {
                store.commit('setHeaderTitle', '');
                window.localStorage.removeItem('iam-header-title-cache');
                window.localStorage.removeItem('iam-header-name-cache');
                if (curRole === 'staff' || curRole === '') {
                    next({ path: `${SITE_URL}my-perm` });
                } else {
                    next({ path: `${SITE_URL}user-group` });
                }
                // next();
            } else {
                const noFrom = !from.name;
                // permTemplateCreate
                if (['permTemplateDetail', 'permTemplateEdit', 'permTemplateDiff'].includes(to.name) && noFrom) {
                    next({ path: `${SITE_URL}perm-template` });
                    // } else if (['createUserGroup', 'userGroupDetail'].includes(to.name) && noFrom) {
                } else if (['createUserGroup'].includes(to.name) && noFrom) {
                    next({ path: `${SITE_URL}user-group` });
                } else if (
                    ['gradingAdminDetail', 'gradingAdminCreate'].includes(to.name) && noFrom
                ) {
                    next({ path: `${SITE_URL}rating-manager` });
                } else if (['gradingAdminEdit'].includes(to.name) && noFrom) {
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

    classNames.forEach(cl => {
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
    store.commit('setMainContentLoading', true && to.name !== 'permTemplateDetail' && to.name !== 'permTransfer');
    store.commit('setBackRouter', '');
    preloading = true;
    await preload();
    preloading = false;
    const pageDataMethods = [];
    const routerList = to.matched;
    routerList.forEach(r => {
        const fetchPageData = r.instances.default && r.instances.default.fetchPageData;
        if (fetchPageData && typeof fetchPageData === 'function') {
            pageDataMethods.push(r.instances.default.fetchPageData());
        }
    });

    pageMethodExecuting = true;

    const headerTitle = window.localStorage.getItem('iam-header-title-cache');

    store.commit(
        'setHeaderTitle',
        (to.meta && to.meta.headerTitle) || store.getters.headerTitle || headerTitle || ''
    );

    store.commit(
        'setBackRouter',
        (to.meta && to.meta.backRouter) || store.getters.backRouter || ''
    );

    await Promise.all(pageDataMethods);

    pageMethodExecuting = false;

    if (!preloading && !canceling && !pageMethodExecuting && to.name !== 'permTemplateDetail') {
        store.commit('setMainContentLoading', false);
    }
};

router.beforeEach(beforeEach);
router.afterEach(afterEach);

export default router;

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

import store from '@/store';

/**
 * 获取user信息
 *
 * @return {Promise} promise 对象
 */
function getUser () {
  return store.dispatch('userInfo', {
    cancelWhenRouteChange: false
    // fromCache: true
    // cancelPrevious: false
  });
}

/**
 * 获取角色列表
 *
 * @return {Promise} promise 对象
 */
function getRoleList () {
  return store.dispatch('roleList', {
    cancelWhenRouteChange: false
    // fromCache: true
    // cancelPrevious: false
  });
}

/**
 * 获取新手指引标识
 *
 * @return {Promise} promise 对象
 */
function getNoviceGuide () {
  return store.dispatch('getNoviceGuide', {
    cancelWhenRouteChange: false
    // fromCache: true
    // cancelPrevious: false
  });
}

export default function () {
  Promise.all([
    getUser(),
    getNoviceGuide(),
    getRoleList()
  ]);
}

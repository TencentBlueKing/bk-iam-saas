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

import _ from 'lodash';
export default class Instance {
  // flag = '' 为默认拉取，flag = 'add' 为新添加的
  // instanceNotDisabled: instance 不允许 disabled
  constructor (payload, flag = 'add', instanceNotDisabled = false) {
    this.name = payload.name || '';
    this.type = payload.type || '';
    this.flag = flag;
    this.instanceNotDisabled = instanceNotDisabled;
    this.initPath(payload, flag, instanceNotDisabled);
    this.initParamsPath(payload, flag, instanceNotDisabled);
  }

  initPath (payload, flag, instanceNotDisabled) {
    if (!payload.path) {
      this.path = [];
      return;
    }
    payload.path.forEach(item => {
      const isDefaultFetch = item.some(v => v.tag === 'add');
      item.forEach(subItem => {
        if (instanceNotDisabled) { // 如果instanceNotDisabled被传入了true, 所有的数据disabled都会变成false
          subItem.disabled = false;
        } else {
          // subItem.disabled = isDefaultFetch ? false : flag === ''
          // subItem.disabled = !isDefaultFetch
          if (['', 'custom'].includes(flag)) {
            subItem.disabled = !isDefaultFetch;
          } else {
            subItem.disabled = false;
          }
        }
      });
    });
    this.path = _.cloneDeep(payload.path);
  }

  // 接口请求所需参数
  initParamsPath (payload, flag, instanceNotDisabled) {
    if (!payload.path) {
      this.paths = [];
      return;
    }
    if (payload.paths && payload.paths.length > 0) {
      payload.paths.forEach(item => {
        const isDefaultFetch = item.some(v => v.tag === 'add');
        item.forEach(subItem => {
          if (instanceNotDisabled) {
            subItem.disabled = false;
          } else {
            // subItem.disabled = isDefaultFetch ? false : flag === ''
            // subItem.disabled = !isDefaultFetch
            if (['', 'custom'].includes(flag)) {
              subItem.disabled = !isDefaultFetch;
            } else {
              subItem.disabled = false;
            }
          }
        });
      });
      this.paths = _.cloneDeep(payload.paths);
    } else {
      payload.path.forEach(item => {
        const isDefaultFetch = item.some(v => v.tag === 'add');
        item.forEach(subItem => {
          if (instanceNotDisabled) {
            subItem.disabled = false;
          } else {
            // subItem.disabled = isDefaultFetch ? false : flag === ''
            // subItem.disabled = !isDefaultFetch
            if (['', 'custom'].includes(flag)) {
              subItem.disabled = !isDefaultFetch;
            } else {
              subItem.disabled = false;
            }
          }
        });
      });
      this.paths = _.cloneDeep(payload.path);
    }
  }

  get displayPath () {
    if (!this.path || this.path.length < 1) {
      return [];
    }
    const tempList = [];
    this.path.forEach(item => {
      const len = item.length;
      const displayName = item.map(sub => sub.name).join('/');
      const tempPath = item.filter(v => v.id !== '*');
      if (!tempList.some(sub => sub.id === item[len - 1].id && item[len - 1].id !== '*')) {
        let disabled = false;
        if (this.instanceNotDisabled) {
          disabled = false;
        } else {
          disabled = ['', 'custom'].includes(this.flag) ? !item.some(v => v.tag === 'add') : false;
        }
        tempList.push({
          name: item[len - 1].name,
          id: item[len - 1].id,
          level: len - 1,
          type: item[len - 1].type,
          parentChain: tempPath.slice(0, tempPath.length - 1),
          // disabled: item.some(v => v.tag === 'add') ? false : item.some(subItem => subItem.disabled),
          disabled: disabled,
          display_name: displayName
        });
      }
    });
    return tempList;
  }
}

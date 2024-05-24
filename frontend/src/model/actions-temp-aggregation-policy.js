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
import { cloneDeep } from 'lodash';
import { il8n, language } from '@/language';

export default class ActionTempAggregationPolicy {
  constructor (payload) {
    this.isAggregate = true;
    this.canPaste = false;
    // 是否需要展示无限制
    this.isNeedNoLimited = payload.isNeedNoLimited || false;
    // 是否是无限制操作
    this.isNoLimited = payload.isNoLimited || false;
    this.isError = payload.isError || false;
    this.selectedIndex = payload.selectedIndex || 0;
    this.tag = payload.tag || 'add';
    this.aggregationId = payload.aggregationId || '';
    this.mode_type = payload.mode_type || '';
    this.system_id = payload.actions.length > 0 ? payload.actions[0].system_id : '';
    this.system_name = payload.actions.length > 0 ? payload.actions[0].system_name || '' : '';
    this.actions = payload.actions || [];
    this.instancesDisplayData = payload.instancesDisplayData || {};
    this.aggregateResourceType = payload.aggregate_resource_types || payload.aggregateResourceType || [];
    this.instances = payload.instances || [];
    this.instancesBackup = cloneDeep(this.instances);
    this.initDetailData(this.actions);
  }

  initDetailData (payload) {
    if (payload.length < 1) {
      this.detail = {};
      return;
    }
    this.detail = payload[0];
  }

  get empty () {
    if (this.isNeedNoLimited) {
      if (this.instances.length === 1 && this.instances[0] === 'none') {
        return true;
      }
      return false;
    } else {
      return this.instances.length < 1;
    }
  }

  get value () {
    if (this.empty) {
      return il8n('verify', '请选择');
    }
    if ((this.isNoLimited || (!this.instances.length && !['add'].includes(this.tag)))) {
      return il8n('common', '无限制');
    }
    let str = '';
    this.aggregateResourceType.length && this.aggregateResourceType.forEach(item => {
      if (this.instancesDisplayData[item.id]) {
        if (this.instancesDisplayData[item.id].length > 1) {
          for (const key in this.instancesDisplayData) {
            if (item.id === key) {
              str = language === 'zh-cn' ? `${str}，已选择<span style='color: #3a84ff; font-weight: 700;'> ${this.instancesDisplayData[item.id].length} </span>个${item.name}` : `${str}, selected <span style='color: #3a84ff; font-weight: 700;'> ${this.instancesDisplayData[item.id].length}</span> ${item.name}(s)`;
              Vue.set(item, 'displayValue', str.substring(1, str.length));
              str = '';
            }
          }
        } else {
          // 这里防止切换tab下存在空数据，需要重新判断下
          if (this.instancesDisplayData[item.id] && this.instancesDisplayData[item.id].length === 1) {
            str = `${str}${il8n('common', '，')}${this.instancesDisplayData[item.id][0].name}`;
          }
          Vue.set(item, 'displayValue', str.substring(1, str.length));
          str = '';
        }
      } else {
        this.instancesDisplayData[item.id] = [];
        Vue.set(item, 'displayValue', '');
        str = '';
      }
    });
    const aggregateResourceType = cloneDeep(this.aggregateResourceType.map(item => item.displayValue));
    return aggregateResourceType.join();
  }

  get name () {
    if (this.actions.length > 0) {
      return this.actions.map(item => item.name).join('，');
    }
    return '';
  }

  get key () {
    if (this.actions.length > 0) {
      return this.actions.map(item => item.id).join('');
    }
    return '';
  }
}

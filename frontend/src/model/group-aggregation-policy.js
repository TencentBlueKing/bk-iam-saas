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
import _ from 'lodash';
import { il8n, language } from '@/language';
import { CUSTOM_PERM_TEMPLATE_ID } from '@/common/constants';
export default class GroupAggregationPolicy {
  constructor (payload) {
    this.isError = payload.isError || false;
    this.actions = payload.actions || [];
    this.instancesDisplayData = payload.instancesDisplayData || {};
    this.aggregateResourceType = payload.aggregate_resource_types || payload.aggregateResourceType || [];
    this.instances = payload.instances || [];
    this.instancesBackup = _.cloneDeep(this.instances);
    this.isAggregate = true;
    this.system_id = payload.actions[0].detail.system.id;
    this.system_name = payload.actions[0].detail.system.name;
    this.canPaste = false;
    this.aggregationId = payload.aggregationId || '';
    this.selectedIndex = payload.selectedIndex || 0;
    // 是否需要展示无限制
    this.isNeedNoLimited = payload.isNeedNoLimited;
    // 是否是无限制操作
    this.isNoLimited = payload.isNoLimited;
    this.tag = payload.tag || 'add';
    this.initDetailData(this.actions);
  }

  initDetailData (payload) {
    if (payload.length < 1) {
      this.detail = {};
      return;
    }
    this.detail = payload[0].detail;
  }

  get isTemplate () {
    if (this.actions.length > 0) {
      return this.actions[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID;
    }
    return false;
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
              str = language === 'zh-cn' ? `${str}，已选择${this.instancesDisplayData[item.id].length}个${item.name}` : `${str}, selected ${this.instancesDisplayData[item.id].length} ${item.name}(s)`;
              Vue.set(item, 'displayValue', str.substring(1, str.length));
              str = '';
            }
          }
        } else {
          // 这里防止切换tab下存在空数据，需要重新判断下
          if (this.instancesDisplayData[item.id] && this.instancesDisplayData[item.id].length === 1) {
            str = `${str}${il8n('common', '，')}${item.name}${il8n('common', '：')}${this.instancesDisplayData[item.id][0].name}`;
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
    const aggregateResourceType = _.cloneDeep(this.aggregateResourceType.map(item => item.displayValue));
    return aggregateResourceType.join();
  }

  get name () {
    if (this.actions.length < 1) {
      return '';
    }
    return this.actions.map(item => item.name).filter(name => name).join('，');
  }

  get key () {
    if (this.actions.length < 1) {
      return '';
    }
    return this.actions.map(item => item.id).join('');
  }

  // get resource_groups
}

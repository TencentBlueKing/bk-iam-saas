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

import { language, il8n } from '@/language';
import { xssFilter } from '@/common/util';
import Instance from './instance';
import Attribute from './attribute';

const isCn = language === 'zh-cn';
export default class Condition {
  // flag = '' 为默认拉取，flag = 'add' 为新添加的
  // type 为 init 时初始化
  // instanceCanDelete: 实例是否可删除
  // attributeCanDelete: 属性是否可删除
  // instanceNotDisabled: instance 不允许 disabled
  constructor (
    payload, type = '', flag = '', instanceCanDelete = true, attributeCanDelete = true, instanceNotDisabled = false
  ) {
    this.instanceExpanded = false;
    this.instanceLoading = false;
    this.attributeExpanded = false;
    this.attributeLoading = false;
    this.isHovering = false;
    this.isInstanceEmpty = false;
    this.isAttributeEmpty = false;
    this.id = payload.id || '';
    this.flag = flag;
    this.selectionMode = payload.selection_mode || 'all';
    if (this.selectionMode === 'all') {
      this.initIntance(payload, type, this.flag, instanceCanDelete, instanceNotDisabled);
      this.initAttribute(payload, type, this.flag, attributeCanDelete);
    } else if (['instance', 'instance:paste'].includes(this.selectionMode)) {
      this.initIntance(payload, type, this.flag, false, instanceNotDisabled);
      this.instanceCanDelete = flag !== '';
    } else {
      this.initAttribute(payload, type, this.flag);
      this.attributeCanDelete = flag !== '';
    }
  }
  initIntance (payload, type, flag, instanceCanDelete, instanceNotDisabled) {
    if (type === 'init') {
      this.instance = [];
      this.instanceCanDelete = instanceCanDelete;
      return;
    }
    if (payload.instances && payload.instances.length > 0) {
      this.instance = payload.instances.map(item => new Instance(item, flag, instanceNotDisabled));
      this.instanceCanDelete = flag !== '';
    }
  }
  initAttribute (payload, type, flag, attributeCanDelete) {
    if (type === 'init') {
      this.attribute = [];
      this.attributeCanDelete = attributeCanDelete;
      return;
    }
    if (payload.attributes && payload.attributes.length > 0) {
      this.attribute = payload.attributes.map(item => new Attribute(item, flag));
      this.attributeCanDelete = flag !== '';
    }
  }
  get instanceTitle () {
    if (this.isInstanceEmpty) {
      return xssFilter(`<span style="color: #ff4d4d;">${il8n('verify', '请选择拓扑实例')}</span>`);
    }
    if (this.instance && this.instance.length > 0) {
      const strList = [];
      this.instance.forEach(item => {
        if (item.displayPath.length > 0) {
          const str = xssFilter(isCn
            ? `<span style="color: #3A84FF; font-weight: 700;">${item.displayPath.length}</span> 个${item.name}`
            : ` <span style="color: #3A84FF; font-weight: 700;">${item.displayPath.length}</span> ${item.name}(s)`);
          strList.push(str);
        }
      });
      if (strList.length > 0) {
        return `${il8n('common', '已选择')} ${strList.join(', ')}`;
      }
      return il8n('resource', '未选择任何拓扑实例');
    }
    return il8n('resource', '未选择任何拓扑实例');
  }
  get attributeTitle () {
    if (this.isAttributeEmpty) {
      return xssFilter(`<span style="color: #ff4d4d; font-weight: 700;">${il8n('verify', '请设置属性条件')}</span>`);
    }
    if (this.attribute && this.attribute.length > 0) {
      let len = 0;
      this.attribute.forEach(item => {
        if (item.id && item.values.some(val => val.id)) {
          ++len;
        }
      });
      if (len > 0) {
        return xssFilter(`${il8n('resource', '已设置')} <span style="color: #ff4d4d;font-weight: 700;">${String(len)}</span> ${il8n('resource', '个属性条件')}`);
      }
      return il8n('verify', '未设置任何条件');
    }
    return il8n('verify', '未设置任何条件');
  }
}

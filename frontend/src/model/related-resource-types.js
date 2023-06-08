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
import Condition from './condition';

const isCn = language === 'zh-cn';
export default class RelateResourceTypes {
  // instanceNotDisabled: instance 不允许 disabled
  constructor (payload, action, flag = '', instanceNotDisabled = false, isNew = false) {
    this.type = ['', 'detail'].includes(flag) ? payload.type : payload.id;
    this.system_id = payload.system_id;
    this.name = payload.name || '';
    this.canPaste = false;
    this.action = action;
    this.isError = false;
    this.tag = payload.tag || '';
    this.flag = ['add', 'detail'].includes(flag) ? 'add' : '';
    this.isChange = false;
    this.isNew = isNew;
    this.selectionMode = payload.selection_mode || 'all';
    const curFlag = flag === 'detail' ? 'add' : '';
    this.initCondition(payload, curFlag, instanceNotDisabled, isNew);
  }

  initCondition (payload, flag, instanceNotDisabled, isNew) {
    // conditionBackup: 做还原操作时的数据备份
    if (payload.isTempora) { // 临时权限标识
      this.condition = payload.condition;
      this.conditionBackup = payload.condition;
    } else {
      const isEmpty = !payload.condition
                || (
                  payload.condition.length > 0
                        && payload.condition.every(item => item.attributes.length < 1 && item.instances.length < 1)
                );
      if (isEmpty) {
        this.condition = ['none'];
        this.conditionBackup = ['none'];
        return;
      }
      this.condition = payload.condition.map(
        item => new Condition(item, '', flag, true, true, instanceNotDisabled)
      ) || [];
    
      this.conditionBackup = payload.condition.map(
        item => new Condition(item, '', flag, true, true, instanceNotDisabled)
      ) || [];
    }
  }

  get isDefaultLimit () {
    return this.flag === '' && this.condition.length < 1 && !this.isChange && !this.isNew;
  }

  get empty () {
    if (this.condition.length === 1 && this.condition[0] === 'none') {
      return true;
    }
    return false;
  }

  get value () {
    if (this.empty) {
      const { type, name } = this.action;
      if (type === 'create') {
        return isCn
          ? `请选择在哪些【${this.name}】下【${name}】`
          : `Please select the 【${this.name}】under which【${name}】`;
      }
      return isCn ? `请选择${this.name}实例` : `Please select ${this.name} instances`;
    }
    if (this.condition.length === 0) {
      return il8n('common', '无限制');
    }
    const singleResourceFlag = this.condition.every(item => {
      return (!item.attribute || (item.attribute && item.attribute.length < 1))
                && item.instance.length === 1
                && item.instance[0].path.length === 1;
    });
    if (singleResourceFlag) {
      return this.condition.map(item => {
        return item.instance[0].path[0].map(subItem => subItem.name).join('/');
      }).join('；');
    }
    let attributeLen = 0;
    let attributeStr = '';
    const instanceStrs = [];
    let instanceStr = '';
    const instanceStrMap = {};
    this.condition.forEach(item => {
      if (item.attribute) {
        attributeLen = attributeLen + item.attribute.length;
      }
      if (item.instance) {
        item.instance.forEach(ins => {
          const pathLen = ins.path.length;
          if (pathLen > 0) {
            if (!instanceStrMap[ins.name]) {
              instanceStrMap[ins.name] = pathLen;
            } else {
              instanceStrMap[ins.name] = instanceStrMap[ins.name] + pathLen;
            }
          }
        });
      }
    });

    for (const key in instanceStrMap) {
      const str = isCn ? `${instanceStrMap[key]} 个${key}` : `${instanceStrMap[key]} ${key}(s)`;
      instanceStrs.push(str);
    }

    if (attributeLen > 0) {
      attributeStr = `${il8n('resource', '已设置')} ${attributeLen} ${il8n('resource', '个属性条件')}`;
    }
    if (instanceStrs.length > 0) {
      instanceStr = `${il8n('common', '已选择')} ${instanceStrs.join('，')}`;
    }
    return [attributeStr, instanceStr].filter(item => item !== '').join('；');
  }
}

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

/* eslint-disable max-len */

import { language, il8n } from '@/language';
import { xssFilter } from '@/common/util';

const isCn = language === 'zh-cn';
class Instance {
  constructor (payload) {
    this.name = payload.name || '';
    this.type = payload.type || '';
    this.status = payload.tag;
    this.initPath(payload);
  }

  initPath (payload) {
    if (!payload.path) {
      this.path = [];
    }
    this.path = payload.path;
  }

  get displayPath () {
    // debugger
    if (!this.path || this.path.length < 1) {
      return [];
    }
    const tempList = [];
    this.path.forEach(item => {
      if (item.chain) {
        const len = item.chain.length;
        const displayName = item.chain.map(sub => sub.name).join('/');
        tempList.push({
          name: displayName,
          id: item.chain[len - 1].id,
          level: len - 1,
          status: item.tag
        });
      } else {
        const len = item.length;
        const displayName = item.map(sub => sub.name).join('/');
        tempList.push({
          name: displayName,
          id: item[len - 1].id,
          level: len - 1,
          status: item[len - 1].tag
        });
      }
    });
    return tempList;
  }

  get title () {
    if (this.status === 'delete') {
      return xssFilter(`<s style="color: #c4c6cc;">${this.name}：</s>`);
    }
    return `${this.name}：`;
  }
}

class Attribute {
  constructor (payload) {
    this.id = payload.id || '';
    this.name = payload.name || '';
    this.status = payload.tag;
    this.initValues(payload);
  }

  initValues (payload) {
    if (!payload.values) {
      this.values = [];
    }
    this.values = payload.values.map(item => {
      const { id, name, tag } = item;
      return {
        id,
        name,
        status: tag
      };
    });
  }

  get title () {
    if (this.status === 'delete') {
      return xssFilter(`<s style="color: #c4c6cc;">${this.name}：</s>`);
    }
    return `${this.name}：`;
  }
}

export default class CompareCondition {
  constructor (payload) {
    this.instanceExpanded = false;
    this.attributeExpanded = false;
    this.isHovering = false;
    this.id = payload.id || '';
    this.status = payload.tag;
    this.initIntance(payload);
    this.initAttribute(payload);
  }

  initIntance (payload) {
    if (payload.instances && payload.instances.length > 0) {
      this.instance = payload.instances.map(item => new Instance(item));
    }
  }

  initAttribute (payload) {
    if (payload.attributes && payload.attributes.length > 0) {
      this.attribute = payload.attributes.map(item => new Attribute(item));
    }
  }

  get instanceTitle () {
    if (this.instance && this.instance.length > 0) {
      if (this.instance.every(item => item.status === 'delete')) {
        return xssFilter(`<s style="color: #c4c6cc;">${il8n('resource', '拓扑实例')}：</s>`);
      }
      return `${il8n('resource', '拓扑实例')}：`;
    }
    return '';
  }

  get isInstanceNew () {
    return this.instance.every(item => item.status === 'add');
  }

  get instanceSubTitle () {
    if (this.instance && this.instance.length > 0) {
      const strList = [];
      // debugger
      this.instance.forEach(item => {
        if (item.displayPath.length > 0) {
          const strList = [];
          let str = '';
          const addLen = item.displayPath.filter(item => item.status === 'add').length;
          const deleteLen = item.displayPath.filter(item => item.status === 'delete').length;
          if (addLen > 0) {
            strList.push(`${il8n('common', '增')} ${addLen}`);
          }
          if (deleteLen > 0) {
            strList.push(`${il8n('common', '删')} ${deleteLen}`);
          }
          if (strList.length > 0) {
            if (item.displayPath.every(item => item.status === 'delete')) {
              str = `<s style="color: #c4c6cc;">0<span style="font-weight: 600;">(${strList.join('，')})</span>${isCn ? '个' : ''} ${item.name}${isCn ? '' : '(s))'}</s>`;
            } else {
              str = `<span>${item.displayPath.length - deleteLen}<span style="font-weight: 600;">(${strList.join('，')})</span>${isCn ? '个' : ''} ${item.name}${isCn ? '' : '(s))'}</span>`;
            }
          } else {
            str = ` ${item.displayPath.length} ${isCn ? '个' : ''} ${item.name}${isCn ? '' : '(s)'}`;
          }
          strList.push(xssFilter(str));
        }
      });
      if (this.instance.every(item => {
        return item.displayPath.every(item => item.status === 'delete');
      })) {
        return xssFilter(`<s style="color: #c4c6cc;">${il8n('common', '已选择')} ${strList.join('、')}</s>`);
      }
      return `${il8n('common', '已选择')} ${strList.join('、')}`;
    }
    return il8n('resource', '未选择任何拓扑实例');
  }

  get attributeTitle () {
    if (this.attribute && this.attribute.length > 0) {
      if (this.attribute.every(item => item.status === 'delete')) {
        return xssFilter(`<s style="color: #c4c6cc;">${il8n('resource', '属性条件')}：</s>`);
      }
      return `${il8n('resource', '属性条件')}：`;
    }
    return '';
  }

  get isAttributeNew () {
    return this.attribute.every(item => item.status === 'add');
  }

  get attributeSubTitle () {
    if (this.attribute && this.attribute.length > 0) {
      let len = 0;
      this.attribute.forEach(item => {
        if (item.id && item.values.some(val => val.id)) {
          ++len;
        }
      });
      if (len > 0) {
        const strList = [];
        const addLen = this.attribute.filter(item => item.status === 'add').length;
        const deleteLen = this.attribute.filter(item => item.status === 'delete').length;
        const editLen = this.attribute.filter(item => item.status === 'unchanged' && item.values.some(val => ['delete', 'add'].includes(val.status))).length;
        if (addLen > 0) {
          strList.push(`${il8n('common', '增')} ${addLen}`);
        }
        if (deleteLen > 0) {
          strList.push(`${il8n('common', '删')} ${deleteLen}`);
        }
        if (editLen > 0) {
          strList.push(`${il8n('common', '改')} ${editLen}`);
        }
        if (strList.length > 0) {
          if (this.attribute.length === deleteLen) {
            return xssFilter(`<s style="color: #c4c6cc;">${isCn ? '已设置0' : '0 has been set'} <span style="font-weight: 600;">(${isCn ? '删' : 'delete'} ${String(deleteLen)})</span>${isCn ? '个属性条件' : 'condition(s)'}</s>`);
          }
          return xssFilter(isCn
            ? `已设置<span>${this.attribute.length - deleteLen}<span style="font-weight: 600;">(${strList.join('，')})</span>个属性条件</span>`
            : `<span>${this.attribute.length - deleteLen}<span style="font-weight: 600;">(${strList.join('，')})</span>condition(s) has been set</span>`);
        }
        return xssFilter(`${il8n('resource', '已设置')} ${String(len)} ${il8n('resource', '个属性条件')}`);
      }
      return il8n('verify', '未设置任何条件');
    }
    return il8n('verify', '未设置任何条件');
  }
}

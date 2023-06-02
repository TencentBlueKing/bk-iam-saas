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

import Policy from './policy';
import { il8n } from '@/language';

export default class GroupPolicy extends Policy {
  // mode: template(模板)， custom(自定义)
  // instanceNotDisabled: instance 不允许 disabled
  constructor (payload, flag = 'detail', mode = 'template', data = {}, instanceNotDisabled = false) {
    super(payload, flag, instanceNotDisabled);
    this.detail = data;
    this.mode = mode;
    this.system_name = payload.system_name;
    this.system_id = payload.system_id;
    this.conditionIds = payload.conditionIds;
    // 聚合id，相同aggregationId的数据聚合时会被聚合在一起
    this.aggregationId = '';
    this.aggregateResourceType = {};
  }

  get isTemplate () {
    return this.mode === 'template';
  }

  get displayName () {
    if (this.isTemplate) {
      return this.detail.name || '';
    }
    return il8n('perm', '自定义权限');
  }

  get judgeId () {
    return `${this.detail.id}&${this.detail.system.id}`;
  }
}

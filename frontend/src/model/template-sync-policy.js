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

import il8n from '@/language';
import { DURATION_LIST } from '@/common/constants';
import RelateResourceTypes from './related-resource-types';

export default class SyncPolicy {
  // flag = '' 为默认拉取，flag = 'add' 为新添加的，flag = 'detail' 为权限模板详情
  // tag: add updata unchanged create
  constructor (payload, flag = '') {
    this.type = payload.type;
    this.id = payload.id;
    this.policy_id = payload.policy_id || '';
    this.name = payload.name;
    this.description = payload.description;
    this.count = payload.count || 0;
    this.tag = payload.tag || '';
    this.isShowCustom = false;
    this.customValue = '';
    this.environment = payload.environment || {};
    this.isNeedAttachAction = false;
    this.isError = false;
    // 实例是否超出限制
    this.isLimitExceeded = false;
    // 已有权限是否需要动画提示
    this.isExistPermAnimation = false;
    this.tid = payload.tid || '';
    this.initExpired(payload);
    this.initRelatedResourceTypes(payload, { name: this.name, type: this.type }, flag);
    this.initRelatedRroupsTypes(payload, { name: this.name, type: this.type }, flag);
    this.initAttachActions(payload);
    this.showAction = false;
    this.showPopover = false;
    this.loading = false;
  }

  initExpired (payload) {
    this.expired_display = payload.expired_display;
    // 默认显示永久
    if (payload.expired_at === null) {
      this.expired_at = 15552000;
      return;
    }
    if (DURATION_LIST.includes(payload.expired_at) && this.policy_id !== '') {
      this.expired_at = payload.expired_at;
      return;
    }
    this.expired_at = payload.expired_at;
  }

  initRelatedResourceTypes (payload, action, flag) {
    if (!payload.related_resource_types) {
      this.related_resource_types = [];
      return;
    }
    this.related_resource_types = payload.related_resource_types.map(
      item => new RelateResourceTypes(item, action, flag)
    );
  }

  initRelatedRroupsTypes (payload, action, flag) {
    if (!payload.resource_groups) {
      this.resource_groups = [];
      return;
    }

    this.resource_groups = payload.resource_groups.reduce((prev, item) => {
      const relatedRsourceTypes = item.related_resource_types.map(
        item => new RelateResourceTypes(item, action, flag)
      );

      prev.push({ id: item.id, related_resource_types: relatedRsourceTypes });
      return prev;
    }, []);
  }

  initAttachActions (payload) {
    if (!payload.attach_actions) {
      this.attach_actions = [];
      return;
    }
    this.attach_actions = payload.attach_actions || [];
  }

  get isCustomExpiredAt () {
    if (DURATION_LIST.includes(this.expired_at)) {
      return false;
    }
    return true;
  }

  get expiredAtPlaceholder () {
    if (DURATION_LIST.includes(this.expired_at)) {
      return il8n('verify', '请选择');
    }
    return this.expired_display;
  }

  get isExpiredAtDisabled () {
    return this.tag === 'unchanged';
  }

  get isNew () {
    return this.tag === 'add';
  }

  get isChanged () {
    return this.tag === 'update';
  }

  get isEmpty () {
    return this.resource_groups.length < 1;
  }

  get isCreate () {
    return this.type === 'create';
  }

  get canView () {
    return this.policy_id !== '';
  }
}

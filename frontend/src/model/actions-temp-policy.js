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
export default class Policy {
  // flag = '' 为默认拉取，flag = 'add' 为新添加的，flag = 'detail' 为权限模板详情, flag = 'custom' 为自定义申请权限
  // tag: add updata unchanged create
  // instanceNotDisabled: instance 不允许 disabled
  // mode判断当前类型是自定义权限还是权限模板
  constructor (payload, flag = '', instanceNotDisabled = false, isProv = false) {
    this.mode = payload.mode || '';
    this.isAggregate = false;
    this.type = payload.type;
    this.id = payload.id;
    this.policy_id = payload.policy_id || '';
    this.name = payload.name;
    this.description = payload.description;
    this.count = payload.count || 0;
    this.tag = payload.tag || '';
    this.isTempora = payload.isTempora || false;
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
    // 依赖操作
    this.related_actions = payload.related_actions || [];
    this.isShowRelatedText = payload.isShowRelatedText || false;
    this.inOriginalList = payload.inOriginalList || false;
    this.related_environments = payload.related_environments || [];
    this.initExpired(payload, isProv);
    this.initRelatedResourceTypes(payload, { name: this.name, type: this.type }, flag, instanceNotDisabled);
    this.initAttachActions(payload);
  }

  initExpired (payload, isProv) {
    this.expired_display = payload.expired_display;
    // 默认显示永久
    if (payload.expired_at === null) {
      this.expired_at = 15552000;
      if (isProv) {
        this.expired_at = 3600;
      }
      return;
    }
    if (DURATION_LIST.includes(payload.expired_at) && this.policy_id !== '') {
      this.expired_at = payload.expired_at;
      return;
    }
    this.expired_at = payload.expired_at;
  }

  initRelatedResourceTypes (payload, action, flag, instanceNotDisabled) {
    // console.log('payload', payload)
    // if (!payload.related_resource_types) {
    //     this.related_resource_types = []
    //     return
    // }
    // this.related_resource_types = payload.related_resource_types.map(
    //     item => new RelateResourceTypes(item, action, flag, instanceNotDisabled, this.isNew)
    // )

    if (!payload.resource_groups) {
      this.resource_groups = [];
      return;
    }

    this.resource_groups = payload.resource_groups.reduce((prev, item) => {
      const relatedRsourceTypes = item.related_resource_types.map(
        item => new RelateResourceTypes({ ...item, isTempora: payload.isTempora },
          action, flag, instanceNotDisabled, this.isNew)
      );
            
      if ((this.related_environments && !!this.related_environments.length)) {
        const environments = item.environments && !!item.environments.length ? item.environments : [];
        prev.push({ id: item.id, related_resource_types: relatedRsourceTypes, environments: environments });
      } else {
        if (item.environments && !!item.environments.length) {
          // eslint-disable-next-line max-len
          prev.push({ id: item.id, related_resource_types: relatedRsourceTypes, environments: item.environments });
        } else {
          prev.push({ id: item.id, related_resource_types: relatedRsourceTypes });
        }
      }
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
    return this.tag === 'update' || (this.tag !== 'add' && this.expired_display && !this.policy_id);
  }

  get isEmpty () {
    return this.resource_groups.length < 1;
    // return this.related_resource_types.length < 1 // || this.resource_groups.length < 1
  }

  get isEffectEmpty () {
    return this.resource_groups.length < 1;
    // return this.related_resource_types.length < 1 // || this.resource_groups.length < 1
  }

  get isCreate () {
    return this.type === 'create';
  }

  get canView () {
    return false;
    // return this.policy_id !== '';
  }

  // 是否主操作
  get isMainAction () {
    return this.related_actions.length > 0;
  }
}

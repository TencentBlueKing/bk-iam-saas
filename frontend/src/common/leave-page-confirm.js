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
import { il8n, language } from '@/language';

export const leavePageConfirm = () => {
  if (!window.changeDialog) {
    return Promise.resolve();
  }
  const vm = new Vue();
  const h = vm.$createElement;
  return new Promise((resolve, reject) => {
    vm.$bkInfo({
      title: il8n('info', '离开将会导致未保存信息丢失'),
      width: language === 'zh-cn' ? 400 : 600,
      subHeader: h('p', {
        style: {
          color: '#63656e',
          fontSize: '14px',
          textAlign: 'center'
        }
      }, il8n('info', '确认离开当前页')),
      okText: il8n('common', '离开'),
      cancelText: il8n('common', '取消-dialog'),
      confirmFn: () => {
        window.changeDialog = false;
        resolve();
      },
      cancelFn: () => {
        reject(Error('cancel'));
      }
    });
  });
};

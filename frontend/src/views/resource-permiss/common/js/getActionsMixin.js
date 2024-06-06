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
import { cloneDeep } from 'lodash';
import { mapGetters } from 'vuex';
export default {
  computed: {
    ...mapGetters(['user', 'externalSystemId'])
  },
  data () {
    return {
      linearActionList: []
    };
  },
  methods: {
    // 获取系统对应的自定义操作
    async fetchActions (item) {
      const params = {
        system_id: item.system.id,
        user_id: this.user.username
      };
      if (this.externalSystemId) {
        params.hidden = false;
      }
      try {
        const { data } = await this.$store.dispatch('permApply/getActions', params);
        this.handleActionLinearData(data || []);
      } catch (e) {
        this.messageAdvancedError(e);
      }
    },

    handleActionLinearData (payload) {
      const linearActions = [];
      payload.forEach((item) => {
        item.actions = item.actions.filter(v => !v.hidden);
        item.actions.forEach(act => {
          linearActions.push(act);
        });
        (item.sub_groups || []).forEach(sub => {
          sub.actions = sub.actions.filter(v => !v.hidden);
          sub.actions.forEach(act => {
            linearActions.push(act);
          });
        });
      });
      this.linearActionList = cloneDeep(linearActions);
      // console.log('this.linearActionList', this.linearActionList);
      return payload;
    }
  }
};

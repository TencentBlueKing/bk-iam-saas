<template>
  <div class="iam-set-super-manager-wrapper">
    <render-item
      :sub-title="subTitle"
      expanded>
      <bk-table
        size="small"
        ext-cls="super-user-table-cls"
        :max-height="tableHeight"
        :data="superUserList"
        :outer-border="false"
        :header-border="false"
        @row-mouse-enter="handleSuperRowMouseEnter"
        @row-mouse-leave="handleSuperRowMouseLeave">
        <bk-table-column :label="$t(`m.set['名称']`)">
          <template slot-scope="{ row, $index }">
            <template v-if="row.isEdit">
              <bk-user-selector
                :value="row.user"
                :ref="`superRef${$index}`"
                :api="userApi"
                style="width: 100%;"
                :placeholder="$t(`m.verify['请输入']`)"
                :empty-text="$t(`m.common['无匹配人员']`)"
                @change="handleSuperRtxChange(...arguments, row)"
                @keydown="handleSuperRtxEnter(...arguments, row)">
              </bk-user-selector>
            </template>
            <template v-else>
              <div
                :class="['user-wrapper', { 'is-hover': row.canEdit && row.user[0] !== 'admin' }]"
                :title="row.user.join('；')"
              >
                {{ row.user.join('；') }}
              </div>
            </template>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.set['更多权限设置']`)">
          <template slot-scope="{ row }">
            <bk-checkbox
              :true-value="true"
              :false-value="false"
              :disabled="row.username === 'admin'"
              :value="row.system_permission_enabled"
              @change="handleEnabledChange(...arguments, row)">
              {{ $t(`m.set['拥有蓝鲸平台所有操作权限']`) }}
            </bk-checkbox>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['操作']`)" width="120">
          <template slot-scope="{ row, $index }">
            <template v-if="row.isEdit">
              <bk-button theme="primary" text :disabled="isDisabled(row)" @click="handleSave(row)">
                {{ $t(`m.common['保存']`) }}
              </bk-button>
              <bk-button theme="primary" text style="margin-left: 10px;"
                @click="handleCancel(row, $index)">
                {{ $t(`m.common['取消']`) }}
              </bk-button>
            </template>
            <template v-else-if="row.user[0] === 'admin'">
              <bk-button
                theme="primary"
                text
                :disabled="row.user[0] === 'admin'">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </template>
            <template v-else>
              <iam-popover-confirm
                :title="$t(`m.set['确定删除该超级管理员']`)"
                :confirm-handler="() => handleDelete(row, $index)">
                <bk-button
                  theme="primary"
                  text>
                  {{ $t(`m.common['删除']`) }}
                </bk-button>
              </iam-popover-confirm>
            </template>
          </template>
        </bk-table-column>
        <template slot="empty">
          <ExceptionEmpty
            :type="emptyData.type"
            :empty-text="emptyData.text"
            :tip-text="emptyData.tip"
            :tip-type="emptyData.tipType"
            @on-clear="handleEmptyClear"
            @on-refresh="handleEmptyRefresh"
          />
        </template>
      </bk-table>
      <render-action
        :title="$t(`m.set['添加超级管理员']`)"
        :handle-click="handleAddSuperUser" />
    </render-item>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import IamPopoverConfirm from '@/components/iam-popover-confirm';
  import BkUserSelector from '@blueking/user-selector';
  import RenderItem from '../common/render-item';
  import RenderAction from '../common/render-action';
    
  export default {
    name: '',
    components: {
      BkUserSelector,
      RenderItem,
      RenderAction,
      IamPopoverConfirm
    },
    filters: {
      memberFilter (value) {
        if (value.length > 0) {
          return value.join('；');
        }
        return '--';
      }
    },
    data () {
      return {
        subTitle: this.$t(`m.set['超级管理员提示']`),
        superUserList: [],
        userApi: window.BK_USER_API,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['user']),
            isDisabled () {
                return payload => {
                    if (payload.user.length !== 1) {
                        return true;
                    }
                    if (this.superUserList.filter(item => item.user[0] === payload.user[0]).length > 1) {
                        return true;
                    }
                    return false;
                };
            },
            tableHeight () {
                return getWindowHeight() - 297;
            }
    },
    created () {
      this.fetchSuperManager();
    },
    methods: {
      handleAddSuperUser () {
        this.superUserList.push({
          user: [],
          userBackup: [],
          system_permission_enabled: false,
          isEdit: true
        });
        const index = this.superUserList.length - 1;
        this.$nextTick(() => {
          this.$refs[`superRef${index}`].focus();
        });
      },

      async fetchSuperManager () {
        this.$emit('data-ready', false);
        try {
          const { code, data } = await this.$store.dispatch('role/getSuperManager');
          const tempArr = [];
          data.forEach(item => {
            const { username, system_permission_enabled } = item;
            tempArr.push({
              user: [username],
              userBackup: [username],
              system_permission_enabled,
              isEdit: false,
              username
            });
          });
          this.superUserList.splice(0, this.superUserList.length, ...tempArr);
          this.emptyData = formatCodeData(code, this.emptyData, this.superUserList.length === 0);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.$emit('data-ready', true);
        }
      },

      handleSuperRtxChange (payload, row) {
        row.user = [...payload];
      },

      handleSuperRtxEnter (event, payload) {
        if (!payload.userBackup || payload.userBackup.length < 1) {
          return;
        }
        if (event.keyCode === 13) {
          event.stopPropagation();
          const flag = _.isEqual(payload.user.sort(), payload.userBackup.sort());
          if (flag) {
            payload.isEdit = false;
            return;
          }
          if (payload.user.length < 2) {
            this.handleSave(payload);
          }
        }
      },

      handleSuperRowMouseEnter (index) {
        this.$set(this.superUserList[index], 'canEdit', true);
      },

      handleSuperRowMouseLeave (index) {
        this.$delete(this.superUserList[index], 'canEdit');
      },

      handleOpenSuperEdit (payload, index) {
        if (!payload.canEdit || payload.username === 'admin') {
          return;
        }
        payload.isEdit = true;
        this.$nextTick(() => {
          this.$refs[`superRef${index}`].focus();
        });
      },

      async handleDelete (payload, index) {
        const username = payload.user[0];
        try {
          this.$store.dispatch('role/deleteSuperManager', { username });
          this.superUserList.splice(index, 1);
          this.messageSuccess(this.$t(`m.common['操作成功']`));
          if (username === this.user.username) {
            bus.$emit('refresh-role', {
              id: 0,
              type: 'staff',
              name: this.user.role.name
            });
          }
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      handleCancel (payload, index) {
        if (payload.userBackup.length < 1) {
          this.superUserList.splice(index, 1);
          return;
        }
        payload.user = [...payload.userBackup];
        payload.isEdit = false;
      },

      async addSuperManager (payload) {
        const { user, system_permission_enabled } = payload;
        try {
          await this.$store.dispatch('role/addSuperManager', {
            username: user[0],
            system_permission_enabled
          });
          payload.userBackup = [...payload.user];
          payload.isEdit = false;
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      async editSuperManager (payload) {
        const { user, system_permission_enabled } = payload;
        try {
          await this.$store.dispatch('role/editSuperManager', {
            username: user[0],
            system_permission_enabled
          });
          payload.userBackup = [...payload.user];
          payload.username = payload.user[0];
          payload.isEdit = false;
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      async handleEnabledChange (newVal, oldVal, val, payload) {
        if (!payload.userBackup || payload.userBackup.length < 1) {
          payload.system_permission_enabled = newVal;
          return;
        }
        try {
          await this.$store.dispatch('role/editSuperManager', {
            username: payload.user[0],
            system_permission_enabled: newVal
          });
          payload.system_permission_enabled = newVal;
          payload.isEdit = false;
          const message = newVal ? this.$t(`m.set['设置成功']`) : this.$t(`m.set['取消设置成功']`);
          this.messageSuccess(message);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      handleSave (payload) {
        const flag = _.isEqual(payload.user.sort(), payload.userBackup.sort());
        if (flag) {
          payload.isEdit = false;
          return;
        }
        if (payload.userBackup.length < 1) {
          this.addSuperManager(payload);
          return;
        }
        this.editSuperManager(payload);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-set-super-manager-wrapper {
        .super-user-table-cls {
            border: none;
            tr {
                &:hover {
                    background-color: transparent;
                    & > td {
                        background-color: transparent;
                    }
                }
            }
            .user-wrapper {
                padding: 0 8px;
                width: 100%;
                height: 32px;
                line-height: 32px;
                border-radius: 2px;
                &.is-hover {
                    background: #f0f1f5;
                    cursor: pointer;
                }
            }
            .is-member-empty-cls {
                .user-selector-container {
                    border-color: #ff4d4d;
                }
            }
        }
    }
</style>

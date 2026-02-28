<template>
  <div class="iam-set-audit-manager-wrapper">
    <render-item
      :sub-title="subTitle"
      expanded>
      <bk-table
        size="small"
        ext-cls="audit-user-table-cls"
        :max-height="tableHeight"
        :data="auditUserList"
        :outer-border="false"
        :header-border="false"
        @row-mouse-enter="handleAuditRowMouseEnter"
        @row-mouse-leave="handleAuditRowMouseLeave">
        <bk-table-column :label="$t(`m.set['名称']`)">
          <template slot-scope="{ row, $index }">
            <template v-if="row.isEdit">
              <bk-user-selector
                :value="row.user"
                :ref="`auditRef${$index}`"
                :api="userApi"
                style="width: 100%;"
                :placeholder="$t(`m.verify['请输入']`)"
                :empty-text="$t(`m.common['无匹配人员']`)"
                @change="handleAuditRtxChange(...arguments, row)"
                @keydown="handleAuditRtxEnter(...arguments, row)">
              </bk-user-selector>
            </template>
            <template v-else>
              <div
                :class="['user-wrapper', { 'is-hover': row.canEdit }]"
                :title="row.user.join('；')"
                @click="handleOpenAuditEdit(row, $index)"
              >
                {{ row.user.join('；') }}
              </div>
            </template>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['操作-table']`)" width="120">
          <template slot-scope="{ row, $index }">
            <template v-if="row.isEdit">
              <bk-button
                theme="primary"
                text
                :title="saveDisableTip"
                :disabled="isDisabled(row)"
                @click="handleSave(row)">
                {{ $t(`m.common['保存']`) }}
              </bk-button>
              <bk-button theme="primary" text style="margin-left: 10px;"
                @click="handleCancel(row, $index)">
                {{ $t(`m.common['取消']`) }}
              </bk-button>
            </template>
            <template v-else>
              <iam-popover-confirm
                :title="$t(`m.set['确定删除该审计管理员']`)"
                :confirm-handler="(e) => handleDelete(e, row, $index)">
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
            @on-refresh="handleEmptyRefresh"
          />
        </template>
      </bk-table>
      <render-action
        :title="$t(`m.set['添加审计管理员']`)"
        :handle-click="handleAddAuditUser" />
    </render-item>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import IamPopoverConfirm from '@/components/iam-popover-confirm';
  import BkUserSelector from '@blueking/user-selector';
  import RenderItem from '../common/render-item';
  import RenderAction from '../common/render-action';
    
  export default {
    name: 'AuditManager',
    components: {
      BkUserSelector,
      RenderItem,
      RenderAction,
      IamPopoverConfirm
    },
    data () {
      return {
        saveDisableTip: '',
        auditUserList: [],
        userApi: window.BK_USER_API,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        tableHeight: getWindowHeight() - 297
      };
    },
    computed: {
      ...mapGetters(['user']),
      subTitle () {
        return this.$t(`m.set['审计管理员提示']`);
      },
      isDisabled () {
        return (payload) => {
          if (!payload.user.length) {
            this.saveDisableTip = this.$t(`m.verify['管理员不能为空']`);
            return true;
          }
          if (payload.user.length > 1) {
            this.saveDisableTip = this.$t(`m.info['最多添加一个管理员']`);
            return true;
          }
          if (this.auditUserList.filter(item => item.user[0] === payload.user[0]).length > 1) {
            this.saveDisableTip = this.$t(`m.info['管理员不可重复添加']`);
            return true;
          }
          this.saveDisableTip = '';
          return false;
        };
      }
    },
    created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 297;
      });
      this.fetchAuditManager();
    },
    methods: {
      handleAddAuditUser () {
        this.auditUserList.push({
          user: [],
          userBackup: [],
          isEdit: true
        });
        const index = this.auditUserList.length - 1;
        this.$nextTick(() => {
          this.$refs[`auditRef${index}`][0].focus();
        });
      },

      async fetchAuditManager () {
        this.$emit('data-ready', false);
        if (!['super_manager'].includes(this.user.role.type)) {
          this.$emit('data-ready', true);
          return;
        }
        try {
          const { code, data } = await this.$store.dispatch('role/getAuditManager');
          const tempArr = [];
          data.forEach(item => {
            const { username } = item;
            tempArr.push({
              user: [username],
              userBackup: [username],
              isEdit: false,
              username
            });
          });
          this.auditUserList.splice(0, this.auditUserList.length, ...tempArr);
          this.emptyData = formatCodeData(code, this.emptyData, this.auditUserList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.$emit('data-ready', true);
        }
      },

      handleAuditRtxChange (payload, row) {
        row.user = [...payload];
        if (this.auditUserList.length) {
          const hasManager = this.auditUserList.filter(item => item.user[0] === row.user[0]).length > 1;
          if (hasManager) {
            if (row.user.length < 2) {
              return this.messageWarn(this.$t(`m.info['管理员不可重复添加']`), 3000);
            } else {
              return this.messageWarn(this.$t(`m.info['最多添加一个管理员']`), 3000);
            }
          }
        }
      },

      handleAuditRtxEnter (event, payload) {
        if (!payload.userBackup || payload.userBackup.length < 1) {
          return;
        }
        if (event.keyCode === 13) {
          event.stopPropagation();
          if (this.auditUserList.length) {
            const hasManager = this.auditUserList.filter(item => item.user[0] === payload.user[0]).length > 1;
            if (hasManager) {
              if (payload.user.length < 2) {
                return this.messageWarn(this.$t(`m.info['管理员不可重复添加']`), 3000);
              } else {
                return this.messageWarn(this.$t(`m.info['最多添加一个管理员']`), 3000);
              }
            }
          }
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

      handleAuditRowMouseEnter (index) {
        this.$set(this.auditUserList[index], 'canEdit', true);
      },

      handleAuditRowMouseLeave (index) {
        this.$delete(this.auditUserList[index], 'canEdit');
      },

      handleOpenAuditEdit (payload, index) {
        if (!payload.canEdit) {
          return;
        }
        payload.isEdit = true;
        this.$nextTick(() => {
          this.$refs[`auditRef${index}`][0].focus();
        });
      },

      async handleDelete (e, payload, index) {
        const username = payload.user[0];
        try {
          await this.$store.dispatch('role/deleteAuditManager', { username });
          this.auditUserList.splice(index, 1);
          e && e.hide();
          this.messageSuccess(this.$t(`m.common['操作成功']`));
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      handleCancel (payload, index) {
        if (payload.userBackup.length < 1) {
          this.auditUserList.splice(index, 1);
          return;
        }
        payload.user = [...payload.userBackup];
        payload.isEdit = false;
      },

      async addAuditManager (payload) {
        const { user } = payload;
        try {
          await this.$store.dispatch('role/addAuditManager', {
            username: user[0]
          });
          payload.userBackup = [...payload.user];
          payload.username = payload.user[0];
          payload.isEdit = false;
          this.messageSuccess(this.$t(`m.common['操作成功']`));
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      handleSave (payload) {
        const flag = _.isEqual(payload.user.sort(), payload.userBackup.sort());
        if (flag) {
          payload.isEdit = false;
          return;
        }
        if (payload.userBackup.length < 1) {
          this.addAuditManager(payload);
          return;
        }
        // 审计管理员不支持编辑，只支持新增和删除
        payload.isEdit = false;
      },

      handleEmptyRefresh () {
        this.fetchAuditManager();
      }
    }
  };
</script>
<style lang="postcss">
    .iam-set-audit-manager-wrapper {
        .audit-user-table-cls {
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
        }
    }
</style>

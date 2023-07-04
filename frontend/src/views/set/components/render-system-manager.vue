<template>
  <div class="iam-set-system-manager-wrapper">
    <render-item
      :sub-title="subTitle"
      expanded>
      <bk-table
        size="small"
        ext-cls="system-user-table-cls"
        :max-height="tableHeight"
        :data="systemUserList"
        :outer-border="false"
        :header-border="false"
        @row-mouse-enter="handleSysRowMouseEnter"
        @row-mouse-leave="handleSysRowMouseLeave">
        <bk-table-column :label="$t(`m.set['系统名称']`)" prop="name">
          <template slot-scope="{ row }">
            <span :title="row.name">{{ row.name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.set['成员列表']`)" width="600">
          <template slot-scope="{ row, $index }">
            <template v-if="row.isEdit || row.members.length">
              <!-- <bk-user-selector
                                :value="formatMemberName(row.members)"
                                :ref="`sysRef${$index}`"
                                :api="userApi"
                                :class="row.isError ? 'is-member-empty-cls' : ''"
                                :placeholder="$t(`m.verify['请输入']`)"
                                style="width: 100%;"
                                data-test-id="set_userSelector_editSystemManager"
                                @blur="handleSystemRtxBlur(row)"
                                @change="handleSystemRtxChange(...arguments, row)"
                                @keydown="handleSystemRtxEnter(...arguments, row)" /> -->
              <iam-edit-member-selector
                :ref="`sysRef${$index}`"
                field="members"
                style="width: 100%;"
                :placeholder="$t(`m.verify['请输入']`)"
                :value="row.members"
                :index="$index"
                :allow-empty="true"
                @on-change="handleUpdateMembers"
                @on-empty-change="handleEmptyChange" />
            </template>
            <template v-else>
              <!-- <div
                                :class="['user-wrapper', { 'is-hover': row.canEdit }]"
                                @click.stop="handleOpenSysEdit(row, $index)">
                                {{ formatMemberFilter(row.members) }}
                            </div> -->
              <iam-edit-input
                field="members"
                style="width: 100%;"
                :is-show-other="true"
                :placeholder="$t(`m.verify['请输入']`)"
                :value="formatMemberFilter(row.members)"
                @handleShow="handleOpenSysEdit(row, $index)" />
            </template>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.set['更多权限设置']`)">
          <template slot-scope="{ row }">
            <bk-checkbox
              :true-value="true"
              :false-value="false"
              :value="row.system_permission_global_enabled"
              @change="handleSystemEnabledChange(...arguments, row)">
              {{ $t(`m.set['拥有该系统的所有操作权限']`) }}
            </bk-checkbox>
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
    </render-item>
  </div>
</template>
<script>
  import _ from 'lodash';
  // import BkUserSelector from '@blueking/user-selector';
  import IamEditInput from '@/components/iam-edit/input';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import RenderItem from '../common/render-item';
  import { getWindowHeight, formatCodeData } from '@/common/util';
    
  export default {
    name: '',
    components: {
      // BkUserSelector,
      IamEditInput,
      IamEditMemberSelector,
      RenderItem
    },
    data () {
      return {
        subTitle: this.$t(`m.set['系统管理员提示']`),
        systemUserList: [],
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
      tableHeight () {
        return getWindowHeight() - 297;
      }
    },
    async created () {
      await this.fetchSystemManager();
    },
    methods: {
      formatMemberFilter (value) {
        if (value.length) {
          return _.isArray(value) ? value.map(item => item.username).join(';') : value;
        }
        return '--';
      },

      async fetchSystemManager () {
        this.$emit('data-ready', false);
        try {
          const { code, data } = await this.$store.dispatch('role/getSystemManager');
          const tempArr = [];
          data.forEach(item => {
            tempArr.push({
                            ...item,
                            memberBackup: _.cloneDeep(item.members),
                            isEdit: false,
                            isError: false
            });
          });
          this.systemUserList.splice(0, this.systemUserList.length, ...tempArr);
          this.emptyData = formatCodeData(code, this.emptyData, this.systemUserList.length === 0);
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

      handleSysRowMouseEnter (index) {
        this.$set(this.systemUserList[index], 'canEdit', true);
      },

      handleSysRowMouseLeave (index) {
        this.$delete(this.systemUserList[index], 'canEdit');
      },

      handleOpenSysEdit (payload, index) {
        if (!payload.canEdit) {
          return;
        }
        this.$set(this.systemUserList[index], 'isEdit', true);
        this.$nextTick(() => {
          this.$refs[`sysRef${index}`].isEditable = true;
          if (!payload.members.length) {
            setTimeout(() => {
              this.$refs[`sysRef${index}`].$refs.selector.focus();
            }, 10);
          }
        });
      },

      handleSystemRtxChange (payload, row) {
        row.isError = false;
        row.members = [...payload];
      },

      handleSystemRtxEnter (event, payload) {
        if (event.keyCode === 13) {
          event.stopPropagation();
                
          this.handleSystemRtxBlur(payload);
        }
      },

      async handleSystemRtxBlur (payload) {
        const ms = JSON.parse(JSON.stringify(payload.members));
        const mbs = JSON.parse(JSON.stringify(payload.memberBackup));
        if (_.isEqual(ms.sort(), mbs.sort())) {
          setTimeout(() => {
            payload.isEdit = false;
          }, 10);
          return;
        }
        if (payload.members.length < 1) {
          payload.isError = true;
          return;
        }
        const { id, members } = payload;
        try {
          this.$store.dispatch('role/editSystemManagerMember', {
            id,
            members
          });
          setTimeout(() => {
            payload.isEdit = false;
            payload.memberBackup = _.cloneDeep(members);
            this.messageSuccess(this.$t(`m.common['操作成功']`));
          }, 10);
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

      handleUpdateMembers (payload, index) {
        const { members } = payload;
        const { id } = this.systemUserList[index];
        if (!members.length) {
          this.$refs[`sysRef${index}`].isEditable = false;
          this.$set(this.systemUserList[index], 'isEdit', false);
          this.$set(this.systemUserList[index], 'members', []);
        }
        // if (JSON.stringify(members) === JSON.stringify(memberBackup)) {
        //     return;
        // }
        try {
          const params = {
            id,
            members: _.cloneDeep(members.map(item => item.username))
          };
          this.$store.dispatch('role/editSystemManagerMember', params);
          // this.$set(this.systemUserList[index], 'memberBackup', _.cloneDeep(members));
          this.fetchSystemManager();
          this.messageSuccess(this.$t(`m.common['操作成功']`));
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

      handleEmptyChange (index) {
        const users = this.systemUserList[index];
        users.isError = false;
        users.isEdit = false;
      },

      async handleSystemEnabledChange (newVal, oldVal, val, payload) {
        try {
          await this.$store.dispatch('role/editSystemManagerPerm', {
            id: payload.id,
            system_permission_global_enabled: newVal
          });
          payload.system_permission_global_enabled = newVal;
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
      }
    }
  };
</script>
<style lang="postcss">
    .iam-set-system-manager-wrapper {
        .system-user-table-cls {
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

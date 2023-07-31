<template>
  <div class="iam-user-group-member">
    <render-search>
      <div class="flex-between group-member-button">
        <bk-button :disabled="readOnly" @click="handleAddMember">
          {{ $t(`m.userGroup['添加成员']`) }}
        </bk-button>
        <bk-button
          :disabled="isNoBatchDelete()"
          :title="adminGroupTitle"
          @click="handleBatchDelete">
          {{ $t(`m.common['批量移除']`) }}
        </bk-button>
        <div>
          <bk-dropdown-menu
            ref="dropdown"
            :disabled="readOnly"
            @show="handleDropdownShow"
            @hide="handleDropdownHide"
          >
            <div
              class="group-dropdown-trigger-btn"
              slot="dropdown-trigger"
            >
              <span class="group-dropdown-text">{{ $t(`m.userGroup['复制成员']`) }}</span>
              <i
                :class="[
                  'bk-icon icon-angle-down',
                  { 'icon-flip': isDropdownShow }
                ]"
              />
            </div>
            <ul class="bk-dropdown-list" slot="dropdown-content">
              <li>
                <a
                  href="javascript:;"
                  class="copy-selected-members"
                  :data-clipboard-text="formatCopyMembers"
                  @click="handleTriggerCopy(...arguments, 'selected')"
                >
                  {{ $t(`m.userGroup['复制已选成员']`) }}
                </a>
              </li>
              <li>
                <a
                  href="javascript:;"
                  class="copy-selected-members-all"
                  @click="handleTriggerCopy(...arguments, 'all')">
                  {{ $t(`m.userGroup['复制所有成员']`) }}
                </a>
              </li>
            </ul>
          </bk-dropdown-menu>
        </div>
      </div>
      <div slot="right">
        <bk-input
          v-model="keyword"
          style="width: 300px;"
          :placeholder="$t(`m.userGroupDetail['请输入至少3个字符的用户/组织，按enter键搜索']`)"
          @enter="handleKeyWordEnter"
        />
      </div>
    </render-search>
    <bk-table
      :data="tableList"
      size="small"
      ext-cls="user-group-member-table"
      :cell-class-name="getCellClass"
      :outer-border="false"
      :header-border="false"
      :pagination="pagination"
      @page-change="pageChange"
      @page-limit-change="limitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <bk-table-column type="selection" align="center"></bk-table-column>
      <bk-table-column :label="$t(`m.userGroup['用户/组织']`)" width="400">
        <template slot-scope="{ row }">
          <div class="user" v-if="row.type === 'user'" :title="`${row.id}(${row.name})`">
            <Icon type="personal-user" />
            <span class="name">{{ row.id }}</span><span class="count" v-if="row.name !== ''">
              {{ '(' + row.name + ')' }}
            </span>
          </div>
          <div class="depart" v-else :title="row.full_name">
            <Icon type="organization-fill" />
            <span class="name">{{ row.name || '--' }}</span>
            <span class="count" v-if="row.member_count && enableOrganizationCount">({{ row.member_count }})</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.userGroupDetail['所属组织架构']`)" width="400">
        <template slot-scope="{ row }">
          <template v-if="row.type === 'user'">
            <template v-if="row.user_departments && row.user_departments.length">
              <div
                :title="row.user_departments.join(';')"
                v-for="(item,index) in row.user_departments"
                :key="index"
                class="user_departs"
              >
                {{ item}}
              </div>
            </template>
            <template v-else>
              <div>
                --
              </div>
            </template>
          </template>
          <template v-else>
            {{ row.full_name }}
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['加入时间']`)">
        <template slot-scope="{ row }">
          <span :title="row.created_time.replace(/T/, ' ')">{{ row.created_time.replace(/T/, ' ') }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['有效期']`)" prop="expired_at_display"></bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)" width="180">
        <template slot-scope="{ row }">
          <div>
            <bk-button
              text
              theme="primary"
              :disabled="disabledGroup()"
              :title="disabledGroup() ? $t(`m.userGroup['管理员组至少保留一条数据']`) : ''"
              @click="handleDelete(row)">
              {{ $t(`m.common['移除']`) }}
            </bk-button>
            <bk-button v-if="row.expired_at !== PERMANENT_TIMESTAMP"
              theme="primary" style="margin-left: 4px;" text @click="handleShowRenewal(row)">
              {{ $t(`m.renewal['续期']`) }}
            </bk-button>
          </div>
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

    <delete-dialog
      :show.sync="deleteDialog.visible"
      :loading="deleteDialog.loading"
      :title="deleteDialog.title"
      :sub-title="deleteDialog.subTitle"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="hideCancelDelete"
      @on-sumbit="handleSubmitDelete" />

    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :loading="loading"
      :name="name"
      :id="id"
      show-expired-at
      :is-rating-manager="isRatingManager"
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
      @on-after-leave="handleAddAfterClose" />

    <render-renewal-dialog
      :show.sync="isShowRenewalDialog"
      :data="curData"
      :type="curType"
      :loading="renewalLoading"
      @on-submit="handleRenewalSubmit" />
  </div>
</template>
<script>
  import _ from 'lodash';
  import ClipboardJS from 'clipboard';
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { formatCodeData } from '@/common/util';
  import renderRenewalDialog from '@/components/render-renewal-dialog';
  import DeleteDialog from '../common/iam-confirm-dialog';
  import AddMemberDialog from './iam-add-member';

  export default {
    name: '',
    inject: ['getGroupAttributes'],
    components: {
      DeleteDialog,
      AddMemberDialog,
      renderRenewalDialog
    },
    props: {
      id: {
        type: [String, Number],
        default: ''
      },
      name: {
        type: String,
        default: ''
      },
      count: {
        type: Number,
        default: 0
      },
      data: {
        type: Array,
        default: () => []
      },
      readOnly: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        tableList: [],
        tableLoading: false,
        currentSelectList: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        deleteDialog: {
          visible: false,
          title: this.$t(`m.dialog['确认移除']`),
          subTitle: '',
          loading: false
        },
        curMember: {},
        loading: false,
        isShowAddMemberDialog: false,

        isShowRenewalDialog: false,
        curData: {},
        renewalLoading: false,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        adminGroupTitle: '',
        keyword: '',
        enableOrganizationCount: window.ENABLE_ORGANIZATION_COUNT.toLowerCase() === 'true',
        isDropdownShow: false
      };
    },
    computed: {
      ...mapGetters(['user']),
      isNoBatchDelete () {
        return () => {
            const hasData = this.tableList.length && this.currentSelectList.length;
            if (this.getGroupAttributes && this.getGroupAttributes().source_from_role) {
                const isAll = hasData && this.currentSelectList.length === this.pagination.count;
                this.adminGroupTitle = isAll ? this.$t(`m.userGroup['管理员组至少保留一条数据']`) : '';
                return isAll;
            }
            return !hasData;
        };
      },
      isRatingManager () {
          return ['rating_manager', 'subset_manager'].includes(this.user.role.type);
      },
      curType () {
          return this.curData.type || 'department';
      },
      disabledGroup () {
          return () => {
              return this.getGroupAttributes && this.getGroupAttributes().source_from_role
              && this.pagination.count === 1;
          };
      },
      formatCopyMembers () {
        return this.currentSelectList.length
        ? this.currentSelectList.map(v => v.type === 'user' ? v.id : `{${v.id}}${v.name}&full_name=${v.full_name}&count=${v.member_count}*`).join('\n') : '';
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      data: {
        handler (value) {
          this.tableList.splice(0, this.tableList.length, ...value);
        },
        immediate: true
      },
      count: {
        handler (value) {
          this.pagination.count = value;
        },
        immediate: true
      }
    },
    created () {
      this.PERMANENT_TIMESTAMP = PERMANENT_TIMESTAMP;
      this.fetchMemberList();
      // window.addEventListener('message', this.fetchReceiveData);
    },
    methods: {
      // 接收iframe父页面传递的message
      fetchReceiveData (payload) {
        const { data } = payload;
        console.log(data, '接受传递过来的数据');
        // this.fetchResetData(data);
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 2) {
          return 'iam-table-cell-depart-cls';
        }
        return '';
      },

      async handleKeyWordEnter () {
        this.emptyData.tipType = 'search';
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
        this.fetchMemberList();
      },

      async fetchMemberList () {
        this.tableLoading = true;
        try {
          const params = {
            id: this.id,
            limit: this.pagination.limit,
            offset: this.pagination.limit * (this.pagination.current - 1),
            keyword: this.keyword
          };
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupMemberList', params);
          this.pagination.count = data.count || 0;
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.tableList = [];
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.tableLoading = false;
        }
      },

      handleDropdownShow () {
        this.isDropdownShow = true;
      },

      handleDropdownHide () {
        this.isDropdownShow = false;
      },

      async handleTriggerCopy (event, payload) {
        // 需先保存currentTarget，因为此方法为异步方法，同步代码执行完成后，浏览器会将event事件对象的currentTarget值重置为空
        const currentTarget = event.currentTarget;
        const typeMap = {
          selected: () => {
            if (!this.currentSelectList.length) {
              this.messageError(this.$t(`m.verify['请选择用户或组织成员']`), 2000);
              return;
            }
            const clipboard = new ClipboardJS('.copy-selected-members');
            clipboard.on('success', () => {
              this.messageSuccess(this.$t(`m.info['已经复制到粘贴板，可在其他用户组添加成员时粘贴到手动输入框']`), 2000, 2);
              // 调用后销毁，避免多次执行
              if (clipboard) {
                clipboard.destroy();
              }
            });
            clipboard.on('error', (e) => {
              console.error('复制失败', e);
            });
          },
          all: async () => {
            const params = {
              id: this.id,
              offset: 0,
              limit: 1000
            };
            const { data } = await this.$store.dispatch('userGroup/getUserGroupMemberList', params);
            if (data && data.results) {
              if (!data.results.length) {
                this.messageError(this.$t(`m.common['暂无可复制内容']`), 2000);
                return;
              }
              const clipboard = new ClipboardJS(event.target, {
                text: () => data.results.map(v => v.type === 'user' ? v.id : `{${v.id}}${v.name}&full_name=${v.full_name}&count=${v.member_count}*`).join('\n')
              });
              clipboard.on('success', () => {
                this.messageSuccess(this.$t(`m.info['已经复制到粘贴板，可在其他用户组添加成员时粘贴到手动输入框']`), 2000, 2);
              });
              clipboard.on('error', (e) => {
                console.error('复制失败', e);
              });
              clipboard.onClick({ currentTarget });
              // 调用后销毁，避免多次执行
              if (clipboard) {
                clipboard.destroy();
              }
            }
          }
        };
        typeMap[payload]();
        this.$refs.dropdown.hide();
      },

      async handleEmptyClear () {
        this.handleEmptyRefresh();
      },

      async handleEmptyRefresh () {
        this.emptyData.tipType = '';
        this.keyword = '';
        this.pagination = Object.assign(
          this.pagination,
          {
            current: 1,
            limit: 10
          });
        await this.fetchMemberList();
      },

      handleShowRenewal (payload) {
        this.isShowRenewalDialog = true;
        this.curData = Object.assign({}, payload);
      },

      handleAddMember () {
        this.isShowAddMemberDialog = true;
      },

      handleCancelAdd () {
        this.isShowAddMemberDialog = false;
      },

      handleAddAfterClose () {
      },

      async handleSubmitAdd (payload) {
        const externalPayload = _.cloneDeep(payload);
        this.loading = true;
        const { users, departments, expiredAt } = payload;
        let expired = payload.policy_expired_at;
        // 4102444800：非永久时需加上当前时间
        if (expiredAt !== 4102444800) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex(item => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          expired = expired + nowSecond;
        }
        const arr = [];
        if (departments.length > 0) {
          arr.push(...departments.map(item => {
            return {
              id: item.id,
              type: 'department'
            };
          }));
        }
        if (users.length > 0) {
          arr.push(...users.map(item => {
            return {
              id: item.username,
              type: 'user'
            };
          }));
        }
        const params = {
          members: arr,
          expired_at: expired,
          id: this.id
        };
        try {
          const { code, data } = await this.$store.dispatch('userGroup/addUserGroupMember', params);
          if (code === 0 && data) {
            window.parent.postMessage({ type: 'IAM', data: externalPayload, code: 'add_user_confirm' }, '*');
            this.isShowAddMemberDialog = false;
            this.messageSuccess(this.$t(`m.info['添加成员成功']`), 2000);
            this.fetchMemberList();
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
        } finally {
          this.loading = false;
        }
      },

      handleBatchDelete () {
        if (this.currentSelectList.length === 1) {
          const payload = this.currentSelectList[0];
          this.deleteDialog.subTitle
            = `${this.$t(`m.common['移除']`)}${this.$t(`m.common['【']`)}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['该成员将不再继承该组的权限']`)}${this.$t(`m.common['。']`)}`;
        } else {
          this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)} ${this.currentSelectList.length} ${this.$t(`m.common['位成员']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['这些成员将不再继承该组的权限']`)}${this.$t(`m.common['。']`)}`;
        }
        this.deleteDialog.visible = true;
      },

      handleDelete (payload) {
        this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(`m.common['【']`)}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['该成员将不再继承该组的权限']`)}${this.$t(`m.common['。']`)}`;
        this.deleteDialog.visible = true;
        this.curMember = Object.assign({}, {
          id: payload.id,
          type: payload.type
        });
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchMemberList();
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchMemberList();
      },

      handlerAllChange (selection) {
        this.currentSelectList = [...selection];
      },

      handlerChange (selection, row) {
        this.currentSelectList = [...selection];
      },

      handleAfterDeleteLeave () {
        this.deleteDialog.subTitle = '';
        this.curMember = {};
      },

      hideCancelDelete () {
        this.deleteDialog.visible = false;
      },

      async handleSubmitDelete () {
        this.deleteDialog.loading = true;
        try {
          const params = {
            id: this.id,
            members: this.curMember.id
              ? [this.curMember]
              : this.currentSelectList.map(({ id, type }) => ({ id, type }))
          };
          const { code, data } = await this.$store.dispatch('userGroup/deleteUserGroupMember', params);
          if (code === 0 && data) {
            const externalParams = {
                            ...params,
                            count: params.members.length
            };
            window.parent.postMessage({ type: 'IAM', data: externalParams, code: 'remove_user_confirm' }, '*');
            this.messageSuccess(this.$t(`m.info['移除成功']`), 2000);
            this.currentSelectList = [];
            this.pagination.current = 1;
            this.fetchMemberList();
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
        } finally {
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
        }
      },

      async handleRenewalSubmit (payload) {
        this.renewalLoading = true;
        const { id, type } = this.curData;
        const params = {
          groupId: this.id,
          members: [{
            expired_at: payload,
            id,
            type
          }]
        };
        try {
          await this.$store.dispatch('renewal/groupMemberPermRenewal', params);
          this.messageSuccess(this.$t(`m.renewal['续期成功']`), 2000);
          this.isShowRenewalDialog = false;
          this.fetchMemberList();
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.renewalLoading = false;
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-user-group-member {
        .user-group-member-table {
            margin-top: 16px;
            border: none;
            tr:hover {
                .user,
                .depart {
                    background: #fff;
                }
            }
            .user,
            .depart {
                padding: 4px 6px;
                background: #f0f1f5;
                width: max-content;
                border-radius: 2px;
                i {
                    font-size: 14px;
                    color: #c4c6cc;
                }
                .name {
                    display: inline-block;
                    max-width: 350px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    vertical-align: bottom;
                }
            }
        }
    }
</style>

<style lang="postcss" scoped>
/deep/ .iam-table-cell-depart-cls {
  .cell {
    padding: 5px 0;
    -webkit-line-clamp: 100;
    padding-left: 15px;
    .user_departs {
      margin-bottom: 10px;
      word-break: break-all;
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.group-member-button {
  .bk-button {
    margin-right: 10px;
  }
}

.group-dropdown-trigger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #c4c6cc;
    height: 32px;
    min-width: 68px;
    border-radius: 2px;
    padding: 0 15px;
    color: #63656E;
    &:hover {
      cursor: pointer;
      border-color: #979ba5;
    }
    .group-dropdown-text {
      font-size: 14px;
    }
    .bk-icon {
      font-size: 22px;
    }
}
</style>

<template>
  <div class="iam-member-template-wrapper">
    <render-search>
      <div class="search_left">
        <bk-button theme="primary" @click="handleCreate">
          {{ $t(`m.common['新建']`) }}
        </bk-button>
        <bk-button :disabled="isBatchDisabled" @click="handleBatchAddMember">
          {{ $t(`m.common['批量添加成员']`) }}
        </bk-button>
        <bk-button :disabled="isBatchDisabled" @click="handleBatchDelete">
          {{ $t(`m.common['批量删除']`) }}
        </bk-button>
      </div>
      <div slot="right">
        <IamSearchSelect
          style="width: 420px"
          :placeholder="$t(`m.memberTemplate['搜索模板名称、描述、创建人']`)"
          :data="searchData"
          :value="searchValue"
          :quick-search-method="quickSearchMethod"
          @on-change="handleSearch"
        />
      </div>
    </render-search>
    <bk-table
      ref="memberTemplateRef"
      ext-cls="member-template-table"
      :size="setting.size"
      :data="memberTemplateList"
      :row-class-name="getRowClass"
      :max-height="tableHeight"
      :pagination="pagination"
      :dark-header="true"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
      <bk-table-column v-for="field in setting.selectedFields" :key="field.id" :label="field.label" :prop="field.id">
        <template slot-scope="{ row, $index }">
          <div v-if="['name'].includes(field.id)" class="member-template-name">
            <span
              :class="['single-hide', { 'member-template-name-label': isAddRow && $index === 0 }]"
              :title="row.name"
              @click="handleView(row)"
            >
              {{ row.name }}
            </span>
            <bk-tag v-if="isAddRow && $index === 0" theme="success" type="filled" class="member-template-name-tag">
              new
            </bk-tag>
          </div>
          <div v-if="['member_count'].includes(field.id)">
            <span v-if="row.member_count" class="associate-group-count" @click="handleViewGroup(row)">
              {{ row.member_count }}
            </span>
            <span v-else>--</span>
          </div>
          <span v-if="!['name', 'member_count'].includes(field.id)">
            {{ row[field.id] || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)">
        <template slot-scope="{ row }">
          <div class="actions-btn">
            <bk-button
              theme="primary"
              text
              :disabled="row.readonly"
              class="actions-btn-item"
              @click="handleAddMember(row)"
            >
              {{ $t(`m.common['添加成员']`) }}
            </bk-button>
            <bk-popconfirm
              trigger="click"
              placement="bottom-end"
              ext-popover-cls="delete-confirm"
              :confirm-text="$t(`m.common['删除-dialog']`)"
              @confirm="handleConfirmDelete(row.id)"
            >
              <div slot="content">
                <div class="popover-title">
                  <div class="popover-title-text">
                    {{ $t(`m.dialog['确认删除该人员模板？']`) }}
                  </div>
                </div>
                <div class="popover-content">
                  <div class="popover-content-item">
                    <span class="popover-content-item-label">{{ $t(`m.memberTemplate['用户组名称']`) }}:</span>
                    <span class="popover-content-item-value"> {{ row.name }}</span>
                  </div>
                  <div class="popover-content-tip">
                    {{ $t(`m.memberTemplate['删除后，关联用户组也会删除对应的人员权限。']`) }}
                  </div>
                </div>
              </div>
              <bk-button theme="primary" text class="actions-btn-item">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </bk-popconfirm>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column type="setting" :tippy-options="{ zIndex: 3000 }">
        <bk-table-setting-content
          :fields="setting.fields"
          :selected="setting.selectedFields"
          :size="setting.size"
          @setting-change="handleSettingChange"
        />
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

    <MemberTemplateDetailSlider :show.sync="isShowDetailSlider" :cur-detail-data="curDetailData" />

    <AddMemberTemplateSlider :show.sync="isShowAddSlider" @on-submit="handleTempSubmit" />

    <AddMemberDialog
      :show.sync="isShowAddMemberDialog"
      :is-batch="isBatch"
      :loading="memberDialogLoading"
      :name="curName"
      :id="curId"
      :show-limit="false"
      :is-rating-manager="isRatingManager"
      show-expired-at
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
      @on-after-leave="handleAddAfterClose"
    />

    <DeleteActionDialog
      :show.sync="isShowDeleteDialog"
      :loading="batchQuitLoading"
      :width="formatDeleteWidth"
      :title="delActionDialogTitle"
      :tip="delActionDialogTip"
      :name="currentActionName"
      :related-action-list="delActionList"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="handleCancelDelete"
      @on-submit="handleSubmitDelete"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import { MEMBERS_TEMPLATE_FIELDS } from '@/common/constants';
  import IamSearchSelect from '@/components/iam-search-select';
  import MemberTemplateDetailSlider from './components/member-template-detail-slider.vue';
  import AddMemberTemplateSlider from './components/add-member-template-slider.vue';
  import AddMemberDialog from '@/views/group/components/iam-add-member.vue';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';

  export default {
    components: {
      IamSearchSelect,
      MemberTemplateDetailSlider,
      AddMemberTemplateSlider,
      AddMemberDialog,
      DeleteActionDialog
    },
    data () {
      return {
        memberTemplateList: [],
        currentSelectList: [],
        searchList: [],
        searchValue: [],
        delActionList: [],
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.memberTemplate['模板名称']`),
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.memberTemplate['描述']`),
            default: true
          },
          {
            id: 'creator',
            name: this.$t(`m.grading['创建人']`),
            default: true
          }
        ],
        searchParams: {},
        queryParams: {},
        pagination: {
          current: 1,
          limit: 10,
          count: 0
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        setting: {
          fields: MEMBERS_TEMPLATE_FIELDS,
          selectedFields: MEMBERS_TEMPLATE_FIELDS.filter((item) => !['updated_time', 'updated_by'].includes(item.id)),
          size: 'small'
        },
        tableLoading: false,
        memberDialogLoading: false,
        isShowDetailSlider: false,
        isShowAddSlider: false,
        isShowAddMemberDialog: false,
        isShowDeleteDialog: false,
        isAddRow: false,
        isBatch: false,
        batchQuitLoading: false,
        curRole: '',
        curName: '',
        currentActionName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        curId: 0,
        curDetailData: {}
      };
    },
    computed: {
    ...mapGetters(['user', 'externalSystemId']),
    isBatchDisabled () {
      return this.currentSelectList.length === 0;
    },
    tableHeight () {
      return getWindowHeight() - 185;
    },
    isRatingManager () {
      return ['rating_manager', 'subset_manager'].includes(this.curRole);
    },
    formatDeleteWidth () {
      return this.curLanguageIsCn ? 700 : 1000;
    }
    },
    watch: {
      user: {
        handler (value) {
          this.curRole = value.role.type || 'staff';
        },
        immediate: true
      }
    },
    async created () {
      await this.fetchMemberTemplateList(true);
    },
    methods: {
      async fetchMemberTemplateList (tableLoading = false) {
        this.tableLoading = tableLoading;
        try {
          const { current, limit } = this.pagination;
          const params = {
            page: current,
            page_size: limit,
          ...this.searchParams
          };
          const { data } = await this.$store.dispatch('memberTemplate/getSubjectTemplateList', params);
          const { count, results } = data;
          this.pagination.count = count;
          this.memberTemplateList = results || [];
          this.emptyData = formatCodeData(0, this.emptyData, results.length === 0);
          this.$nextTick(() => {
            const currentSelectList = this.currentSelectList.map((item) => item.id);
            this.memberTemplateList.forEach((item) => {
              if (currentSelectList.includes(item.id)) {
                this.$refs.memberTemplateRef && this.$refs.memberTemplateRef.toggleRowSelection(item, true);
              }
            });
            if (this.currentSelectList.length < 1) {
              this.$refs.memberTemplateRef && this.$refs.memberTemplateRef.clearSelection();
            }
          });
        } catch (e) {
          console.error(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.emptyData.tipType = 'search';
        this.queryParams = Object.assign(this.queryParams, {
          current: 1,
          limit: 10
        });
        this.resetPagination();
        await this.fetchMemberTemplateList(true);
      },

      async handleTempSubmit (payload) {
        try {
          const subjects = payload.subjects.map((item) => {
            const { id, username, type } = item;
            if (['depart', 'department'].includes(item.type)) {
              return {
                id,
                type: 'department'
              };
            }
            if (['user'].includes(item.type)) {
              return {
                id: username,
                type
              };
            }
          });
          const params = {
          ...payload,
          ...{
            subjects
          }
          };
          const { code } = await this.$store.dispatch('memberTemplate/createSubjectTemplate', params);
          if (code === 0) {
            this.isAddRow = true;
            this.resetPagination();
            await this.fetchMemberTemplateList();
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleSubmitAdd (payload) {
        const { users, departments, expiredAt } = payload;
        let expired = payload.policy_expired_at;
        // 4102444800：非永久时需加上当前时间
        if (expiredAt !== 4102444800) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex((item) => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          expired = expired + nowSecond;
        }
        const subjects = [];

        if (departments.length > 0) {
          subjects.push(
            ...departments.map((item) => {
              return {
                id: item.id,
                type: 'department'
              };
            })
          );
        }
        if (users.length > 0) {
          subjects.push(
            ...users.map((item) => {
              return {
                id: item.username,
                type: 'user'
              };
            })
          );
        }
        const params = {
          subjects,
          expired_at: expired,
          template_ids: this.isBatch
            ? this.currentSelectList.filter((item) => item.readonly).map((v) => v.id)
            : [this.curId]
        };
        console.log('params', params);
        try {
          this.memberDialogLoading = true;
          await this.$store.dispatch('memberTemplate/addBatchSubjectTemplateMembers', params);
          this.isShowAddMemberDialog = false;
          this.messageSuccess(this.$t(`m.info['添加成员成功']`), 3000);
          this.resetPagination();
          this.fetchMemberTemplateList(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.memberDialogLoading = false;
        }
      },

      async handleSubmitDelete () {
        this.batchQuitLoading = true;
        const selectGroups = this.currentSelectList;
        try {
          for (let i = 0; i < selectGroups.length; i++) {
            await this.$store.dispatch('memberTemplate/deleteSubjectTemplate', {
              type: 'group',
              id: selectGroups[i].id
            });
          }
          this.isShowDeleteDialog = false;
          this.currentSelectList = [];
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.resetPagination();
          this.fetchMemberTemplateList(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.batchQuitLoading = false;
        }
      },

      async handleConfirmDelete (id) {
        try {
          const { code } = await this.$store.dispatch('memberTemplate/deleteSubjectTemplate', { id });
          if (code === 0) {
            // const tableIndex = this.memberTemplateList.findIndex((item) => item.id === id);
            // if (tableIndex > -1) {
            //   this.memberTemplateList.splice(tableIndex, 1);
            // }
            this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            this.currentSelectList = [];
            await this.fetchMemberTemplateList(true);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleCreate () {
        this.isShowAddSlider = true;
      },

      handleView (payload) {
        this.curDetailData = Object.assign(payload, {
          tabActive: 'basic_info'
        });
        this.isShowDetailSlider = true;
      },

      handleViewGroup (payload) {
        this.curDetailData = Object.assign(payload, {
          tabActive: 'associate_groups'
        });
        this.isShowDetailSlider = true;
      },

      handleAddMember (payload) {
        const { id, name } = payload;
        this.curName = name;
        this.curId = id;
        this.isShowAddMemberDialog = true;
      },

      handleBatchAddMember () {
        const hasDisabledData = this.currentSelectList.filter((item) => item.readonly);
        if (hasDisabledData.length) {
          const disabledNames = hasDisabledData.map((item) => item.name);
          this.messageWarn(
            this.$t(`m.info['只读人员模板不能添加成员']`, {
              value: `${this.$t(`m.common['【']`)}${disabledNames}${this.$t(`m.common['】']`)}`
            }),
            3000
          );
          return;
        }
        this.isBatch = true;
        this.isShowAddMemberDialog = true;
      },

      // 批量操作对应操作项
      handleDeleteActions (type) {
        const typeMap = {
          delete: () => {
            this.isShowDeleteDialog = true;
            this.delActionDialogTitle = this.$t(`m.dialog['确认批量删除所选的人员模板吗？']`);
            this.delActionDialogTip = this.$t(`m.memberTemplate['删除后，关联用户组也会删除对应的人员权限。']`);
            this.delActionList = this.currentSelectList;
          }
        };
        return typeMap[type]();
      },

      handleBatchDelete () {
        this.handleDeleteActions('delete');
      },

      fetchSelectedGroupCount () {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.groupPermTableRef && selectionCount) {
            selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
          }
        });
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter((item) => item.id !== row.id);
            }
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName('bk-page-selection-count');
              if (this.$refs.memberTemplateRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
          },
          all: () => {
            const tableList = _.cloneDeep(this.memberTemplateList);
            const selectGroups = this.currentSelectList.filter((item) => !tableList.map((v) => v.id).includes(item.id));
            this.currentSelectList = [...selectGroups, ...payload];
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName('bk-page-selection-count');
              if (this.$refs.memberTemplateRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
          }
        };
        return typeMap[type]();
      },

      handlerAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handlerChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handlePageChange (page) {
        this.pagination.current = page;
        this.fetchMemberTemplateList(true);
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { limit });
        this.fetchMemberTemplateList(true);
      },

      handleSettingChange ({ fields, size }) {
        this.setting.size = size;
        this.setting.selectedFields = fields;
      },

      handleCancelAdd () {
        this.curId = 0;
        this.isShowAddMemberDialog = false;
      },

      handleAddAfterClose () {
        this.curName = '';
        this.curId = 0;
      },

      handleAfterDeleteLeave () {
        this.currentActionName = '';
        this.delActionList = [];
        this.policyIdList = [];
      },

      handleCancelDelete () {
        this.isShowDeleteDialog = false;
      },

      handleEmptyClear () {
        this.handleEmptyRefresh();
      },

      handleEmptyRefresh () {
        this.queryParams = {};
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.resetPagination();
        this.fetchMemberTemplateList(true);
      },

      resetPagination () {
        this.pagination = Object.assign(
          {},
          {
            limit: 10,
            current: 1,
            count: 0
          }
        );
      },

      getDefaultSelect () {
        return this.memberTemplateList.length > 0;
      },

      getRowClass ({ row, rowIndex }) {
        if (rowIndex === 0 && this.isAddRow) {
          return 'member-template-table-add';
        }
        return '';
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-member-template-wrapper {
  .member-template-table {
    margin-top: 20px;

    .member-template-name {
      display: flex;
      align-items: center;
      color: #3a84ff;
      cursor: pointer;

      &-label {
        max-width: calc(100% - 50px);
        word-break: break-all;
      }

      &-tag {
        background-color: #2dcb56;
        font-size: 10px;
        height: 12px;
        line-height: 1;
        padding: 0 4px;
        margin-left: 5px;
      }
    }

    .associate-group-count {
      color: #3a84ff;
      cursor: pointer;
    }

    .actions-btn {
      &-item {
        margin-right: 10px;
      }
    }

    /deep/ .member-template-table-add {
      background-color: #f2fff4;
    }
  }
}

.delete-confirm {
  .popover-title {
    font-size: 16px;
    padding-bottom: 16px;
  }

  .popover-content {
    color: #63656e;

    .popover-content-item {
      display: flex;

      &-value {
        color: #313238;
        margin-left: 5px;
      }
    }

    &-tip {
      padding: 6px 0 24px 0;
    }
  }
}

/deep/ .content-line-height {
  display: none;
}
</style>

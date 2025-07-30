<template>
  <div class="iam-member-template-wrapper">
    <render-search>
      <div class="search_left">
        <bk-button theme="primary" @click="handleCreate">
          {{ $t(`m.common['新建']`) }}
        </bk-button>
        <bk-popover
          :content="isBatchAddMemberDisabled('title')"
          :disabled="!isBatchAddMemberDisabled('disabled')"
        >
          <bk-button :disabled="isBatchAddMemberDisabled('disabled')" @click="handleBatchAddMember">
            {{ $t(`m.common['批量添加成员']`) }}
          </bk-button>
        </bk-popover>
        <bk-popover
          :content="isBatchDeleteDisabled('title')"
          :disabled="!isBatchDeleteDisabled('disabled')"
        >
          <bk-button :disabled="isBatchDeleteDisabled('disabled')" @click="handleBatchDelete">
            {{ $t(`m.common['批量删除']`) }}
          </bk-button>
        </bk-popover>
      </div>
      <div slot="right">
        <IamSearchSelect style="width: 420px" :placeholder="$t(`m.memberTemplate['搜索模板名称、描述、创建人']`)" :data="searchData"
          :value="searchValue" :quick-search-method="quickSearchMethod" @on-change="handleSearch" />
      </div>
    </render-search>
    <bk-table
      ref="memberTemplateRef"
      ext-cls="member-template-table"
      :size="setting.size"
      :data="memberTemplateList"
      :custom-header-color="'#fafbfd'"
      :dark-header="true"
      :row-class-name="getRowClass"
      :max-height="tableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" fixed="left" />
      <bk-table-column
        v-for="field in setting.selectedFields"
        :key="field.id"
        :label="field.label"
        :prop="field.id"
        :fixed="field.fixed"
      >
        <template slot-scope="{ row }">
          <div v-if="['name'].includes(field.id)" class="member-template-name">
            <span
              :class="[
                'single-hide',
                { 'member-template-name-label': isShowNewTag(row) }
              ]"
              :title="row.name"
              @click="handleViewGroup(row, 'basic_info')">
              {{ row.name }}
            </span>
            <bk-tag v-if="isShowNewTag(row)" theme="success" type="filled" class="member-template-name-tag">
              new
            </bk-tag>
          </div>
          <template v-if="['group_count'].includes(field.id)">
            <span v-if="row.group_count >= 0" class="associate-group-count"
              @click="handleViewGroup(row, 'associate_groups')">
              {{ row.group_count }}
            </span>
            <span v-else>--</span>
          </template>
          <template v-if="['creator'].includes(field.id)">
            <IamUserDisplayName :user-id="row.creator" />
          </template>
          <span v-if="!['name', 'group_count', 'creator'].includes(field.id)">
            {{ row[field.id] || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" fixed="right" :width="150">
        <template slot-scope="{ row }">
          <div class="actions-btn">
            <bk-popover
              :content="row.readonly ? $t(`m.memberTemplate['只读人员模板不能添加成员']`) : ''"
              :disabled="!row.readonly">
              <bk-button
                theme="primary"
                text
                :disabled="row.readonly"
                class="actions-btn-item"
                @click="handleAddMember(row)"
              >
                {{ $t(`m.common['添加成员']`) }}
              </bk-button>
            </bk-popover>
            <bk-popconfirm trigger="click" placement="bottom-end" ext-popover-cls="delete-confirm"
              :confirm-text="$t(`m.common['删除-dialog']`)" @confirm="handleConfirmDelete(row.id)">
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
              <bk-popover
                :content="formatDelAction(row, 'title')"
                :disabled="formatDelAction(row, 'title') ? false : true">
                <bk-button
                  theme="primary"
                  text
                  class="actions-btn-item"
                  :disabled="formatDelAction(row, 'disabled')"
                >
                  {{ $t(`m.common['删除']`) }}
                </bk-button>
              </bk-popover>
            </bk-popconfirm>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column type="setting" :tippy-options="{ zIndex: 3000 }">
        <bk-table-setting-content :fields="setting.fields" :selected="setting.selectedFields" :size="setting.size"
          @setting-change="handleSettingChange" />
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty :type="emptyData.type" :empty-text="emptyData.text" :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType" @on-clear="handleEmptyClear" @on-refresh="handleEmptyRefresh" />
      </template>
    </bk-table>

    <MemberTemplateDetailSlider :show.sync="isShowDetailSlider" :cur-detail-data="curDetailData" />

    <AddMemberTemplateSlider
      ref="addMemberRef"
      :show.sync="isShowAddSlider"
      :is-rating-manager="isRatingManager"
      @on-submit="handleTempSubmit"
    />

    <AddMemberDialog
      :show.sync="isShowAddMemberDialog"
      :is-rating-manager="isRatingManager"
      :is-batch="isBatch"
      :loading="memberDialogLoading"
      :title="memberDialogTitle"
      :name="curName"
      :id="curId"
      :show-limit="false"
      :route-mode="'memberTemplate'"
      :show-expired-at="false"
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd" @on-after-leave="handleAddAfterClose" />

    <DeleteActionDialog :show.sync="isShowDeleteDialog" :loading="batchQuitLoading" :width="formatDeleteWidth"
      :title="delActionDialogTitle" :tip="delActionDialogTip" :name="currentActionName"
      :related-action-list="formatDisableGroup" @on-after-leave="handleAfterDeleteLeave" @on-cancel="handleCancelDelete"
      @on-submit="handleSubmitDelete" />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData, getWindowHeight, xssFilter } from '@/common/util';
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
        readOnlyGroups: [],
        hasRelatedGroups: [],
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
          count: 0,
          showTotalCount: true
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
        memberDialogTitle: '',
        currentActionName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        curId: 0,
        createId: 0,
        curDetailData: {},
        tableHeight: getWindowHeight() - 185
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isAllReadOnly () {
        return this.currentSelectList.filter((item) => item.readonly).length === this.currentSelectList.length;
      },
      isAllRelated () {
        return this.currentSelectList.filter((item) => item.group_count > 0).length === this.currentSelectList.length;
      },
      isAllDisabled () {
        const readOnlyList = this.currentSelectList.filter((item) => item.readonly).map((v) => v.id);
        const relatedList = this.currentSelectList.filter(
          (item) => item.group_count > 0 && !readOnlyList.includes(item.id));
        if (!this.currentSelectList.length) {
          return true;
        }
        return readOnlyList.length + relatedList.length === this.currentSelectList.length;
      },
      isBatchAddMemberDisabled () {
        return (payload) => {
          const typeMap = {
            title: () => {
              if (!this.currentSelectList.length) {
                return this.$t(`m.memberTemplate['请勾选人员模板']`);
              }
              if ((this.isAllReadOnly && this.currentSelectList.length > 0)) {
                return this.$t(`m.memberTemplate['当前勾选项皆为只读人员模板']`);
              }
              return '';
            },
            disabled: () => {
              if ((this.isAllReadOnly && this.currentSelectList.length > 0) || !this.currentSelectList.length) {
                return true;
              }
              return false;
            }
          };
         return typeMap[payload]();
        };
      },
      isBatchDeleteDisabled () {
        return (payload) => {
          const typeMap = {
            title: () => {
              if (!this.currentSelectList.length) {
                return this.$t(`m.memberTemplate['请勾选人员模板']`);
              }
              if (this.isAllReadOnly) {
                return this.$t(`m.memberTemplate['当前勾选项皆为只读人员模板']`);
              }
              if (this.isAllRelated) {
                return this.$t(`m.memberTemplate['当前勾选项皆为有关联用户组人员模板']`);
              }
              if (this.isAllDisabled) {
                return this.$t(`m.memberTemplate['当前勾选项皆为只读和有关联用户组人员模板']`);
              }
              return '';
            },
            disabled: () => {
              if (this.isAllReadOnly || this.isAllRelated || this.isAllDisabled || !this.currentSelectList.length) {
                return true;
              }
              return false;
            }
          };
         return typeMap[payload]();
        };
      },
      isRatingManager () {
        return ['rating_manager', 'subset_manager'].includes(this.curRole);
      },
      isShowNewTag () {
        return (payload) => {
          return this.isAddRow && this.createId === payload.id;
        };
      },
      formatDeleteWidth () {
        return this.curLanguageIsCn ? 700 : 1000;
      },
      curSelectIds () {
        return this.currentSelectList.map((item) => item.id);
      },
      formatDelAction () {
        return ({ readonly, group_count }, type) => {
          const typeMap = {
            title: () => {
              if (readonly) {
                return this.$t(`m.memberTemplate['只读人员模板不可删除']`);
              }
              // eslint-disable-next-line camelcase
              if (group_count > 0) {
                return this.$t(`m.info['有关联的用户组, 无法删除']`);
              }
              return '';
            },
            disabled: () => {
              // eslint-disable-next-line camelcase
              if (readonly || group_count > 0) {
                return true;
              }
              return false;
            }
          };
          return typeMap[type]();
        };
      },
      formatDisableGroup () {
        return this.currentSelectList.filter((item) => item.readonly || item.group_count > 0);
      }
    },
    watch: {
      user: {
        handler (value) {
          this.curRole = value.role.type || 'staff';
        },
        immediate: true
      },
      '$route': {
        handler (value) {
    
        },
        immediate: true
      }
    },
    async created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 185;
      });
      this.handleFilterSearchByOther();
      await this.fetchMemberTemplateList(true);
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-info-change');
        bus.$off('on-related-change');
      });
      bus.$on('on-info-change', (payload) => {
        const { id, name, description } = payload;
        const index = this.memberTemplateList.findIndex((item) => item.id === id);
        if (index > -1) {
          this.memberTemplateList[index] = Object.assign(this.memberTemplateList[index], {
            name,
            description
          });
        }
      });
      bus.$on('on-related-change', (payload) => {
        const { id, group_count } = payload;
        const index = this.memberTemplateList.findIndex((item) => item.id === id);
        if (index > -1) {
          this.memberTemplateList[index] = Object.assign(this.memberTemplateList[index], {
            group_count
          });
        }
      });
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
          this.fetchSelectedGroupCount();
          this.handleOpenDetail();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      // 处理从其他页面传递参数进行数据过滤
      handleFilterSearchByOther () {
        if (this.$route.query.template_name) {
          this.searchParams.name = this.$route.query.template_name;
          this.searchValue.push({
            id: 'name',
            name: this.$t(`m.memberTemplate['模板名称']`),
            values: [{
              id: this.searchParams.name,
              name: this.searchParams.name
            }]
          });
        }
      },

      // 处理从人员模板加入的用户组跳转
      handleOpenDetail () {
        const { template_name: templateName, tab_active: tabActive } = this.$route.query;
        if (this.memberTemplateList.length && templateName && tabActive) {
          this.curDetailData = Object.assign(
            {},
            {
                ...this.memberTemplateList[0],
                ...{
                  tabActive
                }
            });
          this.isShowDetailSlider = true;
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
          const { code, data } = await this.$store.dispatch('memberTemplate/createSubjectTemplate', params);
          if (code === 0) {
            this.$bkMessage({
              limit: 1,
              theme: 'success',
              message: this.$t(`m.memberTemplate['人员模板创建成功']`),
              ellipsisLine: 2,
              ellipsisCopy: true
            });
            this.createId = data.id || 0;
            this.isAddRow = true;
            this.isShowAddSlider = false;
            this.$refs.addMemberRef && this.$refs.addMemberRef.resetData();
            this.resetPagination();
            await this.fetchMemberTemplateList();
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleSubmitAdd (payload) {
        const { users, departments } = payload;
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
          id: this.curId
        };
        let url = 'addSubjectTemplateMembers';
        if (this.isBatch) {
          params.template_ids = this.curSelectIds;
          delete params.id;
          url = 'addBatchSubjectTemplateMembers';
        }
        console.log('params', params);
        try {
          this.memberDialogLoading = true;
          await this.$store.dispatch(`memberTemplate/${url}`, params);
          this.isShowAddMemberDialog = false;
          this.messageSuccess(this.$t(`m.info['添加成员成功']`), 3000);
          this.currentSelectList = [];
          this.resetPagination();
          this.fetchMemberTemplateList(true);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.memberDialogLoading = false;
        }
      },

      async handleSubmitDelete () {
        const selectGroups = this.currentSelectList.filter((item) => !item.readonly && item.group_count === 0);
        this.batchQuitLoading = true;
        try {
          for (let i = 0; i < selectGroups.length; i++) {
            await this.$store.dispatch('memberTemplate/deleteSubjectTemplate', {
              type: 'template',
              id: selectGroups[i].id
            });
          }
          this.isShowDeleteDialog = false;
          this.currentSelectList = [];
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.isAddRow = false;
          this.resetPagination();
          this.fetchMemberTemplateList(true);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.batchQuitLoading = false;
        }
      },

      async handleConfirmDelete (id) {
        try {
          const { code } = await this.$store.dispatch('memberTemplate/deleteSubjectTemplate', { id });
          if (code === 0) {
            this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            this.currentSelectList = [];
            this.isAddRow = false;
            this.resetPagination();
            await this.fetchMemberTemplateList(true);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleCreate () {
        this.isShowAddSlider = true;
      },

      handleViewGroup (payload, tabActive) {
        this.curDetailData = Object.assign(payload, {
          tabActive
        });
        this.isShowDetailSlider = true;
      },

      handleAddMember (payload) {
        const { id, name } = payload;
        this.curName = name;
        this.curId = id;
        this.isBatch = false;
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
            this.delActionDialogTitle = this.$t(`m.dialog['确认批量删除所选的人员模板吗？']`);
            this.delActionDialogTip = this.$t(`m.memberTemplate['以下为只读或有关联用户组的人员模板，不可删除。']`);
            this.readOnlyGroups = this.currentSelectList.filter((item) => item.readonly);
            this.hasRelatedGroups = this.currentSelectList.filter((item) => item.group_count > 0);
            this.isShowDeleteDialog = true;
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
          if (this.$refs.memberTemplateRef && selectionCount && selectionCount.length && selectionCount[0].children) {
            selectionCount[0].children[0].innerHTML = xssFilter(this.currentSelectList.length);
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
            this.fetchSelectedGroupCount();
          },
          all: () => {
            const tableList = _.cloneDeep(this.memberTemplateList);
            const selectGroups = this.currentSelectList.filter((item) => !tableList.map((v) => v.id).includes(item.id));
            this.currentSelectList = [...selectGroups, ...payload];
            this.fetchSelectedGroupCount();
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
        this.readOnlyGroups = [];
        this.hasRelatedGroups = [];
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
        this.pagination = Object.assign(this.pagination, {
          current: 1,
          count: 0
        });
      },

      getDefaultSelect () {
        return this.memberTemplateList.length > 0;
      },

      getRowClass ({ row }) {
        if (row.id === this.createId && this.isAddRow) {
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
  /deep/ .member-template-table {
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

    /deep/ .bk-form-checkbox.is-checked {
      .bk-checkbox {
        border-color: #3a84ff;
        background-color: #3a84ff;
        &:hover {
          background-color: #3a84ff;
        }
      }
    }

    .bk-table-fixed, .bk-table-fixed-right {
      border-bottom: 0;
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

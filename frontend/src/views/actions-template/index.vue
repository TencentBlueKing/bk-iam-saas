<template>
  <div class="iam-actions-template-wrapper">
    <render-search>
      <div class="form-operate-btn">
        <bk-button theme="primary" @click="handleCreate">
          {{ $t(`m.common['新建']`) }}
        </bk-button>
        <bk-popover
          :content="formatDisabledContent('delete')"
          :disabled="!isBatchDeleteDisabled"
        >
          <bk-button
            :disabled="isBatchDeleteDisabled"
            @click="handleBatch('delete')"
          >
            {{ $t(`m.common['批量删除']`) }}
          </bk-button>
        </bk-popover>
      </div>
      <div slot="right">
        <IamSearchSelect
          style="width: 540px"
          :placeholder="$t(`m.actionsTemplate['搜索 模板名称、所属系统、创建人、描述']`)"
          :data="searchData"
          :value="searchValue"
          @on-change="handleSearch"
        />
      </div>
    </render-search>
    <bk-table
      ref="actionsTemplateRef"
      size="small"
      ext-cls="actions-template-table"
      :class="{ 'set-border': tableLoading }"
      :data="actionsTempList"
      :max-height="tableHeight"
      :pagination="pagination"
      @select="handleChange"
      @select-all="handleAllChange"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" fixed="left" />
      <bk-table-column :label="$t(`m.actionsTemplate['模板名称']`)" :min-width="220">
        <template slot-scope="{ row }">
          <div class="actions-template-name">
            <div
              :class="[
                'single-hide name',
                { 'is-lock': row.is_lock }
              ]"
              v-bk-tooltips="{ content: row.name, placement: 'right-start' }"
              @click="handleView(row, 'basic_info')"
            >
              {{ row.name }}
            </div>
            <bk-tag theme="warning" v-if="row.is_lock">{{ $t(`m.permTemplate['编辑中']`) }}</bk-tag>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['所属系统']`)" prop="system.name" :min-width="100" />
      <bk-table-column :label="$t(`m.permTemplate['关联的组']`)">
        <template slot-scope="{ row }">
          <div class="associate-groups">
            <bk-button v-if="!!row.subject_count" text theme="primary" @click="handleView(row, 'associate_groups')">
              {{ row.subject_count }}
            </bk-button>
            <span v-else>0</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.permTemplate['创建人']`)" prop="creator" />
      <bk-table-column :label="$t(`m.common['创建时间']`)" prop="created_time" :min-width="160" />
      <bk-table-column :label="$t(`m.common['描述']`)" width="300">
        <template slot-scope="{ row }">
          <span v-bk-tooltips="{ content: row.description, placement: 'left-start', disabled: !row.description }">
            {{ row.description || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" :min-width="120" fixed="right">
        <template slot-scope="{ row }">
          <span>
            <bk-button theme="primary" text class="table-operate-btn" @click.stop="handleEdit(row)">
              {{ $t(`m.common['编辑']`) }}
            </bk-button>
            <bk-popconfirm
              trigger="click"
              placement="bottom-end"
              ext-popover-cls="actions-template-delete-confirm"
              :width="280"
              :confirm-text="$t(`m.common['确定']`)"
              @confirm="handleTemplateDelete(row)"
            >
              <div slot="content">
                <div class="popover-title">
                  <div class="popover-title-text">
                    {{ $t(`m.dialog['确认删除该操作模板？']`) }}
                  </div>
                </div>
                <div class="popover-content">
                  <div class="popover-content-item">
                    <span class="popover-content-item-label">{{ $t(`m.memberTemplate['模板名称']`) }}:</span>
                    <span class="popover-content-item-value"> {{ row.name }}</span>
                  </div>
                  <div class="popover-content-tip">
                    {{ $t(`m.actionsTemplate['删除后，无法恢复，请谨慎操作！']`) }}
                  </div>
                </div>
              </div>
              <bk-popover
                placement="right-start"
                :content="formatDelAction(row, 'title')"
                :disabled="!formatDelAction(row, 'title')">
                <bk-button
                  theme="primary"
                  text
                  class="table-operate-btn"
                  :disabled="formatDelAction(row, 'disabled')"
                >
                  {{ $t(`m.common['删除']`) }}
                </bk-button>
              </bk-popover>
            </bk-popconfirm>
          </span>
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

    <ActionsTemplateDetailSlider
      :show.sync="isShowDetailSlider"
      :cur-detail-data="curDetailData"
      @on-delete="handleTemplateDelete"
    />

    <DeleteActionDialog
      :show.sync="isShowDeleteDialog"
      :loading="batchQuitLoading"
      :title="delActionDialogTitle"
      :tip="delActionDialogTip"
      :name="currentActionName"
      :width="formatDeleteWidth"
      :related-action-list="formatDisabledGroup"
      @on-after-leave="handleAfterDeleteLeave"
      @on-submit="handleSubmitDelete"
      @on-cancel="handleCancelDelete"
    />
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { bus } from '@/common/bus';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { formatCodeData, getWindowHeight, delLocationHref } from '@/common/util';
  import { addPreUpdateInfo, getActionsData } from '@/views/actions-template/common/actions';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';
  import IamSearchSelect from '@/components/iam-search-select';
  import ActionsTemplateDetailSlider from './components/actions-template-detail-slider.vue';

  export default {
    name: '',
    components: {
      DeleteActionDialog,
      IamSearchSelect,
      ActionsTemplateDetailSlider
    },
    data () {
      return {
        tableLoading: false,
        editLoading: false,
        batchQuitLoading: false,
        isShowDeleteDialog: false,
        isShowDetailSlider: false,
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.actionsTemplate['模板名称']`),
            default: true
          },
          {
            id: 'system_id',
            name: this.$t(`m.common['所属系统']`),
            remoteMethod: this.handleRemoteSystem
          },
          {
            id: 'creator',
            name: this.$t(`m.grading['创建人']`),
            remoteMethod: this.handleRemoteRtx
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            disabled: true
          }
        ],
        searchList: [],
        searchValue: [],
        actionsTempList: [],
        currentSelectList: [],
        hasRelatedGroups: [],
        editRequestQueue: [],
        defaultCheckedActions: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        searchParams: {},
        curDetailData: {},
        queryParams: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        currentActionName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        curTemplateId: '',
        curRole: 'staff',
        currentBackup: 1,
        tableHeight: getWindowHeight() - 185
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isBatchDeleteDisabled () {
        if (this.currentSelectList.length) {
          const result = this.currentSelectList.filter((v) => v.subject_count === 0);
          return !(result.length > 0);
        }
        return true;
      },
      formatDeleteWidth () {
        return this.curLanguageIsCn ? 700 : 1000;
      },
      formatDisabledContent () {
        return (payload) => {
          const typeMap = {
            delete: () => {
              if (!this.currentSelectList.length) {
                return this.$t(`m.verify['请选择操作模板']`);
              }
              return this.$t(`m.info['有关联的用户组, 无法删除']`);
            }
          };
          return typeMap[payload]();
        };
      },
      formatDelAction () {
        return ({ subject_count: subjectCount }, type) => {
          const typeMap = {
            title: () => {
              if (subjectCount > 0) {
                return this.$t(`m.info['有关联的用户组, 无法删除']`);
              }
              return '';
            },
            disabled: () => {
              if (subjectCount > 0) {
                return true;
              }
              return false;
            }
          };
          return typeMap[type]();
        };
      },
      formatDisabledGroup () {
        return this.currentSelectList.filter((item) => item.subject_count > 0);
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      user: {
        handler (value) {
          this.curRole = value.role.type || 'staff';
        },
        immediate: true,
        deep: true
      }
    },
    async created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 185;
      });
    },
    mounted () {
      this.updateSliderOperateData();
    },
    methods: {
      async fetchPageData () {
        await this.fetchTemplateList();
      },
      
      async getPreUpdateInfo () {
        try {
          const { id, system } = this.curDetailData;
          const { data } = await this.$store.dispatch('permTemplate/getPreUpdateInfo', { id });
          // 是否有编辑中的数据
          const flag = Object.keys(data).length > 0;
          if (flag) {
            const params = {
              id,
              data: {
                action_ids: data.action_ids
              }
            };
            const list = cloneDeep(this.curDetailData.actions);
            const actionIdList = data.action_ids || [];
            this.$store.commit('permTemplate/updatePreActionIds', actionIdList);
            this.$store.commit('permTemplate/updateAction', getActionsData(actionIdList, list, this.defaultCheckedActions));
            await addPreUpdateInfo(params);
          } else {
            this.editRequestQueue = ['getPre'];
          }
          this.$router.push({
            name: 'actionsTemplateEdit',
            params: {
              id,
              systemId: system.id
            },
            query: {
              step: flag ? 2 : 1
            }
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.editRequestQueue.shift();
        }
      },

      async handleTemplateDelete ({ id }) {
        try {
          await this.$store.dispatch('permTemplate/deleteTemplate', { id });
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.resetPagination();
          this.isShowDetailSlider = false;
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },
  
      async fetchTemplateList (isLoading = false) {
        this.tableLoading = isLoading;
        const { current, limit } = this.pagination;
        const params = {
          ...this.searchParams,
          limit,
          offset: limit * (current - 1)
        };
        delete params.current;
        try {
          const { code, data } = await this.$store.dispatch('permTemplate/getTemplateList', params);
          this.actionsTempList = [...data.results || []];
          this.pagination = Object.assign(this.pagination, { count: data.count || 0 });
          this.emptyData = formatCodeData(code, this.emptyData, this.actionsTempList.length === 0);
          this.$nextTick(() => {
            const currentSelectList = this.currentSelectList.map((item) => item.id);
            this.actionsTempList.forEach((item) => {
              if (currentSelectList.includes(item.id)) {
                this.$refs.actionsTemplateRef && this.$refs.actionsTemplateRef.toggleRowSelection(item, true);
              }
            });
            if (this.currentSelectList.length < 1) {
              this.$refs.actionsTemplateRef && this.$refs.actionsTemplateRef.clearSelection();
            }
          });
          this.fetchSelectedGroupCount();
        } catch (e) {
          this.actionsTempList = [];
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async fetchTemplateDetail (id) {
        try {
          const { data } = await this.$store.dispatch('permTemplate/getTemplateDetail', { id, grouping: true });
          this.curDetailData = Object.assign(this.curDetailData, data);
          this.handleActionData();
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        const { data } = await this.$store.dispatch('system/getSystems', params);
        return data.map(({ id, name }) => ({ id, name })).filter(item => item.name.indexOf(value) > -1);
      },

      async handleEdit (payload) {
        this.editRequestQueue = ['getPre', 'addPre'];
        this.curDetailData = Object.assign(this.curDetailData, payload);
        await this.fetchTemplateDetail(payload.id);
        await this.getPreUpdateInfo();
      },

      async handleSubmitDelete () {
        const selectGroups = this.currentSelectList.filter((item) => item.subject_count === 0);
        this.batchQuitLoading = true;
        try {
          for (let i = 0; i < selectGroups.length; i++) {
            await this.$store.dispatch('permTemplate/deleteTemplate', {
              id: selectGroups[i].id
            });
          }
          this.isShowDeleteDialog = false;
          this.currentSelectList = [];
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.resetPagination();
          this.fetchTemplateList(true);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.batchQuitLoading = false;
        }
      },

      handleBatch (payload) {
        const typeMap = {
          delete: () => {
            this.delActionDialogTitle = this.$t(`m.dialog['确认批量删除所选的操作模板吗？']`);
            this.delActionDialogTip = this.$t(`m.actionsTemplate['以下为有关联用户组的操作模板，不可删除。']`);
            this.hasRelatedGroups = this.currentSelectList.filter((item) => item.subject_count > 0);
            this.isShowDeleteDialog = true;
          }
        };
        return typeMap[payload]();
      },

      handleCreate () {
        this.$router.push({
          name: 'actionsTemplateCreate'
        });
      },
  
      handleRemoteRtx (value) {
        return fuzzyRtxSearch(value)
          .then(data => {
            return data.results;
          });
      },
  
      handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.emptyData.tipType = 'search';
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: 10 });
        if (!result.length) {
          this.resetLocationHref();
          window.localStorage.removeItem('templateList');
        }
        this.resetPagination();
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
            const tableList = cloneDeep(this.actionsTempList);
            const selectGroups = this.currentSelectList.filter((item) => !tableList.map((v) => v.id).includes(item.id));
            this.currentSelectList = [...selectGroups, ...payload];
            this.fetchSelectedGroupCount();
          }
        };
        return typeMap[type]();
      },

      fetchSelectedGroupCount () {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.actionsTemplateRef && selectionCount && selectionCount.length && selectionCount[0].children) {
            selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
          }
        });
      },

      handleAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },
  
      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.queryParams = Object.assign(this.queryParams, { current: page });
        this.fetchTemplateList(true);
      },
  
      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit });
        this.fetchTemplateList(true);
      },
  
      handleView (payload, tabActive) {
        this.$store.commit('permTemplate/updateCloneActions', []);
        this.$store.commit('permTemplate/updateAction', []);
        this.$store.commit('permTemplate/updatePreActionIds', []);
        this.curDetailData = Object.assign(payload, {
          tabActive
        });
        this.isShowDetailSlider = true;
      },
      
      handleActionData () {
        // 获取actions和sub_groups所有数据，并根据单双行渲染不同背景颜色
        let colorIndex = 0;
        this.curDetailData.actions.forEach((item) => {
          this.$set(item, 'expanded', true);
          let count = 0;
          let allCount = 0;
          let deleteCount = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          if (!item.sub_groups) {
            this.$set(item, 'sub_groups', []);
          }
          if (item.actions.length === 1 || !item.sub_groups.length) {
            this.$set(item, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
          }
          item.actions.forEach((act) => {
            this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
            this.$set(act, 'disabled', act.tag === 'readonly');
            if (item.actions.length > 1 && item.sub_groups.length > 0) {
              this.$set(act, 'bgColor', colorIndex % 2 === 0 ? '#ffffff' : '#f7f9fc');
              colorIndex++;
            }
            if (act.checked) {
              ++count;
              this.defaultCheckedActions.push(act.id);
            }
            if (act.tag === 'delete') {
              ++deleteCount;
            }
            ++allCount;
          });
          item.sub_groups.forEach((sub) => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            this.$set(sub, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions.forEach((act) => {
              this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
              this.$set(act, 'disabled', act.tag === 'readonly');
              if (act.checked) {
                ++count;
                this.defaultCheckedActions.push(act.id);
              }
              if (act.tag === 'delete') {
                ++deleteCount;
              }
              ++allCount;
            });
            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });
          this.$set(item, 'deleteCount', deleteCount);
          this.$set(item, 'count', count);
          this.$set(item, 'allCount', allCount);
          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
          if (item.sub_groups && item.sub_groups.length > 0) {
            this.$set(item, 'actionsAllChecked', isAllChecked && item.sub_groups.every(v => v.allChecked));
            this.$set(item, 'actionsAllDisabled', isAllDisabled && item.sub_groups.every(v => {
              return v.actions.every(sub => sub.disabled);
            }));
          } else {
            this.$set(item, 'actionsAllChecked', isAllChecked);
            this.$set(item, 'actionsAllDisabled', isAllDisabled);
          }
        });
      },

      updateSliderOperateData () {
        this.$once('hook:beforeDestroy', () => {
          bus.$off('on-info-change');
          bus.$off('on-related-group-change');
        });
        bus.$on('on-info-change', (payload) => {
          const { id, name, description } = payload;
          const index = this.actionsTempList.findIndex((item) => item.id === id);
          if (index > -1) {
            this.actionsTempList[index] = Object.assign(this.actionsTempList[index], {
              name,
              description
            });
          }
        });
        bus.$on('on-related-group-change', (payload) => {
          const { id, subject_count } = payload;
          const index = this.actionsTempList.findIndex((item) => item.id === id);
          console.log(index);
          if (index > -1) {
            this.actionsTempList[index] = Object.assign(this.actionsTempList[index], {
              subject_count
            });
          }
        });
      },
      
      handleAfterDeleteLeave () {
        this.currentActionName = '';
        this.hasRelatedGroups = [];
      },

      handleCancelDelete () {
        this.isShowDeleteDialog = false;
      },
  
      resetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
        this.fetchTemplateList(true);
      },
        
      resetLocationHref () {
        const urlFields = [...this.searchData.map(item => item.id), ...['current', 'limit']];
        delLocationHref(urlFields);
      },

      getDefaultSelect () {
        return this.actionsTempList.length > 0;
      },
  
      handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.queryParams = Object.assign({}, { current: 1, limit: 10 });
        this.resetPagination();
      },
  
      handleEmptyRefresh () {
        this.queryParams = Object.assign({}, { current: 1, limit: 10 });
        this.resetPagination();
      }
    }
  };
</script>

<style lang="postcss">
.actions-template-delete-confirm {
  padding: 16px;
  .popconfirm-content {
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
  .popconfirm-operate {
    .default-operate-button {
      margin-right: 8px;
      min-width: 64px !important;
      &:not(&:last-child) {
        margin-right: 8px;
      }
    }
  }
}
</style>

<style lang="postcss" scoped>
.iam-actions-template-wrapper {
  .form-operate-btn {
    font-size: 0;
    .bk-button {
      &:not(&:last-child) {
        margin-right: 8px;
      }
    }
  }
  .actions-template-table {
    margin-top: 16px;
    border-right: none;
    border-bottom: none;
    &.set-border {
      border-right: 1px solid #dfe0e5;
      border-bottom: 1px solid #dfe0e5;
    }
    .actions-template-name {
      display: flex;
      align-items: center;
      .name {
        color: #3a84ff;
        word-break: break-all;
        &:hover {
          color: #699df4;
          cursor: pointer;
        }
        &.is-lock {
          max-width: calc(100% - 68px);
        }
      }
    }
    .lock-status {
      font-size: 12px;
      color: #fe9c00;
    }
    .table-operate-btn {
      &:not(&:last-child) {
        margin-right: 16px;
      }
    }
  }
}
</style>

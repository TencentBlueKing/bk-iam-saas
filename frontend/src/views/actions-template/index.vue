<template>
  <div class="iam-actions-template-wrapper">
    <render-search>
      <bk-button theme="primary" @click="handleCreate">
        {{ $t(`m.common['新建']`) }}
      </bk-button>
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
      size="small"
      ext-cls="actions-template-table"
      :class="{ 'set-border': tableLoading }"
      :data="actionsTempList"
      :max-height="tableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column :label="$t(`m.actionsTemplate['模板名称']`)" :min-width="220" fixed="left">
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
      <bk-table-column :label="$t(`m.common['操作-table']`)" :min-width="100" fixed="right">
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
  
    <user-group-dialog
      :show.sync="isShowUserGroupDialog"
      :name="curTemplateName"
      :template-id="curTemplateId"
      :loading="addGroupLoading"
      @on-cancel="handleCancelSelect"
      @on-sumbit="handleSubmitSelectUserGroup"
    />

    <ActionsTemplateDetailSlider :show.sync="isShowDetailSlider" :cur-detail-data="curDetailData" />
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { bus } from '@/common/bus';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, getWindowHeight, delLocationHref } from '@/common/util';
  import { addPreUpdateInfo, getActionsData } from '@/views/actions-template/common/actions';
  import UserGroupDialog from '@/components/render-user-group-dialog';
  import IamSearchSelect from '@/components/iam-search-select';
  import ActionsTemplateDetailSlider from './components/actions-template-detail-slider.vue';
  export default {
    name: '',
    components: {
      UserGroupDialog,
      IamSearchSelect,
      ActionsTemplateDetailSlider
    },
    data () {
      return {
        actionsTempList: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
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
        searchParams: {},
        curDetailData: {},
        editLoading: false,
        isShowUserGroupDialog: false,
        isShowDetailSlider: false,
        curTemplateName: '',
        curTemplateId: '',
        addGroupLoading: false,
        spaceFiltersList: [],
        editRequestQueue: [],
        defaultCheckedActions: [],
        curRole: 'staff',
        queryParams: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        tableHeight: getWindowHeight() - 185
      };
    },
    computed: {
        ...mapGetters(['user', 'externalSystemId']),
        isCanBatchDelete () {
            return this.currentSelectList.length > 0;
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
      this.getQueryParamsData();
    },
    mounted () {
      this.updateSliderOperateData();
    },
    methods: {
      async fetchPageData () {
        await this.fetchTemplateList();
      },
      
      async getQueryParamsData () {
        this.searchParams = this.$route.query;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const isObject = (payload) => {
          return Object.prototype.toString.call(payload) === '[object Object]';
        };
        const currentQueryCache = await this.getCurrentQueryCache();
        if (currentQueryCache && Object.keys(currentQueryCache).length) {
          if (currentQueryCache.limit) {
            this.pagination = Object.assign(
              this.pagination,
              {
                current: Number(currentQueryCache.current),
                limit: Number(currentQueryCache.limit)
              }
            );
          }
          for (const key in currentQueryCache) {
            if (!['current', 'limit'].includes(key)) {
              const curData = currentQueryCache[key];
              const tempData = this.searchData.find(item => item.id === key);
              if (isObject(curData)) {
                if (tempData) {
                  this.searchValue.push({
                    id: key,
                    name: tempData.name,
                    values: [curData]
                  });
                  this.searchList.push(...cloneDeep(this.searchValue));
                  this.searchParams[key] = curData.id;
                }
              } else if (tempData) {
                this.searchValue.push({
                  id: key,
                  name: tempData.name,
                  values: [{
                    id: curData,
                    name: curData
                  }]
                });
                this.searchList.push(...cloneDeep(this.searchValue));
                this.searchParams[key] = curData;
              } else {
                this.searchParams[key] = curData;
              }
            }
          }
        }
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
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },
  
      async fetchTemplateList (isLoading = false) {
        this.tableLoading = isLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
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
  
      async handleSubmitSelectUserGroup (payload) {
        const params = {
          expired_at: 0,
          members: payload,
          id: this.curTemplateId
        };
        this.addGroupLoading = true;
        try {
          await this.$store.dispatch('permTemplate/addTemplateMember', params);
          this.messageSuccess(this.$t(`m.info['关联用户组成功']`), 3000);
          this.handleCancelSelect();
          this.fetchTemplateList(true);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.addGroupLoading = false;
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

      handleCreate () {
        this.$router.push({
          name: 'actionsTemplateCreate'
        });
      },
  
      handleCancelSelect () {
        this.curTemplateId = '';
        this.curTemplateName = '';
        this.isShowUserGroupDialog = false;
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
      },
       
      refreshCurrentQuery () {
        const params = {};
        const queryParams = {
            ...this.searchParams,
            ...this.queryParams
        };
        if (Object.keys(queryParams).length) {
          window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        }
        for (const key in this.searchParams) {
          const tempObj = this.searchData.find(item => key === item.id);
          if (tempObj && tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
            if (this.searchList.length > 0) {
              const tempData = this.searchList.find(item => item.id === key);
              params[key] = tempData.values[0];
            }
          } else {
            params[key] = this.searchParams[key];
          }
        }
        this.emptyData = Object.assign(this.emptyData, { tipType: Object.keys(this.searchParams).length > 0 ? 'search' : '' });
        this.pagination = Object.assign(
          this.pagination,
          {
            current: queryParams.current || 1,
            limit: queryParams.limit || 10
          }
        );
        return {
          ...queryParams
        };
      },
  
      setCurrentQueryCache (payload) {
        window.localStorage.setItem('templateList', JSON.stringify(payload));
      },
  
      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('templateList'));
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
          margin-right: 8px;
      }
    }
  }
}
</style>

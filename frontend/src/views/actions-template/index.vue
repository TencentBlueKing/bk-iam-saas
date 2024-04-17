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
                'name',
                { 'single-hide is-lock': row.is_lock }
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
          <span :title="row.description">{{ row.description || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" :min-width="100" fixed="right">
        <template slot-scope="{ row }">
          <span>
            <bk-button theme="primary" text class="table-operate-btn"> {{ $t(`m.common['编辑']`) }}</bk-button>
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
  
      handleCreate () {
        this.$router.push({
          name: 'permTemplateCreate'
        });
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
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.addGroupLoading = false;
        }
      },
  
      handleCancelSelect () {
        this.curTemplateId = '';
        this.curTemplateName = '';
        this.isShowUserGroupDialog = false;
      },
  
      handleBatchDelete () {
        const hasSelectedLen = this.currentSelectList.length;
        let deleteTitle = '';
        if (hasSelectedLen === 1) {
          deleteTitle = `${this.$t(`m.dialog['确认删除']`)}`;
        } else {
          deleteTitle = `${this.$t(`m.common['确认删除']`)}${hasSelectedLen}${this.$t(`m.permTemplate['个模板']`)}？`;
        }
        this.$bkInfo({
          title: deleteTitle,
          subTitle: this.$t(`m.permTemplate['删除权限模版不会影响已授权用户，可以放心删除。']`),
          maskClose: true,
          confirmFn: async () => {
            console.warn('');
          }
        });
      },
  
      handleRemoteRtx (value) {
        return fuzzyRtxSearch(value)
          .then(data => {
            return data.results;
          });
      },
  
      handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        return this.$store.dispatch('system/getSystems', params)
          .then(({ data }) => {
            return data.map(({ id, name }) => ({ id, name })).filter(item => item.name.indexOf(value) > -1);
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
        // this.$router.push({
        //   name: 'permTemplateDetail',
        //   params: {
        //     id: payload.id,
        //     systemId: payload.system.id
        //   },
        //   query: {
        //     tab
        //   }
        // });
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

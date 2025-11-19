<template>
  <div class="iam-perm-template-wrapper">
    <render-search>
      <iam-guide
        type="create_perm_template"
        direction="left"
        :cur-style="{ top: curLanguageIsCn ? '-20px' : '-32px', left: '80px' }"
        :content="$t(`m.guide['创建模板']`)"
      />
      <bk-button theme="primary" @click="handleCreate" data-test-id="permTemplate_btn_create">
        {{ $t(`m.common['新建']`) }}
      </bk-button>
      <!-- <bk-button style="margin-left: 10px;" :disabled="!isCanBatchDelete" @click="handleBatchDelete">
                    批量删除
                </bk-button> -->
      <div slot="right">
        <iam-search-select
          style="width: 420px"
          :data="searchData"
          :value="searchValue"
          :quick-search-method="quickSearchMethod"
          @on-change="handleSearch"
        />
      </div>
    </render-search>

    <bk-table
      size="small"
      ext-cls="perm-template-table"
      :class="{ 'set-border': tableLoading }"
      :data="tableList"
      :max-height="tableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <!-- <bk-table-column type="selection" align="center"></bk-table-column> -->
      <bk-table-column :label="$t(`m.permTemplate['模板名']`)" width="220">
        <template slot-scope="{ row }">
          <span class="perm-template-name" :title="row.name" @click="handleView(row, 'TemplateDetail')">
            {{ row.name }}
          </span>
          <!-- <span class="lock-status" v-if="row.is_lock">{{ $t(`m.permTemplate['编辑中']`) }}</span> -->
          <bk-tag theme="warning" v-if="row.is_lock">{{ $t(`m.permTemplate['编辑中']`) }}</bk-tag>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['所属系统']`)">
        <template slot-scope="{ row }">
          <span :title="row.system.name">{{ row.system.name }}</span>
        </template>
      </bk-table-column>
      <!-- <template v-if="['rating_manager'].includes(curRole)">
                <bk-table-column
                    :label="$t(`m.nav['管理空间']`)"
                >
                    <template slot-scope="{ row }">
                        <span class="user-group-name" :title="row.role.name" @click="handleView(row)">
                            {{ row.role.name || '--' }}
                        </span>
                        <span>{{ user.role && user.role.name === row.role.name
                            ? `(${il8n('levelSpace', '当前空间')})` : '' }}</span>
                    </template>
                </bk-table-column>
            </template> -->
      <bk-table-column :label="$t(`m.permTemplate['关联的组']`)">
        <template slot-scope="{ row }">
          <template v-if="!!row.subject_count">
            <bk-button text theme="primary" @click="handleView(row, 'AttachGroup')">
              {{ row.subject_count }}
            </bk-button>
          </template>
          <template v-else> -- </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.permTemplate['创建人']`)" prop="creator"></bk-table-column>
      <bk-table-column :label="$t(`m.common['创建时间']`)" width="240">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)" width="300">
        <template slot-scope="{ row }">
          <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" width="100">
        <template slot-scope="{ row }">
          <section>
            <!-- <bk-button
                            theme="primary"
                            text
                            @click="handleRelateGroup(row)">
                            {{ $t(`m.permTemplate['关联用户组']`) }}
                        </bk-button> -->
            <bk-button theme="primary" text v-if="row.subject_count < 1" @click="handleTemplateDelete(row)">
              {{ $t(`m.common['删除']`) }}
            </bk-button>
            <!-- <bk-button theme="primary" disabled text v-else>
              <span :title="$t(`m.info['有关联的用户组, 无法删除']`)">
                {{ $t(`m.common['删除']`) }}
              </span>
            </bk-button> -->
            <bk-popover
              v-else
              :content="$t(`m.info['有关联的用户组, 无法删除']`)"
            >
              <bk-button
                theme="primary"
                :disabled="true"
                :text="true"
              >
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </bk-popover></section>
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
      :template-id="curTempalteId"
      :loading="addGroupLoading"
      @on-cancel="handleCancelSelect"
      @on-sumbit="handleSubmitSelectUserGroup"
    />
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import UserGroupDialog from '@/components/render-user-group-dialog';
  import IamSearchSelect from '@/components/iam-search-select';
  import IamGuide from '@/components/iam-guide/index.vue';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, getWindowHeight, delLocationHref } from '@/common/util';
  export default {
    name: '',
    components: {
      UserGroupDialog,
      IamSearchSelect,
      IamGuide
    },
    data () {
      return {
        tableList: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        searchParams: {},
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.permTemplate['模板名']`),
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
        currentSelectList: [],
        currentPermTemplate: {},
        editLoading: false,
        isShowUserGroupDialog: false,
        curTemplateName: '',
        curTempalteId: '',
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
            isRatingManager () {
                return this.curRole === 'rating_manager';
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
          if (key !== 'limit' && key !== 'current') {
            const curData = currentQueryCache[key];
            const tempData = this.searchData.find(item => item.id === key);
            if (isObject(curData)) {
              if (tempData) {
                this.searchValue.push({
                  id: key,
                  name: tempData.name,
                  values: [curData]
                });
                this.searchList.push(..._.cloneDeep(this.searchValue));
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
              this.searchList.push(..._.cloneDeep(this.searchValue));
              this.searchParams[key] = curData;
            } else {
              this.searchParams[key] = curData;
            }
          }
        }
      }
    },
    methods: {
      async fetchPageData () {
        await this.fetchTemplateList();
      },

      refreshCurrentQuery () {
        const params = {};
        const queryParams = {
          ...this.searchParams,
          ...this.queryParams
        };
        if (Object.keys(queryParams).length) {
          window.history.replaceState({}, '', `?${buildURLParams({
            ...queryParams,
             role_name: this.user.role.name
          })}`);
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
          { current: queryParams.current || 1, limit: queryParams.limit || 10 }
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

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },
      
      resetLocationHref () {
        const urlFields = [...this.searchData.map(item => item.id), ...['current', 'limit']];
        delLocationHref(urlFields);
      },

      async handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.queryParams = Object.assign({}, { current: 1, limit: 10 });
        this.resetPagination();
        await this.fetchTemplateList(true);
      },

      async handleEmptyRefresh () {
        this.queryParams = Object.assign({}, { current: 1, limit: 10 });
        this.resetPagination();
        await this.fetchTemplateList(true);
      },

      handleTemplateDelete ({ id }) {
        this.$bkInfo({
          title: this.$t(`m.dialog['确认删除']`),
          confirmLoading: true,
          confirmFn: async () => {
            try {
              await this.$store.dispatch('permTemplate/deleteTemplate', { id });
              this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
              this.resetPagination();
              this.fetchTemplateList(true);
              return true;
            } catch (e) {
              console.warn(e);
              return false;
            }
          }
        });
      },

      async fetchTemplateList (isLoading = false) {
        this.tableLoading = isLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const params = {
            ...this.searchParams,
            limit: this.pagination.limit,
            offset: this.pagination.limit * (this.pagination.current - 1)
        };
        delete params.current;
        try {
          const { code, data } = await this.$store.dispatch('permTemplate/getTemplateList', params);
          this.pagination = Object.assign(this.pagination, { count: data.count || 0 });
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.$store.commit('setGuideShowByField', { field: 'template', flag: !this.tableList.length > 0 });
          this.$store.commit('setGuideShowByField', { field: 'group', flag: this.tableList.length > 0 });
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          this.tableList = [];
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
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
          id: this.curTempalteId
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
        this.curTempalteId = '';
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
        this.resetPagination();
        if (!result.length) {
          this.resetLocationHref();
          window.localStorage.removeItem('templateList');
        }
        this.fetchTemplateList(true);
      },

      handleRelateGroup (payload) {
        this.curTempalteId = payload.id;
        this.curTemplateName = payload.name;
        this.isShowUserGroupDialog = true;
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.queryParams = Object.assign(this.queryParams, { current: page });
        this.fetchTemplateList(true);
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: currentLimit });
        this.fetchTemplateList(true);
      },

      handlerAllChange (selection) {
        this.currentSelectList = [...selection];
      },

      handlerChange (selection, row) {
        this.currentSelectList = [...selection];
      },

      handleView (payload, tab) {
        this.$store.commit('permTemplate/updateCloneActions', []);
        this.$store.commit('permTemplate/updateAction', []);
        this.$store.commit('permTemplate/updatePreActionIds', []);
        window.localStorage.setItem('iam-header-title-cache', payload.name);
        window.localStorage.setItem('iam-header-name-cache', payload.name);
        this.$router.push({
          name: 'permTemplateDetail',
          params: {
            id: payload.id,
            systemId: payload.system.id
          },
          query: {
            tab
          }
        });
      }
    }
  };
</script>
<style lang="postcss">
.iam-perm-template-wrapper {
  .perm-template-table {
    margin-top: 16px;
    border-right: none;
    border-bottom: none;
    &.set-border {
      border-right: 1px solid #dfe0e5;
      border-bottom: 1px solid #dfe0e5;
    }
    .perm-template-name {
      color: #3a84ff;
      cursor: pointer;
      &:hover {
        color: #699df4;
      }
    }
    .lock-status {
      font-size: 12px;
      color: #fe9c00;
    }
  }
}
</style>

<style lang="postcss" scoped>
    /deep/ .bk-table-pagination-wrapper {
        background: #fff;
    }
</style>

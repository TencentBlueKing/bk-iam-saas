<template>
  <div class="iam-level-manage-space-wrapper">
    <render-search>
      <bk-button theme="primary" @click="handleCreate" data-test-id="level-manage_space_btn_create">
        {{ isStaff ? $t(`m.common['申请新建']`) : $t(`m.common['新建']`) }}
      </bk-button>
      <div slot="right">
        <bk-input :placeholder="$t(`m.levelSpace['搜索空间名、描述、创建人']`)" :clearable="true" style="width: 420px"
          right-icon="bk-icon icon-search" v-model="searchValue" @enter="handleSearch" @clear="handleClear">
        </bk-input>
      </div>
    </render-search>
    <bk-table size="small" :max-height="tableHeight" :data="tableList" :class="{ 'set-border': tableLoading }"
      ext-cls="level-manage-table" :pagination="pagination" @page-change="handlePageChange"
      @page-limit-change="handleLimitChange" v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <bk-table-column :label="$t(`m.levelSpace['名称']`)">
        <template slot-scope="{ row }">
          <span class="level-manage-name" :title="row.name" @click="handleNavAuthBoundary(row)">
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)">
        <template slot-scope="{ row }">
          <span :title="row.description">{{ row.description || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.levelSpace['创建人']`)" prop="creator"></bk-table-column>
      <bk-table-column :label="$t(`m.common['创建时间']`)" width="240">>
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.grading['更新人']`)" prop="updater"></bk-table-column>
      <bk-table-column :label="$t(`m.grading['更新时间']`)">
        <template slot-scope="{ row }">
          <span :title="row.updated_time">{{ row.updated_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)" width="150" fixed="right">
        <template slot-scope="{ row }">
          <section>
            <bk-button theme="primary" text @click="handleClone(row)">
              {{ $t(`m.levelSpace['克隆']`) }}
            </bk-button>
          </section>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { getWindowHeight } from '@/common/util';
  export default {
    name: 'firstManageSpace',
    data () {
      return {
        searchValue: '',
        isFilter: false,
        tableList: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        tableLoading: false,
        confirmLoading: false,
        confirmDialogTitle: '',
        confirmDialogSubTitle: '',
        isShowConfirmDialog: false,
        curOperateType: '',
        curId: -1,
        isShowApplyDialog: false,
        applyLoading: false,
        curName: '',
        showImageDialog: false,
        noFooter: false
      };
    },
    computed: {
            ...mapGetters(['user']),
            isStaff () {
                return this.user.role.type === 'staff';
            },
            tableHeight () {
                return getWindowHeight() - 185;
            }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
        if (currentQueryCache.name) {
          this.searchValue = currentQueryCache.name;
        }
        if (this.searchValue !== '') {
          this.isFilter = true;
        }
      }
    },
    methods: {
      async fetchGradingAdmin (isTableLoading = false) {
        this.tableLoading = isTableLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const { current, limit } = this.pagination;
        try {
          const res = await this.$store.dispatch('role/getRatingManagerList', {
            limit,
            offset: (current - 1) * limit,
            name: this.searchValue
          });
          this.pagination.count = res.data.count;
          this.tableList.splice(0, this.tableList.length, ...(res.data.results || []));
          if (this.isStaff) {
            this.$store.commit('setGuideShowByField', { field: 'role', flag: this.tableList.length > 0 });
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async fetchPageData () {
        await this.fetchGradingAdmin();
      },

      handleCreate () {
        this.$router.push({
          name: 'firstManageSpaceCreate',
          params: {
            id: 0
          }
        });
      },

      handleClone (value) {
        this.$router.push({
          name: 'firstManageSpaceCreate',
          params: {
            id: value.id
          }
        });
      },

      handleNavAuthBoundary (payload) {
        window.localStorage.setItem('iam-header-name-cache', payload.name);
        this.$store.commit('updateIndex', 1);
        this.$router.push({
          name: 'authorBoundary',
          params: {
            id: payload.id,
            type: 'first'
          }
        });
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const queryParams = {
          limit,
          current
        };
        if (this.searchValue) {
          queryParams.name = this.searchValue;
        }
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        return queryParams;
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('firstLevelPager'));
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('firstLevelPager', JSON.stringify(payload));
      },

      handleSearch () {
        if (!this.searchValue) {
          return;
        }
        this.isFilter = true;
        this.resetPagination();
        this.fetchGradingAdmin(true);
      },

      handleClear () {
        if (this.isFilter) {
          this.isFilter = false;
          this.resetPagination();
          this.fetchGradingAdmin(true);
        }
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchGradingAdmin(true);
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { limit, current: 1 });
        this.fetchGradingAdmin(true);
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          current: 1,
          count: 0,
          limit: 10
        });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-level-manage-space-wrapper {
    .level-manage-table {
        margin-top: 16px;
        border-right: none;
        border-bottom: none;

        &.set-border {
            border-right: 1px solid #dfe0e5;
            border-bottom: 1px solid #dfe0e5;
        }

        .level-manage-name {
            color: #3a84ff;
            cursor: pointer;

            &:hover {
                color: #699df4;
            }
        }

        /deep/ .bk-table-pagination-wrapper {
            background: #fff;
        }
    }
}
</style>

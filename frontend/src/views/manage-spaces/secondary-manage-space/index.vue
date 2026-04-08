<template>
  <div class="iam-level-manage-space-wrapper">
    <render-search>
      <bk-button
        theme="primary"
        @click="handleView({ id: 0 }, 'create')" data-test-id="level-manage_space_btn_create">
        {{ isStaff ? $t(`m.common['申请新建']`) : $t(`m.common['新建']`) }}
      </bk-button>
      <div slot="right">
        <bk-input
          :placeholder="$t(`m.levelSpace['请输入名称']`)"
          clearable
          style="width: 420px;"
          right-icon="bk-icon icon-search"
          v-model="searchValue"
          @enter="handleSearch">
        </bk-input>
      </div>
    </render-search>
    <bk-table size="small" :max-height="tableHeight" :data="tableList" :class="{ 'set-border': tableLoading }"
      ext-cls="level-manage-table" :pagination="pagination" @page-change="handlePageChange"
      @page-limit-change="handleLimitChange" v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <bk-table-column :label="$t(`m.levelSpace['名称']`)">
        <template slot-scope="{ row }">
          <span class="level-manage-name" :title="row.name" @click="handleView(row, 'detail')">
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.levelSpace['管理员']`)" prop="members" width="300">
        <template slot-scope="{ row, $index }">
          <template v-if="row.isEdit || row.members.length > 0">
            <IamEditMemberSelector
              field="members"
              width="200"
              :ref="`managerRef${$index}`"
              :placeholder="$t(`m.verify['请输入']`)"
              :allow-empty="true"
              :is-edit-allow-empty="false"
              :value="row.members"
              :index="$index"
              @on-change="handleUpdateMembers"
              @on-empty-change="handleEmptyMemberChange(...arguments, row)"
            />
          </template>
          <template v-else>
            <IamManagerEditInput
              field="members"
              style="width: 100%;"
              :is-show-other="true"
              :placeholder="$t(`m.verify['请输入']`)"
              :value="getMemberFilter(row.members)"
              @handleShow="handleOpenManagerEdit(row, $index)"
            />
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)">
        <template slot-scope="{ row }">
          <span :title="row.description">{{ row.description || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.grading['更新人']`)" prop="updater">
        <template slot-scope="{ row }">
          <IamUserDisplayName :user-id="row.updater" />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.grading['更新时间']`)" width="240">
        <template slot-scope="{ row }">
          <span :title="row.updated_time">{{ row.updated_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" width="120">
        <template slot-scope="{ row }">
          <section>
            <bk-button
              theme="primary"
              text
              @click="handleView(row, 'role')"
            >
              {{ $t(`m.levelSpace['进入空间']`) }}
            </bk-button>
            <bk-button
              theme="primary"
              text
              style="margin-left: 10px;"
              @click="handleView(row, 'clone')"
            >
              {{ $t(`m.levelSpace['克隆']`) }}
            </bk-button>
          </section>
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
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import IamManagerEditInput from '@/components/iam-edit/input';

  export default {
    name: 'secondaryManageSpace',
    components: {
      IamEditMemberSelector,
      IamManagerEditInput
    },
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
        noFooter: false,
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
            ...mapGetters(['user']),
            isStaff () {
                return this.user.role.type === 'staff';
            },
            disabledPerm () {
                return (payload) => {
                    const result = payload.members.map(item => item.username).includes(this.user.username);
                    return !result;
                };
            }
    },
    watch: {
      searchValue (newVal, oldVal) {
        if (!newVal && oldVal && this.isFilter) {
          this.isFilter = false;
          this.resetPagination();
          this.fetchGradingAdmin(true);
        }
      },
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 185;
      });
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
          const { code, data } = await this.$store.dispatch('spaceManage/getSecondManager', {
            limit,
            offset: (current - 1) * limit,
            name: this.searchValue
          });
          this.pagination.count = data.count;
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          if (this.isStaff) {
            this.$store.commit('setGuideShowByField', { field: 'role', flag: this.tableList.length > 0 });
          }
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.tableList = [];
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async fetchPageData () {
        await this.fetchGradingAdmin();
      },

      async handleUpdateMembers (payload, index, role) {
        const { name, description, members } = payload;
        const params = {
          name: name || role.name,
          description: description || role.description,
          members: members || role.members,
          id: role.id
        };
        await this.$store.dispatch('spaceManage/updateSecondManager', params);
        this.resetPagination();
        this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
        await this.fetchGradingAdmin(true);
      },

      getMemberFilter (value) {
        if (value.length) {
          return Array.isArray(value) ? value.map(item => item.username).join(';') : value;
        }
        return '--';
      },

      handleOpenManagerEdit (payload, index) {
        this.$set(this.tableList[index], 'isEdit', true);
        this.$nextTick(() => {
          const managerRef = this.$refs[`managerRef${index}`];
          if (managerRef) {
            managerRef.isEditable = true;
            if (!payload.members.length) {
              setTimeout(() => {
                managerRef.$refs.selector.$el.querySelector('input').focus();
              }, 10);
            }
          }
        });
      },

      handleEmptyMemberChange (index, row) {
        row.isEdit = false;
      },

      handleNavAuthBoundary (payload) {
        window.localStorage.setItem('iam-header-name-cache', payload.name);
        this.$store.commit('updateIndex', 1);
        this.$router.push({
          name: 'secondaryManageSpaceDetail',
          params: {
            id: payload.id
          }
        });
      },
            
      async handleView ({ id, name }, type) {
        const navRoute = {
          detail: () => {
            window.localStorage.setItem('iam-header-name-cache', name);
            this.$store.commit('updateIndex', 1);
            this.$router.push({
              name: 'secondaryManageSpaceDetail',
              params: {
                id
              }
            });
          },
          role: async () => {
            await this.$store.dispatch('role/updateCurrentRole', { id });
            await this.$store.dispatch('userInfo');
            const { role } = this.user;
            if (role) {
              this.$store.commit('updateCurRoleId', id);
              this.$store.commit('updateIdentity', { id, type: role.type, name });
              this.$store.commit('updateNavId', id);
              this.$store.commit('updateIndex', 1);
              window.localStorage.setItem('index', 1);
              this.$router.push({
                name: 'userGroup',
                params: {
                  id,
                  entry: 'all_manager'
                }
              });
            }
          },
          create: () => {
            this.$router.push({
              name: 'secondaryManageSpaceCreate'
            });
          },
          clone: () => {
            this.$router.push({
              name: 'secondaryManageSpaceClone',
              params: {
                id
              }
            });
          }
        };
        navRoute[type]();
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const queryParams = {
          limit,
          current
        };
        if (this.searchValue) {
          this.emptyData.tipType = 'search';
          queryParams.name = this.searchValue;
        }
        window.history.replaceState({}, '', `?${buildURLParams({
          ...queryParams,
           role_name: this.user.role.name
        })}`);
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
        this.emptyData.tipType = 'search';
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

      handleEmptyClear () {
        this.isFilter = false;
        this.searchValue = '';
        this.emptyData.tipType = '';
        this.resetPagination();
        this.fetchGradingAdmin(true);
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.fetchGradingAdmin(true);
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

<style lang="postcss">
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

        .bk-table-pagination-wrapper {
            background: #fff;
        }
    }
}
</style>

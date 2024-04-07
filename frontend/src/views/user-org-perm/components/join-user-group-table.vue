<template>
  <div ref="selectTableRef" class="user-org-table-slider">
    <div class="joined-user-group-wrapper">
      <div class="joined-user-group-left">
        <div class="search-wrapper">
          <iam-search-select
            ref="searchSelectRef"
            :data="searchData"
            :value="searchValue"
            :placeholder="$t(`m.userOrOrg['搜索用户组名、描述']`)"
            @on-input="handleSearchInput"
            @on-change="handleSearch"
            @on-click-menu="handleClickMenu"
          />
        </div>
        <bk-table
          ref="groupTableRef"
          size="small"
          ext-cls="group-table"
          :outer-border="false"
          :header-border="false"
          :class="{ 'set-border': tableLoading }"
          :data="tableList"
          :max-height="pagination.count > 0 ? 527 : 280"
          :cell-attributes="handleCellAttributes"
          :pagination="pagination"
          @page-change="handlePageChange"
          @page-limit-change="handleLimitChange"
          @select="handleSelectedChange"
          @select-all="handleSelectedAllChange"
          v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
        >
          <bk-table-column type="selection" align="center" :selectable="setDefaultSelect" />
          <bk-table-column :label="$t(`m.userGroup['用户组名']`)" :width="300">
            <template slot-scope="{ row }">
              <span
                :class="[
                  'user-group-name-label'
                ]"
                v-bk-tooltips="{
                  content: row.name,
                  placements: ['right-start']
                }"
                @click="handleNavGroup(row)"
              >
                {{ row.name }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.common['描述']`)">
            <template slot-scope="{ row }">
              <span
                v-bk-tooltips="{
                  content: row.description,
                  placements: ['right'],
                  disabled: !row.description
                }"
              >
                {{ row.description || '--' }}
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
      </div>
      <div class="joined-user-group-right">
        <div class="result-preview">
          <div>{{ $t(`m.common['结果预览']`) }}</div>
        </div>
        <div class="has-selected" v-if="!isSelectedEmpty">
          <div class="has-selected-title">
            <span>{{ $t(`m.common['已选择']`) }}</span>
            <span class="count">{{ currentSelectedGroups.length }}</span>
            <span>{{ $t(`m.common['个用户组#']`) }}</span>
          </div>
          <bk-button
            size="small"
            theme="primary"
            text
            class="has-selected-clear"
            @click="handleClearGroups"
          >
            {{ $t(`m.common['清空']`) }}
          </bk-button>
        </div>
        <div class="content" v-if="!isSelectedEmpty">
          <div class="selected-group-content">
            <div class="selected-group-item" v-for="item in currentSelectedGroups" :key="item.id">
              <div class="selected-group-item-left">
                <span
                  :class="[
                    'single-hide',
                    'selected-group-name'
                  ]"
                  :title="item.name"
                >
                  {{ item.name }}
                </span>
              </div>
              <Icon bk type="close" class="delete-depart-icon" @click="handleDelete(item, 'organization')" />
            </div>
          </div>
        </div>
        <div class="selected-empty-wrapper" v-if="isSelectedEmpty">
          <ExceptionEmpty />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData } from '@/common/util';
  import IamSearchSelect from '@/components/iam-search-select';

  export default {
    components: {
      IamSearchSelect
    },
    data () {
      return {
        expiredAt: 15552000,
        expiredAtUse: 15552000,
        tableLoading: false,
        isShowGroupError: false,
        tableList: [],
        currentSelectList: [],
        curUserGroup: [],
        currentSelectedGroups: [],
        defaultSelectedGroups: [],
        searchParams: {},
        searchList: [],
        searchValue: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10,
          type: 'compact',
          showTotalCount: true
        },
        currentBackup: 1,
        curGroupName: '',
        curGroupId: '',
        curSelectMenu: '',
        curInputText: '',
        queryParams: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户组名']`),
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            disabled: true
          }
        ],
        contentWidth: window.innerWidth <= 1440 ? '200px' : '240px'
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isSelectedEmpty () {
        return this.currentSelectedGroups.length < 1;
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    async created () {
      this.fetchDefaultData();
    },
    mounted () {
      window.addEventListener('resize', this.formatFormItemWidth);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
    },
    methods: {
      formatFormItemWidth () {
        this.contentWidth = window.innerWidth <= 1520 ? '200px' : '240px';
      },
      /**
       * 获取页面数据
       */
      async fetchDefaultData () {
        await this.fetchUserGroupList();
      },

      handleEmptyRefresh () {
        this.searchParams = {};
        this.queryParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.resetPagination();
        this.fetchUserGroupList(false);
      },

      handleEmptyClear () {
        this.searchParams = {};
        this.queryParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        if (this.$refs.searchSelectRef && this.$refs.searchSelectRef.$refs.searchSelect) {
          this.$refs.searchSelectRef.$refs.searchSelect.localValue = '';
        }
        this.resetPagination();
        this.fetchUserGroupList(false);
      },

      // 处理手动输入各种场景
      handleManualInput () {
        if (this.curSelectMenu) {
          // 转换为tag标签后,需要清空输入框的值
          if (this.$refs.searchSelectRef && this.$refs.searchSelectRef.$refs.searchSelect) {
            this.$refs.searchSelectRef.$refs.searchSelect.keySubmit();
            this.$refs.searchSelectRef.$refs.searchSelect.localValue = '';
          }
          this.curSelectMenu = '';
          this.curInputText = '';
        } else {
          // 如果当前已有tag，后面如果只输入文字没生成tag自动过滤掉
          if (
            this.searchList.length
            && this.$refs.searchSelectRef
            && this.$refs.searchSelectRef.$refs.searchSelect
            && this.curInputText
          ) {
            this.$refs.searchSelectRef.$refs.searchSelect.localValue = '';
          }
          if (!this.searchList.length) {
            // 处理无tag标签，直接输入内容情况
            this.searchParams.name = this.curInputText;
            if (!this.curInputText) {
              delete this.searchParams.name;
            }
          }
        }
      },

      async handleSearchUserGroup (isClick = false) {
        this.handleManualInput();
        await this.fetchUserGroupList(true);
      },

      async fetchSearchUserGroup (resourceInstances, isTableLoading = true) {
        this.tableLoading = isTableLoading;
        const { current, limit } = this.pagination;
        if (this.searchParams.hasOwnProperty('id')) {
          if (!isNaN(Number(this.searchParams.id))) {
            this.searchParams.id = Number(this.searchParams.id);
          }
        }
        const params = {
          ...this.searchParams,
          limit,
          offset: limit * (current - 1),
          resource_instances: resourceInstances || [],
          apply_disable: false
        };
        try {
          const { code, data } = await this.$store.dispatch('permApply/getJoinGroupSearch', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.tableList.splice(0, this.tableList.length, ...(results || []));
          this.emptyData.tipType = 'search';
          this.emptyData = formatCodeData(code, this.emptyData, count === 0);
          this.formatTableData();
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.tableList = [];
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
          this.curSelectMenu = '';
          this.curInputText = '';
        }
      },

      async fetchUserGroupList (isTableLoading = true) {
        this.tableLoading = isTableLoading;
        const { current, limit } = this.pagination;
        delete this.searchParams.current;
        const params = {
          ...this.searchParams,
          limit,
          offset: limit * (current - 1),
          apply_disable: false
        };
        try {
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupList', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.tableList.splice(0, this.tableList.length, ...(results || []));
          this.emptyData = formatCodeData(code, this.emptyData, count === 0);
          this.formatTableData();
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.tableList = [];
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      formatTableData () {
        this.$nextTick(() => {
          const currentSelectedGroups = this.currentSelectedGroups.length
            ? this.currentSelectedGroups.map((item) => String(item.id))
            : [];
          this.tableList.forEach((item) => {
            if (item.role_members && item.role_members.length) {
              const hasName = item.role_members.some((v) => v.username);
              if (!hasName) {
                item.role_members = item.role_members.map((v) => {
                  return {
                    username: v,
                    readonly: false
                  };
                });
              }
            }
            if (this.defaultSelectedGroups.length) {
              const hasSelected = this.defaultSelectedGroups.find((v) => String(v.id) === String(item.id));
              if (hasSelected) {
                this.$set(item, 'expired_at', hasSelected.expired_at);
                this.$set(item, 'expired_at_display', hasSelected.expired_at_display);
                this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
              }
            }
            const hasSelectedData = [...currentSelectedGroups, ...this.curUserGroup].includes(String(item.id));
            if (hasSelectedData) {
              this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
              this.currentSelectList.push(item);
            }
          });
        });
      },

      handleCellAttributes ({ rowIndex, cellIndex, row, column }) {
        if (cellIndex === 0) {
          if (this.curUserGroup.includes(String(row.id))) {
            return {
              title: this.$t(`m.userOrOrg['已加入该用户组']`)
            };
          }
          return {};
        }
        return {};
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination = Object.assign(this.pagination, { current: page });
        this.queryParams = Object.assign(this.queryParams, { current: page });
        this.handleSearchUserGroup();
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: currentLimit });
        this.handleSearchUserGroup();
      },

      handleClickMenu (payload) {
        const { menu } = payload;
        if (menu.id) {
          this.curSelectMenu = menu.id;
        }
      },

      handleSearchInput (payload) {
        const { text } = payload;
        this.curInputText = text;
      },

      handleSearch (payload, result) {
        this.currentSelectList = [];
        this.searchParams = payload;
        this.searchList = [...result];
        this.curSelectMenu = '';
        this.curInputText = '';
        this.emptyData.tipType = 'search';
        this.resetPagination();
        this.handleSearchUserGroup();
      },

      async handleClearSearch () {
        this.emptyData.tipType = '';
        this.resetPagination();
        this.handleSearchUserGroup();
      },

      handleNavGroup ({ id, name }) {
        this.curGroupName = name;
        this.curGroupId = id;
        const routeData = this.$router.resolve({
          path: `user-group-detail/${id}`,
          query: {
            noFrom: true,
            tab: 'group_perm'
          }
        });
        window.open(routeData.href, '_blank');
      },
      
      fetchSelectedGroups (type, payload, row) {
        this.isShowGroupError = false;
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectedGroups.push(row);
            } else {
              this.currentSelectedGroups = this.currentSelectedGroups.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
            this.$emit('on-selected-group', this.currentSelectedGroups);
          },
          all: () => {
            const list = payload.filter((item) => !this.curUserGroup.includes(item.id.toString()));
            this.currentSelectList = _.cloneDeep(list);
            const tableList = _.cloneDeep(this.tableList);
            const selectGroups = this.currentSelectedGroups.filter(
              (item) => !tableList.map((v) => v.id.toString()).includes(item.id.toString())
            );
            this.currentSelectedGroups = [...selectGroups, ...list];
            this.$emit('on-selected-group', this.currentSelectedGroups);
          }
        };
        return typeMap[type]();
      },

      handleSelectedChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleSelectedAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleClearGroups () {
        this.tableList.forEach((item) => {
          if (!this.curUserGroup.includes(item.id.toString())) {
            this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, false);
          }
        });
        this.currentSelectedGroups = [];
      },

      handleDelete (payload) {
        const index = this.currentSelectedGroups.findIndex((item) => item.id === payload.id);
        const tableIndex = this.tableList.findIndex((item) => item.id === payload.id);
        this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(this.tableList[tableIndex], false);
        this.currentSelectedGroups.splice(index, 1);
      },

      handleBatchRenewal () {
        this.$router.push({
          name: 'permRenewal',
          query: {
            tab: 'group'
          }
        });
      },
      
      setDefaultSelect (payload) {
        return !this.curUserGroup.includes(payload.id.toString());
      },

      resetPagination () {
        this.currentSelectList = [];
        this.pagination = Object.assign(
          this.pagination,
          {
            limit: 10,
            current: 1,
            count: 0
          }
        );
      }
    }
  };
</script>

<style lang="postcss" scoped>
.user-org-table-slider {
  .joined-user-group-wrapper {
    display: flex;
    .joined-user-group-left {
      width: calc(100% - 280px);
      padding: 16px;
      padding-bottom: 0;
      /deep/ .search-wrapper {
        padding-bottom: 12px;
        .search-nextfix {
          top: 0;
        }
      }
      .group-table {
        border: none;
        .user-group-name {
          /* display: flex;
          align-items: center; */
          &-label {
            color: #3a84ff;
            word-break: break-all;
            cursor: pointer;
            &:hover {
              color: #699df4;
            }
            /* &-expired {
              max-width: calc(100% - 150px);
            } */
          }
          &-expired {
            /* line-height: 1; */
            margin-left: 5px;
          }
        }
      }
    }
    .joined-user-group-right {
      width: 280px;
      padding: 0 16px;
      color: #313238;
      background: #F5F7FA;
      position: relative;
      .result-preview {
        display: flex;
        font-size: 14px;
        line-height: 19px;
        padding-top: 16px;
        padding-bottom: 12px;
      }
      .has-selected {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        line-height: 16px;
        &-title {
          .count {
            color: #3a84ff;
            font-weight: 700;
          }
        }
        &-clear {
          padding: 0;
          height: 16px;
          line-height: 16px;
        }
      }

      .content {
        position: relative;
        margin: 12px 0 16px 0;
        max-height: 510px;
        overflow: auto;
        &::-webkit-scrollbar {
          width: 4px;
          background-color: lighten(transparent, 80%);
        }
        &::-webkit-scrollbar-thumb {
          height: 5px;
          border-radius: 2px;
          background-color: #e6e9ea;
        }
        .selected-group-content {
            background-color: #ffffff;
            .selected-group-item {
              padding: 0 8px;
              line-height: 32px;
              box-shadow: 0 1px 1px 0 #00000014;
              border-radius: 2px;
              display: flex;
              align-items: center;
              justify-content: space-between;
              &:last-child {
                margin-bottom: 1px;
              }
              &-left {
                width: calc(100% - 30px);
                display: flex;
                align-items: center;
              }
              .selected-group-name {
                display: inline-block;
                margin-left: 5px;
                font-size: 12px;
                vertical-align: top;
                word-break: break-all;
              }
              .delete-depart-icon {
                display: block;
                font-size: 18px;
                color: #c4c6cc;
                cursor: pointer;
                &:hover {
                  color: #3a84ff;
                }
              }
              .user-count {
                color: #c4c6cc;
              }
            }
        }
      }
      .selected-empty-wrapper {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
    }
  }
}

/deep/ .bk-table-pagination-wrapper {
  padding: 15px 0;
  .bk-page.bk-page-align-right {
    .bk-page-selection-count-left {
      display: none;
    }
  }
}

</style>

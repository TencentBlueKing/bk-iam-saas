<template>
  <div class="resource-perm-manage-wrapper">
    <IamResourceCascadeSearch
      ref="iamResourceSearchRef"
      :custom-class="'resource-perm-manage'"
      :cur-search-data="searchData"
      :grid-count="gridCount"
      :system-required="true"
      :action-required="true"
      :resource-instance-required="false"
      :is-full-screen="true"
      :is-custom-search="true"
      :is-show-resource-type="false"
      :is-system-disabled="isSystemDisabled"
      :form-item-margin="12"
      :nav-stick-padding="24"
      @on-select-system="handleSelectSystemAction"
      @on-remote-table="handleRemoteTable"
      @on-refresh-table="handleRefreshTable"
    >
      <div slot="custom-default-search-item" class="custom-default-search-item">
        <iam-form-item
          :label="$t(`m.userGroup['用户/用户组']`)"
          :style="{ width: formItemWidth }"
          class="form-item-resource"
        >
          <bk-input
            v-model="formData.name"
            :clearable="true"
            :placeholder="$t(`m.verify['请输入']`)"
            :right-icon="'bk-icon icon-search'"
            @right-icon-click="handleSearch"
            @enter="handleSearch"
            @clear="handleClearSearch"
          />
        </iam-form-item>
      </div>
      <div slot="custom-content" class="custom-content">
        <div class="custom-content-footer">
          <bk-button
            theme="primary"
            class="operate-btn"
            @click="handleSearchTable"
          >
            {{ $t(`m.common['查询']`) }}
          </bk-button>
          <bk-button
            class="operate-btn reset-btn"
            theme="default"
            @click="handleReset"
          >
            {{ $t(`m.common['重置']`) }}
          </bk-button>
          <bk-popover
            v-if="isShowExport"
            :content="$t(`m.resourcePermiss['导出需提供系统和操作名']`)"
            :disabled="!isExportDisabled()"
          >
            <bk-button
              theme="default"
              class="operate-btn"
              :disabled="isExportDisabled()"
              @click="handleSearchAndExport(true)"
            >
              {{ $t(`m.common['导出']`) }}
            </bk-button>
          </bk-popover>
        </div>
      </div>
    </IamResourceCascadeSearch>
    
    <bk-table
      v-if="!tableLoading"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
      size="small"
      ext-cls="system-access-table"
      :data="tableList"
      :class="{ 'set-border': tableLoading }"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
    >
      <bk-table-column :label="$t(`m.resourcePermiss['有权限的成员']`)">
        <template slot-scope="{ row }">
          <span
            v-bk-tooltips="{ content: row.type === 'user' ? `${row.id} (${row.name})` : `${row.name}` }"
            class="system-access-name"
            @click.stop="handleViewDetail(row)"
          >
            {{row.type === 'user' ? `${row.id} (${row.name})` : `${row.name}`}}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.resourcePermiss['用户类型']`)">
        <template slot-scope="{ row }">
          {{row.type === 'user' ? $t(`m.nav['用户']`) : $t(`m.nav['用户组']`)}}
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :error-message="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>
    <!-- 用户组类型 -->
    <GroupDetailSlider :show.sync="isShowGroupDetailSlider" :cur-detail-data="curDetailData" />
    <!-- 人员权限详情 -->
    <MemberPermDetailSlider :show.sync="isShowMemberPermDetailSlider" :cur-detail-data="curDetailData" />
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { formatCodeData } from '@/common/util';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import GroupDetailSlider from './components/group-detail-slider.vue';
  import MemberPermDetailSlider from './components/member-perm-detail-slider.vue';

  export default {
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    components: {
      IamResourceCascadeSearch,
      GroupDetailSlider,
      MemberPermDetailSlider
    },
    data () {
      return {
        tableList: [],
        tableListBack: [],
        tableLoading: true,
        isShowGroupDetailSlider: false,
        isShowMemberPermDetailSlider: false,
        instanceLoading: false,
        sliderLoading: false,
        limit: 1000,
        resourceType: '',
        parentId: '',
        instanceSliderTitle: '',
        isShowInstanceSlider: false,
        currentBackup: 1,
        curResIndex: -1,
        groupIndex: -1,
        gridCount: 4,
        params: {},
        curDetailData: {},
        curSystemAction: {},
        searchData: [
          {
            id: 'group',
            name: this.$t(`m.userGroup['用户组名']`),
            default: true
          },
          {
            id: 'user',
            name: this.$t(`m.common['用户']`)
          }
        ],
        formItemWidth: '',
        searchType: 'resource_instance',
        systemIdError: false,
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        isSearchPerm: false,
        curSearchParams: {},
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        formData: {
          name: ''
        },
        emptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: this.$t(`m.resourcePermiss['查询必须选择“系统”和“操作名”']`),
          tipType: 'noPerm'
        },
        curEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters(['externalSystemId', 'user', 'index', 'navStick']),
      isShowExport () {
        return ['resourcePermiss'].includes(this.$route.name);
      },
      isSystemDisabled () {
        return this.index === 1 && ['system_manager'].includes(this.user.role.type);
      },
      isExportDisabled () {
        return () => {
          return !this.curSearchParams.action_id;
        };
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      navStick () {
        this.formatFormItemWidth();
      }
    },
    mounted () {
      this.formatFormItemWidth();
      window.addEventListener('resize', this.formatFormItemWidth);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
    },
    methods: {
      async handleRemoteTable (payload) {
        const { emptyData, searchParams } = payload;
        const params = {
          ...searchParams,
          ...this.formData
        };
        this.isSearchPerm = emptyData.tipType === 'search';
        this.curSearchParams = cloneDeep(params);
        this.curEmptyData = cloneDeep(emptyData);
        if (this.isExportDisabled()) {
          this.handleReset();
          return;
        }
        await this.handleSearchAndExport(false);
      },

      async handleRefreshTable () {
        this.curEmptyData.tipType = '';
        this.emptyData.tipType = '';
        this.formData.name = '';
        this.pagination.current = 1;
        this.isSearchPerm = false;
        this.curSearchParams = {};
        console.log(5655);
        await this.handleSearchAndExport(false);
      },

      // 查询和导入
      async handleSearchAndExport (isExport = false) {
        this.tableLoading = !isExport;
        const params = {
          ...this.curSearchParams,
          ...{
            limit: this.limit,
            permission_type: this.searchType
          }
        };
        try {
          const fetchUrl = isExport ? 'resourcePermiss/exportResourceManager' : 'resourcePermiss/getResourceManager';
          const res = await this.$store.dispatch(fetchUrl, params);
          if (isExport) {
            if (res.ok) {
              const blob = await res.blob();
              const url = URL.createObjectURL(blob);
              const element = document.createElement('a');
              element.download = `${this.$t(`m.nav['资源权限管理']`)}.xlsx`;
              element.href = url;
              element.click();
              URL.revokeObjectURL(blob);
              this.messageSuccess(this.$t(`m.resourcePermiss['导出成功！']`), 3000);
            }
          } else {
            this.tableListBack = res.data || [];
            this.pagination.count = this.tableList.length;
            const result = this.getDataByPage();
            this.tableList.splice(0, this.tableList.length, ...result);
            this.emptyData.tipType = 'search';
            this.emptyData = formatCodeData(res.code, this.emptyData, this.tableList.length === 0);
          }
        } catch (e) {
          this.tableList = [];
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async handleSearchTable () {
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleSearchUserGroup(true, true);
      },

      handleViewDetail (payload) {
        this.curDetailData = {
          ...payload,
          ...{
            system_id: this.curSearchParams.system_id
          }
        };
        const { type } = payload;
        const typeMap = {
          group: () => {
            this.isShowGroupDetailSlider = true;
          },
          user: () => {
            this.isShowMemberPermDetailSlider = true;
          }
        };
        return typeMap[type]();
      },

      handleSelectSystemAction (payload) {
        console.log(payload);
        this.curSystemAction = payload;
        if (payload && payload.action_id) {
          this.curSearchParams = Object.assign(this.curSearchParams, {
            system_id: payload.system_id.value,
            action_id: payload.action_id.value
          });
          this.handleSearchAndExport(false);
        }
      },
            
      // 搜索
      handleSearch () {
        const routeMap = {
          resourcePermManage: async () => {
            this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
            await this.handleSearchAndExport();
          },
          resourcePermiss: () => {
            this.tableList = this.getDataByPage();
            this.pagination.count = this.tableList.length;
            this.emptyData = formatCodeData(0, Object.assign(this.emptyData, { tipType: 'search' }));
          }
        };
        routeMap[this.$route.name]();
      },

      handleClearSearch () {
        this.handleSearch();
      },

      handleEmptyClear () {
        this.handleReset();
      },

      handleEmptyRefresh () {
        this.handleSearchAndExport();
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        const data = this.getDataByPage(page);
        this.tableList.splice(0, this.tableList.length, ...data);
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        const data = this.getDataByPage(this.pagination.current);
        this.tableList.splice(0, this.tableList.length, ...data);
      },

      // 重置
      handleReset () {
        this.searchType = 'resource_instance';
        if (!this.isSystemDisabled) {
          this.curSearchParams.systemId = '';
        }
        this.limit = 1000;
        this.tableList = [];
        this.formData = Object.assign(this.formData, { name: '' });
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10, showTotalCount: true });
        this.emptyData = {
          type: 'empty',
          text: '暂无数据',
          tip: this.$t(`m.resourcePermiss['查询必须选择“系统”和“操作名”']`),
          tipType: 'noPerm'
        };
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleClearSearch();
      },

      getDataByPage (page) {
        if (!page) {
          this.pagination.current = page = 1;
        }
        const { name } = this.formData;
        let tableList = cloneDeep(this.tableListBack);
        tableList = this.tableListBack.filter((item) => {
          if (['user'].includes(item.type)) {
            return item.id.indexOf(name) > -1
              || item.name.indexOf(name) > -1
              || `${item.id} (${item.name})`.indexOf(name) > -1;
          } else {
            return item.name.indexOf(name) > -1;
          }
        });
        let startIndex = (page - 1) * this.pagination.limit;
        let endIndex = page * this.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > tableList.length) {
          endIndex = tableList.length;
        }
        return tableList.slice(startIndex, endIndex);
      },

      formatFormItemWidth () {
        const navStickWidth = this.navStick ? 260 + 48 : 60 + 48;
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
        this.formItemWidth = `${(window.innerWidth - navStickWidth - (this.gridCount * 12)) / this.gridCount}px`;
      },

      resetDataAfterClose () {
        this.curResIndex = -1;
        this.groupIndex = -1;
        this.params = {};
        this.instanceSliderTitle = '';
      }
    }
  };
</script>

<style lang="postcss" scoped>
.resource-perm-manage-wrapper {
  padding: 16px 24px;
  /deep/ .resource-perm-manage {
    background-color: #f5f6fa;
    padding: 0;
    .form-item-resource {
      margin-right: 12px !important;
      .bk-select {
        background-color: #ffffff;
      }
    }
    .left {
      .resource-action-form {
        .error-tips {
          position: absolute;
          line-height: 16px;
          font-size: 10px;
          color: #ea3636;
        }
      }
    }
    .custom-content {
      &-footer {
        margin-top: 16px;
        font-size: 0;
        .operate-btn {
          font-size: 14px;
          margin-right: 8px;
          &.reset-btn {
            margin-right: 32px;
          }
        }
      }
    }
  }
  .system-access-table {
    margin-top: 16px;
    border-right: none;
    border-bottom: none;
    &.set-border {
      border-right: 1px solid #dfe0e5;
      border-bottom: 1px solid #dfe0e5;
    }
    .system-access-name {
      color: #3a84ff;
      cursor: pointer;
      &:hover {
        color: #699df4;
      }
    }
  }
}
</style>

<template>
  <div class="iam-apply-perm-template-table-wrapper">
    <render-search>
      <div slot="right">
        <iam-search-select
          @on-change="handleSearch"
          :data="searchData"
          :quick-search-method="quickSearchMethod"
          style="width: 420px;" />
      </div>
    </render-search>
    <bk-table
      :data="tableList"
      size="small"
      :class="{ 'set-border': tableLoading }"
      ext-cls="perm-template-table"
      :pagination="pagination"
      :cell-attributes="handleCellAttributes"
      @page-change="pageChange"
      @page-limit-change="limitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <bk-table-column type="selection" align="center" :selectable="handleDefaultSelect"></bk-table-column>
      <bk-table-column :label="$t(`m.permTemplate['模板名']`)">
        <template slot-scope="{ row }">
          <span class="perm-template-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['所属系统']`)">
        <template slot-scope="{ row }">
          <span :title="row.system.name">{{ row.system.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)">
        <template slot-scope="{ row }">
          <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
        </template>
      </bk-table-column>
    </bk-table>

    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :title="permSidesilderTitle"
      :template-id="curTemplateId"
      :template-version="curTemplateVersion"
      @on-view="handleOnView"
      @animation-end="handleAnimationEnd" />

    <bk-sideslider
      :is-show.sync="isShowSideslider"
      :title="sidesliderTitle"
      :width="880"
      :quick-close="true"
      @animation-end="handleViewResourceAnimationEnd">
      <div slot="content">
        <component :is="renderDetailCom" :data="previewData" />
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import RenderPermSideslider from '../../perm/components/render-template-perm-sideslider';
  import RenderDetail from '../../perm/components/render-detail';
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    components: {
      RenderPermSideslider,
      RenderDetail
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      count: {
        type: Number,
        default: 0
      },
      permTemplate: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        searchValue: {},
        tableList: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,

        isShowPermSidesilder: false,
        permSidesilderTitle: '',
        curTemplateId: '',
        curTemplateVersion: '',

        previewData: [],
        sidesliderTitle: '',
        isShowSideslider: false,
        renderDetailCom: 'RenderDetail'
      };
    },
    computed: {
            ...mapGetters(['externalSystemId'])
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      data: {
        handler (value) {
          this.tableList = [...value];
        },
        immediate: true
      },
      count: {
        handler (value) {
          this.pagination.count = value;
        },
        immediate: true
      }
    },
    created () {
      this.searchData = [
        {
          id: 'keyword',
          name: this.$t(`m.common['关键字']`),
          disabled: true
        },
        {
          id: 'system_id',
          name: this.$t(`m.common['系统']`),
          remoteMethod: this.handleRemoteSystem
        }
      ];
    },
    methods: {
      async fetchPermTemplateList () {
        this.tableLoading = true;
        const params = {
                    ...this.searchValue,
                    limit: this.pagination.limit,
                    offset: this.pagination.limit * (this.pagination.current - 1)
        };
        try {
          const res = await this.$store.dispatch('permTemplate/getTemplateList', params);
          this.pagination.count = res.data.count || 0;
          this.tableList.splice(0, this.tableList.length, ...(res.data.results || []));
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      handleResetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },

      handleRemoteSystem () {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        return this.$store.dispatch('system/getSystems', params)
          .then(({ data }) => {
            return data.map(({ id, name }) => ({ id, name }));
          });
      },

      handleCellAttributes ({ rowIndex, cellIndex, row, column }) {
        if (cellIndex === 0) {
          if (this.permTemplate.map(item => item.id).includes(row.id)) {
            return {
              title: this.$t(`m.info['你已被授予该模板权限']`)
            };
          }
          return {};
        }
        return {};
      },

      handleDefaultSelect (payload) {
        return !this.permTemplate.map(item => item.id).includes(payload.id);
      },

      handleSearch (payload) {
        this.searchValue = payload;
        this.handleResetPagination();
        this.fetchPermTemplateList(true);
      },

      handleView (payload) {
        this.curTemplateId = payload.id;
        this.curTemplateVersion = payload.version;
        this.permSidesilderTitle = `${payload.name}(${payload.system.name})`;
        this.isShowPermSidesilder = true;
      },

      handleOnView (payload) {
        const { name, data } = payload;
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${name}${this.$t(`m.common['】']`)}` });
        this.previewData = _.cloneDeep(data);
        this.isShowSideslider = true;
      },

      handleAnimationEnd () {
        this.permSidesilderTitle = '';
        this.curTemplateVersion = '';
        this.curTemplateId = '';
        this.isShowPermSidesilder = false;
      },

      handleViewResourceAnimationEnd () {
        this.previewData = [];
        this.sidesliderTitle = '';
        this.isShowSideslider = false;
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchPermTemplateList(true);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchPermTemplateList(true);
      },

      handlerAllChange (selection) {
        this.$emit('on-select', selection);
      },

      handlerChange (selection, row) {
        this.$emit('on-select', selection);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-apply-perm-template-table-wrapper {
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
        }
    }
</style>

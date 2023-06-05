<template>
  <div class="iam-apply-user-group-table-wrapper">
    <render-table
      :expanded="expanded"
      :data="tableList">
      <bk-table
        :data="curPageData"
        size="small"
        ext-cls="user-group-table"
        :pagination="pagination"
        @page-change="pageChange"
        @page-limit-change="limitChange">
        <bk-table-column :label="$t(`m.common['ID']`)" prop="display_id" width="180">
          <template slot-scope="{ row }">
            <span :title="row.display_id">{{ row.display_id }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
          <template slot-scope="{ row }">
            <span class="user-group-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['描述']`)">
          <template slot-scope="{ row }">
            <span :title="row.description !== '' ? row.description : ''">
              {{ row.description || '--' }}
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </render-table>

    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd" />
  </div>
</template>
<script>
  import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider';
  import RenderTable from '../common/render-table';

  export default {
    name: '',
    components: {
      RenderPermSideslider,
      RenderTable
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      count: {
        type: Number,
        default: 0
      }
    },
    data () {
      return {
        tableList: [],
        curPageData: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },

        currentBackup: 1,

        expanded: false,

        isShowPermSidesilder: false,
        curGroupName: '',
        curGroupId: ''
      };
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      data: {
        handler (value) {
          this.tableList = [...value];
          this.curPageData = this.getDataByPage(this.pagination.current);
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
    methods: {
      handleResetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },

      getDataByPage (page) {
        if (!page) {
          this.pagination.current = page = 1;
        }
        let startIndex = (page - 1) * this.pagination.limit;
        let endIndex = page * this.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.tableList.length) {
          endIndex = this.tableList.length;
        }
        return this.tableList.slice(startIndex, endIndex);
      },

      handleView (payload) {
        this.curGroupName = payload.name;
        this.curGroupId = payload.id;
        this.isShowPermSidesilder = true;
      },

      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSidesilder = false;
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        const data = this.getDataByPage(page);
        this.curPageData.splice(0, this.curPageData.length, ...data);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        const data = this.getDataByPage(this.pagination.current);
        this.curPageData.splice(0, this.curPageData.length, ...data);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-apply-user-group-table-wrapper {
        margin-top: 20px;
        .user-group-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            .user-group-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>

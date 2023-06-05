<template>
  <div class="iam-join-rate-manager-process-wrapper">
    <render-search>
      <bk-button theme="primary"
        :disabled="!isCanBatchDelete"
        @click="handleBatchDelete">
        {{ $t(`m.approvalProcess['批量设置']`) }}
      </bk-button>
      <div slot="right">
        <bk-input
          v-model="searchValue"
          :placeholder="$t(`m.approvalProcess['加入管理空间流程搜索提示']`)"
          clearable
          style="margin-left: 8px; width: 320px;"
          right-icon="bk-icon icon-search"
          @enter="handleSearch" />
      </div>
    </render-search>
    <bk-table
      :data="tableList"
      size="small"
      ext-cls="join-rate-manager-process-table"
      :outer-border="false"
      :header-border="false"
      :pagination="pagination"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
      @page-change="pageChange"
      @page-limit-change="limitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      @row-mouse-enter="handleRowMouseEnter"
      @row-mouse-leave="handleRowMouseLeave">
      <bk-table-column type="selection" align="center" :selectable="getSelectable"></bk-table-column>
      <bk-table-column :label="$t(`m.approvalProcess['管理空间名称']`)" width="400">
        <template slot-scope="{ row }">
          <span class="rate-manager-name" :title="row.groupName" @click.stop="handleViewDetail(row)">
            {{ row.groupName }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)" prop="description" width="400">
        <template slot-scope="{ row }">
          <span :title="row.description">{{ row.description }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.approvalProcess['审批流程']`)">
        <template slot-scope="{ row }">
          <section class="process-select-wrapper" v-if="row.canEdit || row.isToggle">
            <bk-select
              :value="row.processValue"
              :clearable="false"
              searchable
              @selected="handleProcessSelect(...arguments, row)"
              @toggle="handleSelectToggle(...arguments, row)">
              <bk-option v-for="option in list"
                :key="option.id"
                :id="option.id"
                :name="option.name">
              </bk-option>
            </bk-select>
          </section>
          <section class="process-name" v-else>
            {{ row.processValue | proceeNameFilter(list) }}
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

    <edit-process-dialog
      :show.sync="isProcessDialogShow"
      :list="list"
      @on-submit="handleEditProcess"
      @on-cancel="isProcessDialogShow = false" />
  </div>
</template>
<script>
  import editProcessDialog from './edit-process-dialog';
  export default {
    name: '',
    components: {
      editProcessDialog
    },
    filters: {
      proceeNameFilter (value, list) {
        const data = list.find(item => item.id === value);
        if (data) return data.name;
        return '';
      }
    },
    props: {
      list: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        currentSelectList: [],
        tableList: [
          {
            groupName: '测试管理空间',
            id: 1,
            description: 'qqqq',
            processValue: '1'
          }
        ],
        pagination: {
          current: 1,
          count: 1,
          limit: 10
        },
        currentBackup: 1,
        searchValue: '',
        tableLoading: false,
        isProcessDialogShow: false,
        emptyData: {
          type: 'empty',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      isCanBatchDelete () {
        return this.currentSelectList.length > 0 && this.tableList.length > 0;
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    methods: {
      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        // this.fetchMemberList()
      },

      handleSearch () {},

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        // this.fetchMemberList()
      },

      handlerAllChange (selection) {
        this.currentSelectList = [...selection];
      },

      handlerChange (selection, row) {
        this.currentSelectList = [...selection];
      },

      handleProcessSelect (value, option, item) {

      },

      handleSelectToggle (payload, row) {
        if (payload) {
          this.$set(row, 'isToggle', true);
        } else {
          this.$delete(row, 'isToggle');
        }
      },

      handleRowMouseEnter (index) {
        this.$set(this.tableList[index], 'canEdit', true);
      },

      handleRowMouseLeave (index) {
        this.$delete(this.tableList[index], 'canEdit');
      },

      getSelectable (row, index) {
        if (this.tableList.length < 1) {
          return false;
        }
        return true;
      },

      handleBatchDelete () {
        this.isProcessDialogShow = true;
      },

      handleEditProcess (payload) {
        this.isProcessDialogShow = false;
      },

      handleViewDetail (payload) {

      }
    }
  };
</script>
<style lang="postcss">
    .iam-join-rate-manager-process-wrapper {
        .join-rate-manager-process-table {
            margin-top: 16px;
            border: none;
            .process-name {
                position: relative;
                padding-left: 11px;
                line-height: 30px;
                color: #63656e;
                cursor: pointer;
            }
            .process-select-wrapper {
                background: #fff;
            }
            .rate-manager-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>

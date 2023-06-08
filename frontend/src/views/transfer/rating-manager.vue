<template>
  <div class="iam-transfer-group-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
    v-bkloading="{ isLoading, opacity: 1 }">
    <template v-if="!isLoading && !isEmpty">
      <div class="transfer-group-content">
        <div class="header" @click="handlerateExpanded">
          <Icon bk class="expanded-icon" :type="rateExpanded ? 'down-shape' : 'right-shape'" />
          <label class="title">{{ $t(`m.permTransfer['管理空间权限交接']`) }}</label>
        </div>
        <div class="content" v-if="rateExpanded">
          <div class="slot-content">
            <bk-table
              border
              ref="rateTable"
              :data="rateListRender"
              size="small"
              :class="{ 'set-border': tableLoading }"
              v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
              :row-key="tableRowKey"
              @selection-change="handleSelectionChange"
              @select-all="handleSelectAll">
              <bk-table-column type="selection" align="center"
                :reserve-selection="true">
              </bk-table-column>
              <bk-table-column :label="$t(`m.grading['管理空间名称']`)" width="300">
                <template slot-scope="{ row }">
                  <bk-button text>{{row.name}}</bk-button>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.common['描述']`)" width="300">
                <template slot-scope="{ row }">
                  {{row.description || '--'}}
                </template>
              </bk-table-column>
            </bk-table>
          </div>
          <p class="expand-action" @click="handlerateShowAll" v-if="rateListAll.length > 5">
            <Icon :type="rateShowAll ? 'up-angle' : 'down-angle'" />
            <template v-if="!rateShowAll">{{ $t(`m.common['点击展开']`) }}</template>
            <template v-else>{{ $t(`m.common['点击收起']`) }}</template>
          </p>
        </div>
      </div>
    </template>
    <template v-if="!isLoading && isEmpty">
      <div class="empty-wrapper">
        <!-- <iam-svg />
                <p class="text">{{ $t(`m.common['暂无数据']`) }}</p> -->
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </div>
    </template>
  </div>
</template>

<script>
  import { formatCodeData } from '@/common/util';
  export default {
    name: '',
    components: {
    },
    data () {
      return {
        isEmpty: false,
        isLoading: false,
        rateListRender: [],
        rateListAll: [], // 管理空间权限交接
        rateExpanded: true,
        isSelectAllChecked: false,
        rateSelectData: [],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    mounted () {
      this.fetchData();
    },
    methods: {
      async fetchData () {
        this.isLoading = true;
        try {
          const { code, data } = await this.$store.dispatch('role/getRatingManagerList', {
            limit: 1024, // 接口是分页接口...需要确认
            offset: '',
            name: ''
          });
          const rateListAll = data.results || [];
          this.rateListAll.splice(0, this.rateListAll.length, ...rateListAll);
          const rateListRender = data.results.length > 5
            ? data.results.slice(0, 5) : data.results;
          this.rateListRender.splice(0, this.rateListRender.length, ...rateListRender);
          this.isEmpty = rateListAll.length < 1;
          this.emptyData = formatCodeData(code, this.emptyData, this.isEmpty);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.isLoading = false;
        }
      },
            
      handleEmptyRefresh () {
        this.fetchData();
      },

      handlerateExpanded () {
        this.rateExpanded = !this.rateExpanded;
      },

      handleSelectAll (selection) {
        this.isSelectAllChecked = !!selection.length;

        if (this.isSelectAllChecked) {
          this.rateSelectData.splice(
            0,
            this.rateSelectData.length,
            ...this.rateListAll
          );
        }
                
        this.$emit('rate-selection-change', this.rateSelectData);
      },

      handleSelectionChange (selection) {
        this.isSelectAllChecked = selection.length === this.rateListAll.length;
        this.rateSelectData.splice(0, this.rateSelectData.length, ...selection);

        this.$emit('rate-selection-change', this.rateSelectData);
      },

      handlerateShowAll () {
        this.rateShowAll = !this.rateShowAll;
        if (this.rateShowAll) {
          this.rateListRender.splice(
            0,
            this.rateListRender.length,
            ...this.rateListAll
          );
        } else {
          this.rateListRender.splice(
            0,
            this.rateListRender.length,
            ...(this.rateListAll.length > 5 ? this.rateListAll.slice(0, 5) : this.rateListAll)
          );
        }
        if (this.isSelectAllChecked) {
          this.$refs.rateTable.clearSelection();
          this.$refs.rateTable.toggleAllSelection();
        }
      },

      tableRowKey (row) {
        return row.id + '__' + row.name;
      }
    }
  };
</script>
<style lang="postcss">
    @import './group.css';
    .member-item {
            position: relative;
            display: inline-block;
            margin: 0 6px 6px 0;
            padding: 0 10px;
            line-height: 22px;
            background: #f5f6fa;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            font-size: 12px;
            .member-name {
                display: inline-block;
                max-width: 200px;
                line-height: 17px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: text-top;
                .count {
                    color: #c4c6cc;
                }
            }
        }
</style>

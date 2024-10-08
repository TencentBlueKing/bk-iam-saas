<template>
  <div class="iam-perm-audit-policy-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <bk-table
      v-if="!loading"
      :data="tableList"
      :outer-border="false"
      :header-border="false"
      :header-cell-style="{ background: '#f5f6fa', borderRight: 'none' }"
      :cell-class-name="getCellClass"
      @cell-mouse-enter="handleCellMouseEnter"
      @cell-mouse-leave="handleCellMouseLeave"
    >
      <bk-table-column :label="$t(`m.common['操作']`)" :width="300">
        <template slot-scope="{ row }">
          <Icon
            type="pin"
            class="relate-action-tips-icon"
            v-bk-tooltips="{ content: $t(`m.common['依赖操作']`), extCls: 'iam-tooltips-cls' }"
            v-if="row.tag === 'related'" />
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column
        prop="system_id"
        column-key="filterTag"
        :width="300"
        :label="$t(`m.common['所属系统']`)"
        :filter-multiple="false"
        :filters="systemFilter"
        :filter-method="handleSystemFilterMethod"
        @filter-change="handleFilterChange"
      >
        <template slot-scope="{ row }">
          <span :title="row.system_name">{{ row.system_name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" prop="resource_instance">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div v-for="_ in row.resource_groups" :key="_.id">
              <p class="related-resource-item"
                v-for="item in _.related_resource_types"
                :key="item.type">
                <render-resource-popover
                  :key="item.type"
                  :data="item.condition"
                  :value="`${item.name}：${item.value}`"
                  :max-width="380"
                  :is-show-popover="row.showPopover"
                  @on-view="handleViewResource(row)" />
              </p>
            </div>
          </template>
          <template v-else>
            {{ $t(`m.common['无需关联实例']`) }}
          </template>
          <Icon
            type="detail-new"
            class="view-icon"
            :title="$t(`m.common['详情']`)"
            v-if="isShowPreview(row)"
            @click.stop="handleViewResource(row)" />
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

    <bk-sideslider
      :is-show.sync="isShowSideSlider"
      :title="sideSliderTitle"
      :width="960"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      <div slot="content">
        <component :is="renderDetailCom" :data="previewData" />
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import RenderDetail from './render-detail';
  import GradePolicy from '@/model/grade-policy';
  export default {
    name: '',
    components: {
      RenderResourcePopover,
      RenderDetail
    },
    props: {
      actions: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        tableList: [],
        tableListBack: [],
        initRequestQueue: [],
        curDeleteIds: [],
        previewData: [],
        curId: '',
        renderDetailCom: 'RenderDetail',
        isShowSideSlider: false,
        sideSliderTitle: '',
        curFilterSystem: '',
        systemFilter: [],
        policyCountMap: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      loading () {
        return this.initRequestQueue.length > 0;
      },
      isShowPreview () {
        return (payload) => {
          return !payload.isEmpty;
        };
      }
    },
    watch: {
      actions: {
        handler (value) {
          if (value.length > 0) {
            value.forEach(e => {
              if (!e.name) {
                e.name = e.action ? e.action.name : '--';
              }
            });
            this.tableList = value.map(item => new GradePolicy(item));
            this.tableList.forEach(item => {
              if (!this.systemFilter.find(subItem => subItem.value === item.system_id)) {
                this.systemFilter.push({
                  text: item.system_name,
                  value: item.system_id
                });
              }
            });
            this.tableListBack = _.cloneDeep(this.tableList);
          }
        },
        immediate: true
      }
    },
    methods: {
      handleAnimationEnd () {
        this.sideSliderTitle = '';
        this.previewData = [];
        this.curId = '';
      },

      handleCellMouseEnter (row, column, cell, event) {
        if (['resource_instance'].includes(column.property)) {
          this.$set(row, 'showPopover', true);
        }
      },
      
      handleCellMouseLeave (row, column, cell, event) {
        if (['resource_instance'].includes(column.property)) {
          this.$set(row, 'showPopover', false);
        }
      },

      handleSystemFilterMethod (value, row, column) {
        const property = column.property;
        this.curFilterSystem = value;
        return row[property] === this.curFilterSystem;
      },

      handleFilterChange (payload) {
        const { filterTag } = payload;
        this.curFilterSystem = filterTag.length > 0 ? filterTag[0] : '';
        this.emptyData.tipType = 'search';
      },

      handleViewResource (payload) {
        this.curId = payload.id;
        const params = [];
        if (payload.resource_groups.length > 0) {
          payload.resource_groups.forEach(groupItem => {
            if (groupItem.related_resource_types.length > 0) {
              groupItem.related_resource_types.forEach(item => {
                const { name, type, condition } = item;
                params.push({
                  name: type,
                  label: this.$t(`m.info['tab操作实例']`, { value: name }),
                  tabType: 'resource',
                  data: condition
                });
              });
            }
          });
        }
        this.previewData = _.cloneDeep(params);
        this.sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideSlider = true;
      },

      handleEmptyClear () {
        this.emptyData.tipType = '';
        this.curFilterSystem = '';
        this.tableList = _.cloneDeep(this.tableListBack);
      },

      handleEmptyRefresh () {
        this.$emit('on-refresh');
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 2) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-perm-audit-policy-table {
        min-height: 101px;
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .bk-table {
            border: none;
            .bk-table-header-wrapper {
                .cell {
                    padding-left: 15px !important;
                }
            }
            .relate-action-tips-icon {
                position: absolute;
                top: 50%;
                left: 5px;
                transform: translateY(-50%);
                &:hover {
                    color: #3a84ff;
                }
            }
            .bk-table-body-wrapper {
                .cell {
                    .view-icon {
                        display: none;
                        position: absolute;
                        top: 50%;
                        right: 10px;
                        transform: translate(0, -50%);
                        font-size: 18px;
                        cursor: pointer;
                    }
                    &:hover {
                        .view-icon {
                            display: inline-block;
                            color: #3a84ff;
                        }
                    }
                }
            }
            tr:hover {
                background-color: #fff;
            }
            .bk-table-row-last {
                td {
                    border-bottom: 1px solid #dfe0e5 !important;
                }
            }
        }
    }
</style>

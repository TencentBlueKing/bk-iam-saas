<template>
  <div class="iam-perm-aggregate-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <bk-table
      v-if="!loading"
      :data="tableList"
      border
      :cell-class-name="getCellClass">
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
        :label="$t(`m.common['所属系统']`)"
        :filters="systemFilter"
        :filter-method="systemFilterMethod"
        :filter-multiple="false"
        prop="system_id"
        :width="300">
        <template slot-scope="{ row }">
          <span :title="row.system_name">{{ row.system_name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div v-for="(_, _index) in row.resource_groups" :key="_.id" class="related-resource-list"
              :class="row.resource_groups === 1 || _index === row.resource_groups.length - 1
                ? '' : 'related-resource-list-border'">
              <p class="related-resource-item"
                v-for="item in _.related_resource_types"
                :key="item.type">
                <render-resource-popover
                  :key="item.type"
                  :data="item.condition"
                  :value="`${item.name}：${item.value}`"
                  :max-width="380"
                  @on-view="handleViewResource(_, row)" />
              </p>
              <Icon
                type="detail-new"
                class="view-icon"
                :title="$t(`m.common['详情']`)"
                v-if="isShowPreview(row)"
                @click.stop="handleViewResource(_, row)" />
            </div>
          </template>
          <template v-else>
            <span class="pl20">{{ $t(`m.common['无需关联实例']`) }}</span>
          </template>
        </template>
      </bk-table-column>
    </bk-table>

    <bk-sideslider
      :is-show.sync="isShowSideslider"
      :title="sidesliderTitle"
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
        policyCountMap: {},
        initRequestQueue: [],
        curDeleteIds: [],
        previewData: [],
        curId: '',
        renderDetailCom: 'RenderDetail',
        isShowSideslider: false,
        sidesliderTitle: '',
        systemFilter: []
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
            this.tableList = value.map(item => new GradePolicy(item)); // 继承。此处会新增字段
            this.tableList.forEach(item => {
              if (!this.systemFilter.find(subItem => subItem.value === item.system_id)) {
                this.systemFilter.push({
                  text: item.system_name,
                  value: item.system_id
                });
              }
            });
          }
        },
        immediate: true
      }
    },
    methods: {
      handleAnimationEnd () {
        this.sidesliderTitle = '';
        this.previewData = [];
        this.curId = '';
      },

      systemFilterMethod (value, row, column) {
        const property = column.property;
        return row[property] === value;
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 2) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      handleViewResource (groupItem, payload) {
        this.curId = payload.id;
        const params = [];
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
        this.previewData = _.cloneDeep(params);
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideslider = true;
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-perm-aggregate-table {
        /* max-height: 300px;
        overflow-y: auto; */
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .related-resource-list{
            position: relative;
            .related-resource-item{
                margin: 20px !important;
            }
            .view-icon {
                display: none;
                position: absolute;
                top: 50%;
                right: 40px;
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
            .effect-icon {
                display: none;
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .effect-icon {
                    display: inline-block;
                    color: #3a84ff;
                }
            }
            &-border{border-bottom: 1px solid #dfe0e5;}
        }
        .bk-table {
            border-right: none;
            border-bottom: none;
            .bk-table-header-wrapper {
                .cell {
                    padding-left: 20px !important;
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
                    padding: 20px !important;
                }
            }
            .iam-perm-table-cell-cls {
                .cell {
                    padding: 0px !important;
                }
            }
            tr:hover {
                background-color: #fff;
            }
        }
    }
</style>

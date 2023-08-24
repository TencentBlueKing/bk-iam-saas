<template>
  <div class="iam-apply-create-rate-manager-content">
    <render-vertical-block>
      <bk-table
        :data="tableList"
        ext-cls="apply-content-table"
        border
        :cell-class-name="getCellClass">
        <bk-table-column :label="$t(`m.common['操作']`)" width="360">
          <template slot-scope="{ row }">
            <Icon
              type="pin"
              class="relate-action-tips-icon"
              v-bk-tooltips="{ content: $t(`m.common['依赖操作']`), extCls: 'iam-tooltips-cls' }"
              v-if="row.tag === 'related'" />
            <span :title="row.name">{{ row.name }}</span>
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
                  v-if="!row.isEmpty"
                  @click.stop="handleViewResource(_, row)" />
              </div>
            </template>
            <template v-else>
              <span class="pl20">{{ $t(`m.common['无需关联实例']`) }}</span>
            </template>
          </template>
        </bk-table-column>
      </bk-table>
    </render-vertical-block>
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
  import Resource from '@/components/render-resource/detail';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import DetailContent from './detail-content';
  export default {
    name: '',
    components: {
      Resource,
      DetailContent,
      RenderResourcePopover
    },
    props: {
      data: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        previewData: {},
        renderDetailCom: 'DetailContent',
        isShowSideslider: false,
        sidesliderTitle: '',
        tableList: [],
        curId: ''
      };
    },
    watch: {
      data: {
        handler (value) {
          this.tableList = _.cloneDeep(value);
        },
        immediate: true
      }
    },
    methods: {
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      handleViewResource (groupItem, row) {
        this.previewData = _.cloneDeep(this.handleDetailData(groupItem));
        this.renderDetailCom = 'DetailContent';
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideslider = true;
      },

      handleDetailData (payload) {
        this.curId = payload.id;
        const params = [];
        if (payload.related_resource_types.length > 0) {
          payload.related_resource_types.forEach(item => {
            const { name, type, condition } = item;
            params.push({
              name: type,
              label: `${name} ${this.$t(`m.common['实例']`)}`,
              tabType: 'resource',
              data: condition
            });
          });
        }
        return params;
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-apply-create-rate-manager-content {
        background: #fff;
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .apply-content-table {
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

            .related-resource-list{
                position: relative;
                .related-resource-item{
                    margin: 20px !important;
                }
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

<template>
  <div class="iam-apply-content">
    <render-vertical-block
      :label="applyTitle"
      ext-cls="apply-title">
      <bk-table
        :data="tableList"
        ext-cls="apply-content-table"
        border
        :cell-class-name="getCellClass">
        <bk-table-column :label="$t(`m.common['操作']`)" min-width="160">
          <template slot-scope="{ row }">
            <Icon
              type="pin"
              class="relate-action-tips-icon"
              v-bk-tooltips="{ content: $t(`m.common['依赖操作']`), extCls: 'iam-tooltips-cls' }"
              v-if="row.tag === 'related'" />
            <span :title="row.name">{{ row.name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" min-width="360">
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
                    :value="`${item.name}${$t(`m.common['：']`)}${item.value}`"
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
              <div class="pl20 mt20">{{ $t(`m.common['无需关联实例']`) }}</div>
            </template>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['生效条件']`)" min-width="300">
          <template slot-scope="{ row, $index }">
            <div class="condition-table-cell" v-if="row.resource_groups.length">
              <div v-for="(_, groIndex) in row.resource_groups" :key="_.id"
                class="related-condition-list"
                :class="[row.resource_groups.length > 1 ? 'related-resource-list' : 'environ-group-one',
                         row.resource_groups === 1 || groIndex === row.resource_groups.length - 1
                           ? '' : 'related-resource-list-border']">
                <effect-conditon
                  :value="_.environments"
                  @on-click="showTimeSlider(row, $index, groIndex)">
                </effect-conditon>
                <Icon
                  type="detail-new"
                  class="effect-icon"
                  :title="$t(`m.common['详情']`)"
                  v-if="isShowPreview(row)"
                  @click.stop="handleEnvironmentsViewResource(_, row)" />
              </div>
            </div>
            <div v-else class="ml20 mt20">{{ $t(`m.common['无生效条件']`) }}</div>
          </template>
        </bk-table-column>
        <bk-table-column prop="expired_dis" min-width="100" :label="$t(`m.common['申请期限']`)"></bk-table-column>
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
    <bk-sideslider
      :is-show="isShowEnvironmentsSideslider"
      :title="environmentsSidesliderTitle"
      :width="960"
      quick-close
      @update:isShow="handleResourceCancel"
      ext-cls="effect-conditon-side">
      <div slot="content">
        <effect-conditon
          :value="environmentsSidesliderData"
          :is-empty="!environmentsSidesliderData.length"
          @on-view="handleViewSidesliderCondition"
        >
        </effect-conditon>
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import Resource from '@/components/render-resource/detail';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import DetailContent from './detail-content';
  import EffectConditon from './effect-conditon';
  import SidesliderEffectConditon from './sideslider-effect-condition';
  export default {
    name: '',
    components: {
      Resource,
      DetailContent,
      RenderResourcePopover,
      EffectConditon,
      SidesliderEffectConditon
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      system: {
        type: Object,
        default: () => {
          return {};
        }
      },
      actionTopologies: {
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
        curId: '',
        environmentsSidesliderData: [],
        isShowResourceInstanceEffectTime: false
      };
    },
    computed: {
      applyTitle () {
        return `${this.$t(`m.myApply['申请内容']`)}${this.$t(`m.common['（']`)}${this.system.system_name}${this.$t(`m.common['）']`)}`;
      },
      isShowPreview () {
        return (payload) => {
          return !payload.isEmpty && payload.policy_id !== '';
        };
      }
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
        if (columnIndex === 1 || columnIndex === 2) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      handleViewResource (groupItem, row) {
        this.previewData = _.cloneDeep(this.handleDetailData(groupItem));
        this.renderDetailCom = 'DetailContent';
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}` });
        // this.sidesliderTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
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
      },

      /**
       * handleEnvironmentsViewResource
       */
      handleEnvironmentsViewResource (payload, data) {
        this.environmentsSidesliderData = payload.environments;
        console.log('environmentsSidesliderData', this.environmentsSidesliderData);
        this.isShowEnvironmentsSideslider = true;
        this.environmentsSidesliderTitle = this.$t(`m.info['关联侧边栏操作生效条件']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        // this.environmentsSidesliderTitle = `${this.$t(`m.common['关联操作']`)}${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['生效条件']`)}`;
      },

      /**
       * handleViewSidesliderCondition
       */
      handleViewSidesliderCondition () {
        console.log('environmentsSidesliderData', this.environmentsSidesliderData);
        this.isShowResourceInstanceEffectTime = true;
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-apply-content {
        margin-top: 16px;
        padding: 20px 30px;
        background: #fff;
        border-radius: 2px;
        box-shadow: 0px 1px 2px 0px rgba(49, 50, 56, .1);
        .apply-title {
            .label {
                margin-bottom: 15px;
                font-size: 14px !important;
                color: #63656e;
                font-weight: bold;
            }
        }
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

            .related-condition-list{
                flex: 1;
                display: flex;
                flex-flow: column;
                justify-content: center;
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
                    height: 100%;
                }
                .condition-table-cell{
                    height: 100%;
                    flex-flow: column;
                    display: flex;
                    justify-content: center;
                    /* padding: 15px 0; */
                }
            }
            tr:hover {
                background-color: #fff;
            }
        }
    }
</style>

<template>
  <div class="iam-apply-create-rate-manager-content">
    <render-vertical-block>
      <bk-table
        :data="tableList"
        ext-cls="apply-content-table"
        border
        :cell-class-name="getCellClass"
      >
        <bk-table-column :label="$t(`m.common['操作']`)" width="180">
          <template slot-scope="{ row }">
            <Icon
              v-if="row.tag === 'related'"
              type="pin"
              class="relate-action-tips-icon"
              v-bk-tooltips="{ content: $t(`m.common['依赖操作']`), extCls: 'iam-tooltips-cls' }"
            />
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
              <span>{{ $t(`m.common['无需关联实例']`) }}</span>
            </template>
          </template>
        </bk-table-column>
        <template v-if="isShowSensitivityLevel">
          <bk-table-column :label="$t(`m.nav['敏感等级']`)">
            <template slot-scope="{ row }">
              <span>{{ getSensitivityLevel(row.sensitivity_level) }}</span>
            </template>
          </bk-table-column>
        </template>
        <template v-if="isShowExpired">
          <bk-table-column prop="expired_display" min-width="100" :label="$t(`m.common['申请期限']`)" />
        </template>
      </bk-table>
    </render-vertical-block>
    <bk-sideslider
      :is-show.sync="isShowSideslider"
      :title="sidesliderTitle"
      :width="960"
      :quick-close="true"
    >
      <div slot="content">
        <component :is="renderDetailCom" :data="previewData" />
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { SENSITIVITY_LEVEL_ENUM } from '@/common/constants';
  import Resource from '@/components/render-resource/detail';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import DetailContent from './detail-content';
  export default {
    components: {
      Resource,
      DetailContent,
      RenderResourcePopover
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      isShowSensitivityLevel: {
        type: Boolean,
        default: false
      },
      isShowExpired: {
        type: Boolean,
        default: false
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
          this.tableList = cloneDeep(value);
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
        this.previewData = cloneDeep(this.getDetailData(groupItem));
        this.renderDetailCom = 'DetailContent';
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideslider = true;
      },

      getSensitivityLevel (level) {
        const levelData = SENSITIVITY_LEVEL_ENUM.find(item => item.id === level);
        if (levelData) {
          return this.$t(`m.sensitivityLevel['${levelData.name}']`);
        }
        return '--';
      },

      getDetailData (payload) {
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
  background-color: #ffffff;

  .apply-content-table {
    border-right: none;
    border-bottom: none;

    .relate-action-tips-icon {
      position: absolute;
      top: 50%;
      left: 6px;
      transform: translateY(-50%);
      
      &:hover {
        color: #3a84ff;
      }
    }

    .related-resource-list {
      position: relative;

      .view-icon {
        display: none;
        position: absolute;
        top: 50%;
        right: 10px;
        transform: translate(0, -50%);
        font-size: 18px;
        cursor: pointer;
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

        .view-icon,
        .effect-icon {
          display: inline-block;
          color: #3a84ff;
        }
      }

      &-border {
        border-bottom: 1px solid #dfe0e5;
      }
    }
  }
}
</style>

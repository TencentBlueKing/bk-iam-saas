<template>
  <div class="iam-transfer-custom-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <bk-table
      v-if="!loading"
      ref="customTable"
      :data="renderPolicyList"
      border
      :header-cell-class-name="getCellClass"
      :cell-class-name="getCellClass"
      @select="handleSelect"
      @select-all="handleSelect">
      <bk-table-column type="selection" align="center" :selectable="row => !row.isExpired">
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)">
        <template slot-scope="{ row }">
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" width="491">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <template v-for="(relatedGroup, relatedGroupIndex) in row.resource_groups">
              <div :key="relatedGroupIndex" style="display: inline-block;padding: 5px 0;">
                <p class="related-resource-item"
                  v-for="item in relatedGroup.related_resource_types"
                  :key="item.type">
                  {{`${item.name}：${item.value}`}}
                </p>
              </div>
            </template>
          </template>
          <template v-else>
            {{ $t(`m.common['无需关联实例']`) }}
          </template>
        </template>
      </bk-table-column>
      <bk-table-column prop="expired_dis" :label="$t(`m.common['有效期']`)"></bk-table-column>
    </bk-table>
  </div>
</template>
<script>
  export default {
    props: {
      policyList: {
        type: Array,
        default: () => ([])
      },
      loading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        renderPolicyList: []
      };
    },
    watch: {
      loading: {
        handler (v) {
          if (v) {
            return;
          }
          this.renderPolicyList.splice(0, this.renderPolicyList.length, ...(this.policyList || []));
          this.renderPolicyList.forEach(p => {
            this.$nextTick(() => {
              this.$refs.customTable && this.$refs.customTable.toggleRowSelection(p, !!p.transferChecked);
            });
          });
        }
        // immediate: true
        // deep: true
      }
    },
    methods: {
      // handleCheckbox (row) {
      //     this.$emit('custom-selection-change', this.renderPolicyList)
      // },

      handleSelect (selection) {
        this.$emit('custom-selection-change', selection);
      },

      /**
       * getCellClass
       */
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 0) {
          return 'checkbox-cell-wrapper';
        }
        return '';
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-transfer-custom-table {
        min-height: 101px;
    }
</style>

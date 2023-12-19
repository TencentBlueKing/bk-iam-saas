<template>
  <div class="manual-wrapper">
    <div class="manual-wrapper-left">
      <bk-input
        ref="manualInputRef"
        type="textarea"
        class="manual-textarea"
        v-model="manualValue"
        :placeholder="$t(`m.common['请输入实例名称，以回车/逗号/分号/空格分割']`)"
        :rows="14"
        @input="handleManualInput"
      />
      <p class="manual-error-text pr10" v-if="manualInputError">
        {{ $t(`m.common['实例名称输入错误或不存在于授权资源实例范围内']`) }}
      </p>
      <div class="manual-bottom-btn">
        <bk-button
          theme="primary"
          :outline="true"
          style="width: 168px"
          :loading="manualAddLoading"
          :disabled="isManualDisabled"
          @click="handleAddManualUser">
          {{ $t(`m.common['解析并添加']`) }}
        </bk-button>
        <bk-button style="margin-left: 10px" @click="handleClearManualInput">
          {{ $t(`m.common['清空']`) }}
        </bk-button>
      </div>
    </div>
    <div v class="manual-wrapper-right">
      <bk-input
        v-model="tableKeyWord"
        class="manual-input-wrapper"
        :placeholder="$t(`m.common['搜索解析结果']`)"
        :right-icon="'bk-icon icon-search'"
        :clearable="true"
        @clear="handleClearSearch"
        @enter="handleTableSearch"
        @right-icon-click="handleTableSearch"
      />
      <div>
        <bk-table
          ref="manualTableRef"
          size="small"
          :data="manualTableList"
          :ext-cls="'manual-table-wrapper'"
          :outer-border="false"
          :header-border="false"
          @select="handleSelectChange"
          @select-all="handleSelectAllChange">

          <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
          <bk-table-column :label="$t(`m.common['实例名称']`)" prop="name">
            <template slot-scope="{ row }">
              <span :title="row.display_name">
                {{ row.display_name }}
              </span>
            </template>
          </bk-table-column>
          <template slot="empty">
            <ExceptionEmpty
              :type="emptyTableData.type"
              :empty-text="emptyTableData.text"
              :tip-text="emptyTableData.tip"
              :tip-type="emptyTableData.tipType"
              @on-clear="handleClearSearch"
            />
          </template>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { formatCodeData } from '@/common/util';
  export default {
    props: {
      curSelectedChain: {
        type: Object
      },
      systemParams: {
        type: Object
      },
      selectionMode: {
        type: String
      },
      hasSelectedValues: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        tableKeyWord: '',
        manualValue: '',
        manualAddLoading: false,
        manualInputError: false,
        manualTableListStorage: [{
          id: 1,
          display_name: 'admin',
          child_type: ''
        }],
        manualTableList: [],
        hasSelectedInstances: [],
        pagination: {
          current: 1,
          limit: 10,
          count: 1,
          showTotalCount: true
        },
        emptyTableData: {
          type: 'empty',
          text: '请先从左侧输入并解析',
          tip: '',
          tipType: ''
        },
        regValue: /，|,|；|;|、|\\|\n|\s/
      };
    },
    computed: {
      isManualDisabled () {
        // 处理单选
        if (this.resourceValue && this.hasSelectedValues.length) {
          return true;
        }
        return this.manualValue === '';
      }
    },
    methods: {
      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            let allTreeData = [...this.manualTableList];
            if (!allTreeData.length && !this.isOnlyLevel && this.curKeyword) {
              allTreeData = [...this.curTreeTableData.children || []];
            }
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            const curNode = allTreeData.find((item) => `${row.name}&${row.id}` === `${item.name}&${item.id}`);
            if (isChecked) {
              this.$set(row, 'checked', true);
              if (curNode) {
                this.currentSelectedNode.push(curNode);
                this.$emit('on-select', true, curNode);
              }
            } else {
              this.currentSelectedNode = this.currentSelectedNode.filter(
                (item) => `${item.name}&${item.id}` !== `${row.name}&${row.id}`
              );
              this.$set(row, 'checked', false);
              if (curNode) {
                this.$emit('on-select', false, curNode);
              }
            }
            this.$store.commit('setTreeSelectedNode', this.currentSelectedNode);
          },
          all: () => {
            // 针对资源权限搜索单选特殊处理
            const resourceList = this.resourceValue ? [...payload].slice(0, 1) : [...payload];
            let allTreeData = [...this.allTreeData];
            if (!allTreeData.length && !this.isOnlyLevel && this.curKeyword) {
              allTreeData = [...this.curTreeTableData.children || []];
            }
            const tableIdList = cloneDeep(this.renderTopologyData.map((v) => `${v.name}&${v.id}`));
            const selectNode = this.currentSelectedNode.filter(
              (item) => !tableIdList.includes(`${item.name}&${item.id}`)
            );
            this.currentSelectedNode = [...selectNode, ...resourceList];
            const currentSelect = allTreeData.filter(
              (item) => resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`) && !item.disabled
            );
            // 如果currentSelect有内容， 代表当前是勾选，否则就取从总数据里取当前页不是disabled的数据
            let noDisabledData = [];
            if (this.resourceValue) {
              // 处理单选业务
              const defaultSelectList = this.curSelectedValues
                .filter((item) => !item.disabled)
                .map((v) => v.ids).flat(this.curChain.length);
              noDisabledData = allTreeData.filter(
                (item) => defaultSelectList.includes(`${item.id}&${this.curChain[item.level].id}`)
              );
            } else {
              noDisabledData = allTreeData.filter(
                (item) =>
                  !resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
                  && this.renderTopologyData.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
              );
            }
            const nodes = currentSelect.length ? currentSelect : noDisabledData;
            this.renderTopologyData.forEach((item) => {
              if (!item.disabled) {
                this.$set(item, 'checked', resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`));
                if (resourceList.length && !currentSelect.length) {
                  this.$set(
                    item,
                    'disabled',
                    resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
                  );
                }
                this.$refs.topologyTableRef && this.$refs.topologyTableRef.toggleRowSelection(item, item.checked);
              }
            });
            this.$store.commit('setTreeSelectedNode', this.currentSelectedNode);
            this.$emit('on-select-all', nodes, currentSelect.length > 0);
          }
        };
        return typeMap[type]();
      },

      fetchManualTableData () {
        this.$nextTick(() => {
          this.manualTableList.forEach((item) => {
            if (this.$refs.manualTableRef) {
              const hasSelectedInstances = [...this.hasSelectedInstances].map((v) => `${v.id}${v.display_name}`);
              this.$refs.manualTableRef.toggleRowSelection(
                item,
                (hasSelectedInstances.includes(`${item.id}${item.display_name}`))
              );
            }
          });
        });
      },

      handleSelectChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleSelectAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleTableSearch () {
        this.emptyTableData.tipType = 'search';
        this.manualTableList = this.manualTableListStorage.filter((item) => {
          return item.display_name.indexOf(this.tableKeyWord) > -1;
        });
        if (!this.manualTableList.length) {
          this.emptyTableData = formatCodeData(0, this.emptyTableData, true);
        }
        this.fetchManualTableData();
      },

      handleClearSearch () {
        this.tableKeyWord = '';
        this.manualTableList = cloneDeep(this.manualTableListStorage);
        if (!this.manualTableList.length) {
          this.emptyTableData = Object.assign({}, {
            type: 'empty',
            text: '请先从左侧输入并解析',
            tip: '',
            tipType: ''
          });
          return;
        }
        this.fetchManualTableData();
      },

      handleManualInput (value) {
        if (value.trim()) {
          this.manualInputError = false;
        }
      },

      handleClearManualInput () {
        this.manualValue = '';
        this.manualInputError = false;
      },

      async handleAddManualUser () {
        this.manualAddLoading = true;
        try {
          const { system_id, action_id, resource_type_system, resource_type_id } = this.systemParams;
          const params = {
            type: resource_type_id,
            system_id,
            action_id,
            action_system_id: resource_type_system,
            display_names: this.manualValue.split(this.regValue)
          };
          const { code, data } = await this.$store.dispatch('permApply/getResourceInstanceManual', params);
          const list = data.results.filter((item) => {
            return !this.hasSelectedInstances.map((v) => `${v.id}${v.display_name}`).includes(`${item.id}${item.display_name}`);
          });
          this.manualTableListStorage = data.results.filter((item) => {
            return !this.manualTableList.map((v) => `${v.id}${v.display_name}`).includes(`${item.id}${item.display_name}`);
          });
          this.manualTableList = cloneDeep(this.manualTableListStorage);
          this.hasSelectedInstances.push(...list);
          this.emptyTableData = formatCodeData(code, this.emptyTableData);
        } catch (e) {
          this.manualTableList = [];
          this.emptyTableData = formatCodeData(e.code, this.emptyTableData);
          this.messageAdvancedError(e);
        } finally {
          this.manualAddLoading = false;
        }
      },

      getDefaultSelect () {
        return this.manualTableList.length > 0;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.manual-wrapper {
    display: flex;
    padding: 20px 0;
    min-height: 450px;

    &-left {
      min-width: 300px;
      padding-left: 24px;
      padding-right: 10px;

        .manual-error-text {
          width: 248px;
          margin-top: 4px;
          font-size: 12px;
          color: #ff4d4d;
          line-height: 14px;
        }

        .manual-bottom-btn {
          margin-top: 10px;
        }
    }

    &-right {
        width: calc(100% - 320px);
        .manual-input-wrapper {
          width: 100%;
          margin-bottom: 10px;
        }
        .manual-table-wrapper {
          height: 360px;
          border: none;
        }
    }
}

/deep/ .manual-textarea {
  width: 248px;
  .bk-textarea-wrapper {
    .bk-form-textarea {
      min-height: 360px;
      &::-webkit-scrollbar {
        width: 6px;
        background-color: lighten(transparent, 80%);
      }
      &::-webkit-scrollbar-thumb {
        height: 5px;
        border-radius: 2px;
        background-color: #e6e9ea;
      }
    }
  }
}
</style>

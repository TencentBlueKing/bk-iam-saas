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
        :disabled="isInputDisabled"
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
          :max-height="360"
          :outer-border="false"
          :header-border="false"
          @select="handleSelectChange"
          @select-all="handleSelectAllChange">

          <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
          <bk-table-column :label="$t(`m.common['实例名称']`)" prop="name">
            <template slot-scope="{ row }">
              <span :title="row.name">
                {{ row.name }}
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
              @on-refresh="handleClearSearch"
            />
          </template>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { guid, formatCodeData } from '@/common/util';
  import { bus } from '@/common/bus';

  class Node {
    constructor (payload, level = 0, isAsync = true, type = 'node') {
      this.disabled = payload.disabled || false;
      this.checked = payload.checked || false;
      this.expanded = false;
      this.loading = false;
      this.loadingMore = false;
      this.current = payload.current || 0;
      this.totalPage = payload.totalPage || 0;
      this.id = payload.id;
      this.name = payload.name || payload.display_name || '';
      this.parentId = level > 0 ? payload.parentId : '';
      this.parentSyncId = level > 0 ? payload.parentSyncId : '';
      this.level = level;
      this.nodeId = guid();
      this.async = isAsync;
      this.children = [];
      this.parentChain = payload.parentChain || [];
      this.type = type;
      this.childType = payload.child_type || '';
      this.isRemote = payload.isRemote || false;
      this.isFilter = payload.isFilter || false;
      this.placeholder = payload.placeholder || '';
      // 是否存在未带下一级的无限制数据
      this.isExistNoCarryLimit = payload.isExistNoCarryLimit || false;
      this.initVisible(payload);
    }
    initVisible (payload) {
      if (payload.hasOwnProperty('visiable')) {
        this.visiable = payload.visiable;
        return;
      }
      this.visiable = true;
    }
  }

  export default {
    props: {
      resourceValue: {
        type: Boolean,
        default: false
      },
      selectionMode: {
        type: String
      },
      curSelectedChain: {
        type: Object
      },
      systemParams: {
        type: Object
      },
      hasSelectedValues: {
        type: Array,
        default: () => []
      },
      curChain: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        tableKeyWord: '',
        manualValue: '',
        regValue: /，|,|；|;|、|\\|\n|\s/,
        manualAddLoading: false,
        manualInputError: false,
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
        manualTableList: [],
        manualTableListStorage: [],
        hasSelectedInstances: [],
        curSelectedValues: []
      };
    },
    computed: {
      isManualDisabled () {
        // 处理单选
        if (this.resourceValue && this.hasSelectedValues.length) {
          return true;
        }
        return this.manualValue.split(this.regValue).filter(item => item !== '').length === 0;
      },
      isInputDisabled () {
        return this.resourceValue && this.hasSelectedValues.length;
      }
    },
    watch: {
      hasSelectedValues: {
        handler (value) {
          this.curSelectedValues = [...value];
        },
        immediate: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('update-manualInput-toggleRowSelection');
      });
      bus.$on('update-manualInput-toggleRowSelection', ({ isChecked, idChain }) => {
        this.$nextTick(() => {
          const curId = idChain.substring(0, idChain.indexOf('&'));
          this.manualTableList.forEach((item) => {
            if (String(item.id) === String(curId)) {
              this.$refs.manualTableRef.toggleRowSelection(item, isChecked);
            }
            if (!isChecked) {
              this.curSelectedValues = this.curSelectedValues.filter((v) => String(item.id) !== String(curId));
            }
          });
        });
      });
    },
    methods: {
      evil (fn) {
        const Fn = Function;
        return new Fn('return ' + fn)();
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            const curNode = this.manualTableList.find((item) => `${row.name}&${row.id}` === `${item.name}&${item.id}`);
            if (isChecked) {
              this.$set(row, 'checked', true);
              if (curNode) {
                this.curSelectedValues.push(curNode);
                this.$emit('on-select', true, curNode);
              }
            } else {
              this.curSelectedValues = this.curSelectedValues.filter(
                (item) => `${item.name}&${item.id}` !== `${row.name}&${row.id}`
              );
              this.$set(row, 'checked', false);
              if (curNode) {
                this.$emit('on-select', false, curNode);
              }
            }
          },
          all: () => {
            // 针对资源权限搜索单选特殊处理
            const resourceList = this.resourceValue ? [...payload].slice(0, 1) : [...payload];
            const allTreeData = [...this.manualTableList];
            const tableIdList = cloneDeep(this.manualTableList.map((v) => `${v.name}&${v.id}`));
            const selectNode = this.curSelectedValues.filter(
              (item) => !tableIdList.includes(`${item.name}&${item.id}`)
            );
            this.curSelectedValues = [...selectNode, ...resourceList];
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
                  && this.manualTableList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
              );
            }
            const nodes = currentSelect.length ? currentSelect : noDisabledData;
            this.manualTableList.forEach((item) => {
              if (!item.disabled) {
                this.$set(item, 'checked', resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`));
                if (resourceList.length && !currentSelect.length) {
                  this.$set(
                    item,
                    'disabled',
                    resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
                  );
                }
                this.$refs.manualTableRef && this.$refs.manualTableRef.toggleRowSelection(item, item.checked);
              }
            });
            this.$emit('on-select-all', nodes, currentSelect.length > 0);
          }
        };
        return typeMap[type]();
      },

      fetchManualTableData () {
        this.$nextTick(() => {
          this.manualTableList.forEach((item) => {
            if (this.$refs.manualTableRef) {
              const hasSelectedInstances = [...this.hasSelectedInstances].map((v) => `${v.id}${v.name}`);
              this.$refs.manualTableRef.toggleRowSelection(
                item,
                (hasSelectedInstances.includes(`${item.id}${item.name}`))
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
          return item.name.indexOf(this.tableKeyWord) > -1;
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

      getUsername (str) {
        const array = str.split('');
        const index = array.findIndex((item) => item === '(');
        if (index !== -1) {
          return array.splice(0, index).join('');
        }
        return str;
      },

      async handleAddManualUser () {
        this.manualAddLoading = true;
        try {
          const { system_id, action_id, resource_type_system, type } = this.systemParams;
          const nameList = this.manualValue.split(this.regValue).filter(item => item !== '');
          const params = {
            type,
            system_id,
            action_id,
            action_system_id: resource_type_system,
            display_names: nameList.map((item) => {
              return this.getUsername(item);
            })
          };
          const { code, data } = await this.$store.dispatch('permApply/getResourceInstanceManual', params);
          const isAsync = this.curChain.length > 1;
          const results = data.results || [];
          if (results.length) {
            const usernameList = results.map((item) => item.display_name);
            // 保存原有格式
            let formatStr = cloneDeep(this.manualValue);
            usernameList.forEach((item) => {
              formatStr = formatStr
                .replace(this.evil('/' + item + '(，|,|；|;|、|\\||\\n|\\s\\n|)/'), '')
                .replace(/(\s*\r?\n\s*)+/g, '\n')
                .replace(';;', '');
              formatStr = formatStr
                .split(this.regValue)
                .filter((item) => item !== '')
                .join('\n');
            });
            if (formatStr === '\n' || formatStr === '\s' || formatStr === ';') {
              formatStr = '';
            }
            console.log(formatStr);
            this.manualValue = cloneDeep(formatStr);
            const list = results.map(item => {
              let checked = false;
              let disabled = false;
              let isRemote = false;
              let isExistNoCarryLimit = false;
              if (this.curSelectedValues.length) {
                let noCarryLimitData = {};
                let normalSelectedData = {};
                this.curSelectedValues.forEach(val => {
                  const curKey = `${item.id}&${params.type}`;
                  if (isAsync) {
                    const curIdChain = `${curKey}#*&${this.curChain[1].id}`;
                    if (val.idChain === curIdChain) {
                      normalSelectedData = val;
                    }
                    if (val.idChain === curKey) {
                      noCarryLimitData = val;
                    }
                  } else {
                    if (val.idChain === curKey) {
                      normalSelectedData = val;
                    }
                  }
                });
                isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
                if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                  isRemote = disabled;
                } else {
                  if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                    checked = true;
                    disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                    isRemote = disabled;
                  }
                }
              }
              const isAsyncFlag = isAsync || item.child_type !== '';
              return new Node({ ...item, checked, disabled, isRemote, isExistNoCarryLimit }, 0, isAsyncFlag);
            });
            const hasSelectedInstances = list.filter((item) => {
              return !this.hasSelectedInstances.map((v) => `${v.id}${v.name}`).includes(`${item.id}${item.name}`);
            });
            this.manualTableListStorage = [...list];
            this.manualTableList = cloneDeep(this.manualTableListStorage);
            this.hasSelectedInstances.push(...hasSelectedInstances);
            console.log(hasSelectedInstances);
            this.fetchManualTableData();
            this.$emit('on-select-all', hasSelectedInstances, true);
          }
          this.emptyTableData = formatCodeData(code, this.emptyTableData);
        } catch (e) {
          this.manualTableList = [];
          this.manualTableListStorage = [];
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

/deep/ .bk-table-pagination-wrapper {
  padding: 15px 0;
  .bk-page.bk-page-align-right {
    .bk-page-selection-count-left {
      display: none;
    }
  }
}
</style>

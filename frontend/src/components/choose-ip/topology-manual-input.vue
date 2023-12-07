<template>
  <div class="manual-wrapper">
    <div class="manual-wrapper-left">
      <bk-input
        ref="manualInputRef"
        type="textarea"
        class="manual-textarea"
        v-model="manualValue"
        :placeholder="$t(`m.common['请输入实例名称，以回车/分号/空格分割']`)"
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
          :pagination="pagination"
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
      }
    },
    data () {
      return {
        tableKeyWord: '',
        manualValue: '',
        manualAddLoading: false,
        manualInputError: false,
        manualTableList: [],
        manualTableListStorage: [],
        pagination: {
          current: 1,
          limit: 10,
          showTotalCount: true
        },
        emptyTableData: {
          type: 'empty',
          text: '请先从左侧输入并解析',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      isManualDisabled () {
        return this.manualValue === '';
      }
    },
    methods: {
      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: async () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (['depart', 'department'].includes(row.type)) {
              if (isChecked) {
                const hasSelectedDepart = [...this.hasSelectedDepartments, ...this.hasSelectedManualDepartments];
                let hasSelectedDepartIds = [];
                if (hasSelectedDepart.length) {
                  hasSelectedDepartIds = hasSelectedDepart.map((v) => String(v.id));
                }
                if (!hasSelectedDepartIds.includes(String(row.id))) {
                  this.hasSelectedDepartments.push(row);
                  this.hasSelectedManualDepartments.push(row);
                }
              } else {
                this.hasSelectedDepartments = this.hasSelectedDepartments.filter(
                  (item) => item.id.toString() !== row.id.toString()
                );
                this.hasSelectedManualDepartments = this.hasSelectedManualDepartments.filter(
                  (item) => item.id.toString() !== row.id.toString()
                );
              }
            }
            if (['user'].includes(row.type)) {
              if (isChecked) {
                const hasSelectedUsers = [...this.hasSelectedUsers, ...this.hasSelectedManualUsers];
                let hasSelectedUsersIds = [];
                if (hasSelectedUsers.length) {
                  hasSelectedUsersIds = hasSelectedUsers.map((v) => `${v.username}${v.name}`);
                }
                if (!hasSelectedUsersIds.includes(`${row.username}${row.name}`)) {
                  this.hasSelectedUsers.push(row);
                  this.hasSelectedManualUsers.push(row);
                }
              } else {
                this.hasSelectedUsers = this.hasSelectedUsers.filter(
                  (item) => `${item.username}${item.name}` !== `${row.username}${row.name}`
                );
                this.hasSelectedManualUsers = this.hasSelectedManualUsers.filter(
                  (item) => `${item.username}${item.name}` !== `${row.username}${row.name}`
                );
              }
            }
          },
          all: async () => {
            const isAllCheck = payload.length > 0;
            this.manualTableList.forEach((item) => {
              if (['depart', 'department'].includes(item.type)) {
                if (isAllCheck) {
                  const hasSelectedDepart = [...this.hasSelectedDepartments, ...this.hasSelectedManualDepartments];
                  let hasSelectedDepartIds = [];
                  if (hasSelectedDepart.length) {
                    hasSelectedDepartIds = hasSelectedDepart.map((v) => String(v.id));
                  }
                  if (!hasSelectedDepartIds.includes(String(item.id))) {
                    this.hasSelectedDepartments.push(item);
                    this.hasSelectedManualDepartments.push(item);
                  }
                } else {
                  this.hasSelectedDepartments = this.hasSelectedDepartments.filter(
                    (v) => item.id.toString() !== v.id.toString()
                  );
                  this.hasSelectedManualDepartments = this.hasSelectedManualDepartments.filter(
                    (v) => item.id.toString() !== v.id.toString()
                  );
                }
              }
              if (['user'].includes(item.type)) {
                if (isAllCheck) {
                  const hasSelectedUsers = [...this.hasSelectedUsers, ...this.hasSelectedManualUsers];
                  let hasSelectedUsersIds = [];
                  if (hasSelectedUsers.length) {
                    hasSelectedUsersIds = hasSelectedUsers.map((v) => `${v.username}${v.name}`);
                  }
                  if (!hasSelectedUsersIds.includes(`${item.username}${item.name}`)) {
                    this.hasSelectedUsers.push(item);
                    this.hasSelectedManualUsers.push(item);
                  }
                } else {
                  this.hasSelectedUsers = this.hasSelectedUsers.filter(
                    (v) => `${item.username}${item.name}` !== `${v.username}${v.name}`
                  );
                  this.hasSelectedManualUsers = this.hasSelectedManualUsers.filter(
                    (v) => `${item.username}${item.name}` !== `${v.username}${v.name}`
                  );
                }
              }
            });
          }
        };
        return typeMap[type]();
      },

      fetchManualTableData () {
        this.$nextTick(() => {
          // this.manualTableList.forEach((item) => {
          //   if (this.$refs.manualTableRef) {
          //     const hasSelectedUsers = [...this.hasSelectedUsers, ...this.hasSelectedManualUsers].map((v) => `${v.username}${v.name}`);
          //     const hasSelectedDepartments = [...this.hasSelectedDepartments, ...this.hasSelectedManualDepartments]
          //       .map((v) => String(v.id));
          //     this.$refs.manualTableRef.toggleRowSelection(
          //       item,
          //       (hasSelectedUsers.includes(`${item.username}${item.name}`))
          //         || (['depart', 'department'].includes(item.type) && hasSelectedDepartments.includes(String(item.id)))
          //     );
          //   }
          // });
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

      handleManualInput () {

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
            display_names: this.manualValue.split(/;|\n|\s/)
          };
          const { code, data } = await this.$store.dispatch('permApply/getResourceInstanceManual', params);
          this.pagination.count = data.count || 0;
          this.manualTableList = data.results || [];
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

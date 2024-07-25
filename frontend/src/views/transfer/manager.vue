<template>
  <div class="iam-transfer-manager-wrapper" v-bkloading="{ isLoading: managerPermData.loading, opacity: 1 }">
    <div class="transfer-manager-content" ref="transferManagerContent">
      <div class="content">
        <div class="slot-content">
          <bk-table
            ref="manageTableRef"
            size="small"
            :border="false"
            :header-border="false"
            :outer-border="false"
            :data="managerPermData.list"
            :pagination="managerPermData.pagination"
            :header-cell-class-name="getCellClass"
            :cell-class-name="getCellClass"
            @select="handleSelect"
            @select-all="handleSelectAll"
            @page-change="handlePageChange"
            @page-limit-change="handleLimitChange">
            <bk-table-column type="selection" align="center" />
            <bk-table-column :label="$t(`m.permTransfer['管理员名称']`)" width="300">
              <template slot-scope="{ row }">
                <span
                  v-bk-tooltips="{
                    content: row.name
                  }"
                >
                  {{row.name}}
                </span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['类型']`)" width="300">
              <template slot-scope="{ row }">
                {{ formatManagerType(row.type) }}
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)" width="300" :show-overflow-tooltip="true">
              <template slot-scope="{ row }">
                {{row.description || '--'}}
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.permTransfer['交接对象']`)" width="300">
              <template slot-scope="{ row }">
                <div class="transfer-object-column" v-if="row.handover_object && row.handover_object.length">
                  <Icon type="arrows-left" />
                  <IamEditMemberSelector
                    mode="detail"
                    field="role_members"
                    width="300"
                    :value="formatRoleMembers(row.handover_object)"
                    :index="$index"
                  />
                </div>
                <span>--</span>
              </template>
            </bk-table-column>
            <template slot="empty">
              <ExceptionEmpty
                :type="emptyData.type"
                :empty-text="emptyData.text"
                :tip-text="emptyData.tip"
                :tip-type="emptyData.tipType"
                @on-refresh="handleEmptyRefresh"
              />
            </template>
          </bk-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ALL_MANAGER_TYPE_ENUM } from '@/common/constants';
  export default {
    components: {
    },
    props: {
      curPermData: {
        type: Object
      },
      selectedHandoverObject: {
        type: Array,
        default: () => []
      },
      description: {
        type: String
      }
    },
    data () {
      return {
        isEmpty: false,
        isLoading: false,
        rateExpanded: true,
        managerShowAll: false,
        isSelectAllChecked: false,
        managerSelectData: [],
        managerPermData: {},
        pagination: {
          current: 1,
          limit: 10,
          count: 0
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      formatManagerType () {
        return (payload) => {
          const managerData = ALL_MANAGER_TYPE_ENUM.find((v) => v.value === payload);
          if (managerData) {
            return managerData.label;
          }
          return '';
        };
      }
    },
    watch: {
      curPermData: {
        handler (value) {
          this.managerPermData = { ...value };
          // this.handleGetCheckData();
        },
        deep: true
      },
      description: {
        handler (value) {
          this.managerPermData.list.forEach((item) => {
            this.$set(item, 'reason', value);
          });
        },
        deep: true
      },
      selectedHandoverObject: {
        handler (value) {
          this.managerSelectData.list.forEach((item) => {
            this.$set(item, 'handover_object', value);
          });
        },
        deep: true
      }
    },
    methods: {
      handleGetCheckData () {
        const selectGroup = this.managerSelectData.length ? this.managerSelectData.map(item => String(item.id)) : [];
        setTimeout(() => {
          this.managerPermData.list.forEach(item => {
            if (selectGroup.includes(String(item.id))) {
              this.$refs.manageTableRef && this.$refs.manageTableRef.toggleRowSelection(item, true);
            }
            if (this.managerSelectData.length < 1) {
              this.$refs.manageTableRef && this.$refs.manageTableRef.clearSelection();
            }
          });
        }, 0);
        this.fetchSelectedGroupCount();
      },

      fetchSelectedGroupCount () {
        setTimeout(() => {
          const paginationWrapper = this.$refs.manageTableRef.$refs.paginationWrapper;
          const selectCount = paginationWrapper.getElementsByClassName('bk-page-selection-count');
          if (selectCount.length && selectCount[0].children && selectCount[0].children.length) {
            selectCount[0].children[0].innerHTML = this.managerSelectData.length;
          }
        }, 0);
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.managerSelectData.push(row);
            } else {
              this.managerSelectData = this.managerSelectData.filter((item) => item.id !== row.id);
            }
            this.fetchSelectedGroupCount();
          },
          all: () => {
            const selectGroups = this.managerSelectData.filter((item) =>
              !this.managerList.map((v) => v.id).includes(item.id));
            this.managerSelectData = [...selectGroups, ...payload];
            this.fetchSelectedGroupCount();
          }
        };
        return typeMap[type]();
      },

      handleSelectAll (selection) {
        this.fetchSelectedGroups('all', selection);
        this.$emit('manager-selection-change', this.managerSelectData);
      },

      handleSelect (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
        this.$emit('manager-selection-change', this.managerSelectData);
      },

      handlePageChange (current) {
        const pagination = Object.assign(this.managerPermData.pagination, { current });
        this.$emit('on-page-change', pagination);
      },

      handleLimitChange (limit) {
        const pagination = Object.assign(this.managerPermData.pagination, { current: 1, limit });
        this.$emit('on-limit-change', pagination);
      },
      
      handleEmptyRefresh () {
        const pagination = Object.assign(this.managerPermData.pagination, { current: 1, limit: 10 });
        this.$emit('on-page-change', pagination);
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 0) {
          return 'checkbox-cell-wrapper';
        }
        return '';
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import './common/css/group.css';
</style>

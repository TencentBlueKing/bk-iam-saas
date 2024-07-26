<template>
  <div class="iam-transfer-manager-wrapper" v-bkloading="{ isLoading: managerPermData.loading, opacity: 1 }">
    <div class="transfer-manager-content" ref="transferManagerContent">
      <div class="content">
        <div class="slot-content">
          <bk-table
            size="small"
            :ref="`manageTableRef_${managerPermData.id}`"
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
            <bk-table-column :label="$t(`m.permTransfer['管理员名称']`)">
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
            <bk-table-column :label="$t(`m.common['类型']`)">
              <template slot-scope="{ row }">
                {{ formatManagerType(row.type) }}
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)" :show-overflow-tooltip="true">
              <template slot-scope="{ row }">
                {{row.description || '--'}}
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.permTransfer['交接对象']`)">
              <template slot-scope="{ row, $index }">
                <div class="transfer-object-column" v-if="row.handover_object && row.handover_object.length > 0">
                  <Icon type="arrows-left" />
                  <IamEditMemberSelector
                    mode="detail"
                    field="role_members"
                    width="300"
                    :value="formatRoleMembers(row.handover_object)"
                    :index="$index"
                  />
                </div>
                <span v-else>--</span>
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
  import { cloneDeep, uniqWith, isEqual } from 'lodash';
  import { ALL_MANAGER_TYPE_ENUM } from '@/common/constants';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  export default {
    components: {
      IamEditMemberSelector
    },
    props: {
      curPermData: {
        type: Object
      },
      selectedManagerGroup: {
        type: Array,
        default: () => []
      },
      selectedHandoverObject: {
        type: Array,
        default: () => []
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
      },
      formatRoleMembers () {
        return (payload) => {
          if (payload && payload.length) {
            const hasName = payload.some((v) => v.username);
            if (!hasName) {
              payload = payload.map(v => {
                return {
                  username: v,
                  readonly: false
                };
              });
            }
            return payload;
          }
          return payload || [];
        };
      }
    },
    watch: {
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
        this.managerPermData = cloneDeep(this.curPermData);
        const selectList = uniqWith([...this.selectedManagerGroup, ...this.managerSelectData], isEqual);
        const selectGroup = selectList.map((item) => `${item.name}&${item.id}`);
        setTimeout(() => {
          this.managerPermData.loading = false;
          console.log(this.selectedHandoverObject);
          const managerPermRef = this.$refs[`manageTableRef_${this.managerPermData.id}`];
          this.managerPermData.list.forEach((item) => {
            this.$set(item, 'handover_object', this.selectedHandoverObject);
            if (managerPermRef) {
              managerPermRef.toggleRowSelection(item, selectGroup.includes(`${item.name}&${item.id}`));
              if (selectGroup.length < 1) {
                managerPermRef.clearSelection();
              }
            }
          });
        }, 0);
        this.fetchSelectedGroupCount();
      },

      fetchSelectedGroupCount () {
        this.$nextTick(() => {
          const selectGroup = uniqWith([...this.selectedManagerGroup, ...this.managerSelectData], isEqual);
          const permRef = this.$refs[`manageTableRef_${this.managerPermData.id}`];
          if (permRef && permRef.$refs && permRef.$refs.paginationWrapper) {
            const paginationWrapper = permRef.$refs.paginationWrapper;
            const selectCount = paginationWrapper.getElementsByClassName('bk-page-selection-count');
            if (selectCount.length && selectCount[0].children && selectCount[0].children.length) {
              selectCount[0].children[0].innerHTML = selectGroup.length;
            }
          }
        });
      },

      fetchSelectedGroups (type, payload, row) {
        const selectList = uniqWith([...this.selectedManagerGroup, ...this.managerSelectData], isEqual);
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              selectList.push(row);
              this.managerSelectData = [...selectList];
            } else {
              this.managerSelectData = selectList.filter((item) => `${item.name}&${item.id}&${this.managerPermData.id}` !== `${row.name}&${row.id}&${this.managerPermData.id}`);
            }
            this.$emit('manager-selection-change', this.managerSelectData);
            this.fetchSelectedGroupCount();
          },
          all: () => {
            const tableList = this.managerPermData.list.map((v) => `${v.name}&${v.id}&${this.managerPermData.id}`);
            const selectGroups = selectList.filter((item) => !tableList.includes(`${item.name}&${item.id}&${this.managerPermData.id}`));
            this.managerSelectData = [...selectGroups, ...payload];
            this.$emit('manager-selection-change', this.managerSelectData);
            this.fetchSelectedGroupCount();
          }
        };
        return typeMap[type]();
      },

      handleSelectAll (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleSelect (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
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

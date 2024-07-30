<template>
  <div
    class="iam-transfer-group-wrapper"
    v-bkloading="{ isLoading: groupPermData.loading, opacity: 1 }"
  >
    <div class="transfer-group-content" ref="transferGroupContent">
      <div class="content">
        <div
          :class="[
            'slot-content',
            { 'set-top-border': groupNotTransferCount > 0 }
          ]"
        >
          <bk-table
            size="small"
            :ref="`groupTableRef_${groupPermData.id}`"
            :border="false"
            :header-border="false"
            :outer-border="false"
            :data="groupPermData.list"
            :pagination="groupPermData.pagination"
            :header-cell-class-name="getCellClass"
            :cell-class-name="getCellClass"
            @select="handleSelect"
            @select-all="handleSelectAll"
            @page-change="handlePageChange"
            @page-limit-change="handleLimitChange"
          >
            <bk-table-column type="selection" align="center" :selectable="(row) => !row.canNotTransfer" />
            <bk-table-column :label="$t(`m.userGroup['用户组名']`)" :min-width="300" fixed="left">
              <template slot-scope="{ row }">
                <div class="perm-group-name">
                  <span
                    v-bk-tooltips="{
                      content: row.name
                    }"
                    :class="[
                      'can-view single-hide',
                      { 'has-icon': row.canNotTransfer }
                    ]"
                    @click.stop="handleViewDetail(row)"
                  >
                    {{ row.name }}
                  </span>
                  <i
                    v-if="row.canNotTransfer"
                    v-bk-tooltips="{
                      content: $t(`m.permTransfer['（通过组织加入、已过期的组无法交接）']`)
                    }"
                    class="iam-icon iamcenter-warning-fill not-transfer-icon"
                  />
                </div>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)" width="220" :show-overflow-tooltip="true">
              <template slot-scope="{ row }">
                <span>{{row.description}}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.grading['管理空间']`)" width="300">
              <template slot-scope="{ row }">
                <span
                  :style="{ color: row.canNotTransfer ? '#c4c6cc' : '' }"
                  v-bk-tooltips="{
                    content: row.role.name,
                    disabled: !row.role.name
                  }"
                >
                  {{ row.role ? row.role.name : '--' }}
                </span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['管理员']`)" width="300">
              <template slot-scope="{ row, $index }">
                <IamEditMemberSelector
                  mode="detail"
                  field="role_members"
                  width="300"
                  :placeholder="$t(`m.verify['请输入']`)"
                  :value="formatRoleMembers(row.role_members)"
                  :index="$index"
                />
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['有效期']`)" width="220">
              <template slot-scope="{ row }">
                <span>{{ row.expired_at_display }}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.permTransfer['交接对象']`)" width="300">
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
        <!-- <p class="expand-action" @click="handleGroupShowAll" v-if="groupList.length > 5">
            <Icon :type="groupShowAll ? 'up-angle' : 'down-angle'" />
            <template v-if="!groupShowAll">{{ $t(`m.common['点击展开']`) }}</template>
            <template v-else>{{ $t(`m.common['点击收起']`) }}</template>
          </p> -->
      </div>
    </div>
    
    <RenderGroupPermSideSlider
      :show="isShowPermSideSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd"
    />
  </div>
</template>

<script>
  import { cloneDeep, uniqWith, isEqual } from 'lodash';
  import { bus } from '@/common/bus';
  import { getNowTimeExpired } from '@/common/util';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import RenderGroupPermSideSlider from '@/views/my-perm/components/render-group-perm-side-slider';
  export default {
    components: {
      IamEditMemberSelector,
      RenderGroupPermSideSlider
    },
    props: {
      curPermData: {
        type: Object
      },
      selectedPersonalGroup: {
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
        groupExpanded: true,
        groupShowAll: false,
        isSelectAllChecked: false,
        isShowPermSideSlider: false,
        curGroupName: '',
        curGroupId: '',
        groupSelectData: [],
        groupNotTransferCount: 0,
        groupPermData: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
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
          this.groupPermData.list.forEach((item) => {
            this.$set(item, 'handover_object', value);
          });
        },
        deep: true
      }
    },
    methods: {
      handleGetCheckData () {
        this.groupPermData = cloneDeep(this.curPermData);
        const selectList = uniqWith(
          [
            ...this.selectedPersonalGroup,
            ...this.groupSelectData
          ],
          isEqual
        );
        const selectGroup = selectList.map((item) => `${item.name}&${item.id}`);
        this.$nextTick(() => {
          this.groupPermData.loading = false;
          this.groupPermData.list.forEach((item) => {
            if (String(item.department_id) !== '0' || item.expired_at < getNowTimeExpired()) {
              item.canNotTransfer = true;
            }
            this.$set(item, 'handover_object', this.selectedHandoverObject);
            const groupPermRef = this.$refs[`groupTableRef_${this.groupPermData.id}`];
            if (groupPermRef) {
              groupPermRef.toggleRowSelection(item, selectGroup.includes(`${item.name}&${item.id}`));
              if (selectGroup.length < 1) {
                groupPermRef.clearSelection();
              }
            }
          });
          this.fetchSelectedGroupCount();
        });
      },

      handleViewDetail ({ id, name, template_name, template_id }) {
        this.curGroupName = name;
        this.curGroupId = id;
        this.isShowPermSideSlider = true;
        bus.$emit('on-drawer-side', { width: 960 });
      },

      fetchSelectedGroupCount () {
        this.$nextTick(() => {
          const selectGroup = uniqWith([...this.selectedPersonalGroup, ...this.groupSelectData], isEqual);
          const permRef = this.$refs[`groupTableRef_${this.groupPermData.id}`];
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
        const selectList = uniqWith([...this.selectedPersonalGroup, ...this.groupSelectData], isEqual);
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              selectList.push(row);
              this.groupSelectData = [...selectList];
            } else {
              this.groupSelectData = selectList.filter((item) => `${item.name}&${item.id}` !== `${row.name}&${row.id}`);
            }
            this.$emit('group-selection-change', this.groupSelectData);
            this.fetchSelectedGroupCount();
          },
          all: () => {
            const tableList = this.groupPermData.list.filter((item) => !item.canNotTransfer).map((v) => `${v.name}&${v.id}`);
            const selectGroups = selectList.filter((item) => !tableList.includes(`${item.name}&${item.id}`));
            this.groupSelectData = [...selectGroups, ...payload];
            this.$emit('group-selection-change', this.groupSelectData);
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
        const pagination = Object.assign(this.groupPermData.pagination, { current });
        this.$emit('on-page-change', pagination);
      },

      handleLimitChange (limit) {
        const pagination = Object.assign(this.groupPermData.pagination, { current: 1, limit });
        this.$emit('on-limit-change', pagination);
      },
      
      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSideSlider = false;
      },
      
      handleEmptyRefresh () {
        const pagination = Object.assign(this.groupPermData.pagination, { current: 1, limit: 10 });
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

<style lang="postcss">
@import './common/css/group.css';
</style>

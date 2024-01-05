<template>
  <div class="my-perm-group-perm">
    <bk-table
      ref="groupMemberRef"
      size="small"
      ext-cls="user-org-perm-table"
      :data="list"
      :outer-border="false"
      :header-border="false"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: isLoading, opacity: 1 }"
    >
      <bk-table-column
        v-if="['personalOrDepartPerm'].includes(mode)"
        type="selection"
        align="center"
        :selectable="getDefaultSelect"
      />
      <template v-for="item in tableProps">
        <template v-if="item.prop === 'name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <div class="can-view-name" @click.stop="handleOpenTag(row, 'userGroupDetail')">
                {{ row.name || "--" }}
              </div>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'created_time'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span :title="row.created_time.replace(/T/, ' ')">
                {{ row.created_time.replace(/T/, " ") }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'join_type'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span>{{ formatJoinType(row) }}</span>
              <span
                v-if="row.template_id > 0 || row.department_id > 0"
                v-bk-tooltips="{ content: formatJoinTypeTip(row), disabled: !formatJoinTypeTip(row) }"
                class="can-view-name"
                @click.stop="handleOpenTag(row, row.template_id > 0 ? 'memberTemplate' : 'userGroupDetail')"
              >
                ({{ row.template_name || row.department_name}})
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'operate'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="'auto'">
            <template slot-scope="{ row }">
              <template>
                <bk-button
                  text
                  theme="primary"
                  @click="handleDelete(row)"
                >
                  {{ $t(`m.common['移除']`) }}
                </bk-button>
                <bk-button
                  v-if="row.expired_at !== PERMANENT_TIMESTAMP"
                  theme="primary"
                  style="margin-left: 5px;"
                  text
                  @click="handleShowRenewal(row)"
                >
                  {{ $t(`m.renewal['续期']`) }}
                </bk-button>
              </template>
            </template>
          </bk-table-column>
        </template>
        <template v-else>
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
          >
            <template slot-scope="{ row }">
              <span :title="row[item.prop] || ''">{{ row[item.prop] || '--'}}</span>
            </template>
          </bk-table-column>
        </template>
      </template>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>
  
    <!-- <RenderGroupPermSideSlider
      :show="isShowPermSideSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd"
    /> -->
  </div>
</template>
  
  <script>
  import { cloneDeep } from 'lodash';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  // import RenderGroupPermSideSlider from '../components/render-group-perm-sideslider';
  export default {
    components: {
      // RenderGroupPermSideSlider
    },
    props: {
      mode: {
        type: String
      },
      isLoading: {
        type: Boolean,
        default: false
      },
      list: {
        type: Array,
        default: () => []
      },
      pagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            limit: 10,
            count: 0,
            showTotalCount: true
          };
        }
      },
      groupData: {
        type: Object
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: '',
            text: '',
            tip: '',
            tipType: ''
          };
        }
      }
    },
    data () {
      return {
        PERMANENT_TIMESTAMP,
        isShowPermSideSlider: false,
        tabActive: 'userOrOrg',
        curGroupName: '',
        curGroupId: '',
        tableProps: [],
        currentSelectList: [],
        tableEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      formatJoinType () {
        return (payload) => {
          if (payload.template_id) {
            return this.$t(`m.userOrOrg['通过人员模板']`);
          }
          if (payload.department_id) {
            return this.$t(`m.userOrOrg['通过组织']`);
          }
          return this.$t(`m.perm['直接加入']`);
        };
      },
      formatJoinTypeTip () {
        return (payload) => {
          if (payload.template_id) {
            return this.$t(`m.userOrOrg['查看该组织的用户组详情页']`);
          }
          if (payload.department_id) {
            return this.$t(`m.userOrOrg['查看人员模板详情']`);
          }
          return '';
        };
      }
    },
    watch: {
      emptyData: {
        handler (value) {
          this.tableEmptyData = Object.assign({}, value);
        },
        immediate: true
      },
      mode: {
        handler (value) {
          this.tableProps = this.getTableProps(value);
        },
        immediate: true
      }
    },
    methods: {
      getTableProps (payload) {
        const tabMap = {
          personalOrDepartPerm: () => {
            const { type } = this.groupData;
            const typeMap = {
              user: () => {
                return [
                  { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
                  { label: this.$t(`m.common['描述']`), prop: 'description' },
                  { label: this.$t(`m.common['加入时间']`), prop: 'created_time' },
                  { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
                  { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
                ];
              },
              department: () => {
                return [
                  { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
                  { label: this.$t(`m.common['描述']`), prop: 'description' },
                  { label: this.$t(`m.common['加入时间']`), prop: 'created_time' },
                  { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
                  { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
                  { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
                ];
              }
            };
            return typeMap[type] ? typeMap[type]() : typeMap['user']();
          },
          departPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.common['加入时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' }
            ];
          }
        };
        return tabMap[payload] ? tabMap[payload]() : tabMap['personalOrDepartPerm']();
      },

      handleOpenTag ({ id }, type) {
        const routeMap = {
          userGroupDetail: () => {
            const routeData = this.$router.resolve({
              path: `user-group-detail/${id}`,
              query: {
                noFrom: true
              }
            });
            window.open(routeData.href, '_blank');
          },
          memberTemplate: () => {
            const routeData = this.$router.resolve({
              path: `member-template`,
              query: {
                template_name: '十点四十',
                tab_active: 'template_member'
              }
            });
            window.open(routeData.href, '_blank');
          }
        };
        return routeMap[type]();
      },

      handleDelete (payload) {
        
      },

      handleViewDetail ({ id, name }) {
        this.curGroupName = name;
        this.curGroupId = id;
        this.isShowPermSideSlider = true;
      },
        
      handlePageChange (page) {
        this.$emit('on-page-change', page);
      },
  
      handleLimitChange (limit) {
        this.$emit('on-limit-change', limit);
      },

      handlerAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handlerChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },
  
      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: async () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
            this.fetchCustomTotal();
          },
          all: async () => {
            const tableList = cloneDeep(this.list);
            const selectGroups = this.currentSelectList.filter(
              (item) => !tableList.map((v) => v.id.toString()).includes(item.id.toString())
            );
            this.currentSelectList = [...selectGroups, ...payload];
            this.fetchCustomTotal();
          }
        };
        return typeMap[type]();
      },
      
      fetchCustomTotal () {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.groupMemberRef && selectionCount && selectionCount.length) {
            selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
          }
        });
      },

      handleEmptyClear () {
        this.$emit('on-clear');
      },
  
      handleEmptyRefresh () {
        this.$emit('on-refresh');
      },
  
      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSideSlider = false;
      },

      getDefaultSelect () {
        return this.list.length > 0;
      }
    }
  };
  </script>
  
  <style lang="postcss" scoped>
  @import '@/views/user-org-perm/user-org-perm.css';
  </style>

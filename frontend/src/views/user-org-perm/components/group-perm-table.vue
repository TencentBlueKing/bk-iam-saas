<template>
  <div class="my-perm-group-perm">
    <bk-table
      ref="groupPermRef"
      size="small"
      ext-cls="user-org-perm-table"
      :data="list"
      :outer-border="false"
      :header-border="false"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handleChange"
      @select-all="handleAllChange"
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
            :prop="item.prop"
            :min-width="200"
            :fixed="'left'">
            <template slot-scope="{ row }">
              <span
                :ref="`name_${row.id}`"
                class="can-view-name"
                v-bk-tooltips="{
                  content: row.name,
                  placements: ['right-start']
                }"
                @click.stop="handleOpenTag(row, 'userGroupDetail')">
                {{ row.name || "--" }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'created_time'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="150">
            <template slot-scope="{ row }">
              <span>
                {{ row.created_time.replace(/T/, " ") }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'join_type'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="300">
            <template slot-scope="{ row }">
              <span
                v-bk-tooltips="{
                  content:
                    `${formatJoinType(row)}( ${row.template_name || row.department_name }
                  ${row.template_name && row.department_name ? ' - ' + row.department_name + ' )' : ' )'}`
                }"
              >
                {{ formatJoinType(row) }}
              </span>
              (<span
                v-if="row.template_id > 0 || row.department_id > 0"
                v-bk-tooltips="{ content: formatJoinTypeTip(row), disabled: !formatJoinTypeTip(row) }"
                class="can-view-name"
                @click.stop="handleOpenTag(row, row.template_id > 0 ? 'memberTemplate' : 'userOrgPerm')"
              >
                {{ row.template_name || row.department_name }}
              </span>
              <span
                v-if="row.template_name && row.department_name"
                v-bk-tooltips="{
                  content:
                    `${formatJoinType(row)}( ${row.template_name || row.department_name }
                  ${' - ' + row.department_name + ' )'}`
                }"
              >
                {{ ` - ${row.department_name}` }}
              </span>
              )
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'operate'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="150"
          >
            <template slot-scope="{ row }">
              <template>
                <bk-popconfirm
                  trigger="click"
                  placement="bottom-start"
                  ext-popover-cls="user-org-remove-confirm"
                  :confirm-text="$t(`m.userOrOrg['移出']`)"
                  @confirm="handleRemove(row)"
                >
                  <div slot="content">
                    <div class="popover-title">
                      <div class="popover-title-text">
                        {{ $t(`m.dialog['确认把用户/组织移出该用户组？']`) }}
                      </div>
                    </div>
                    <div class="popover-content">
                      <div class="popover-content-item">
                        <span class="popover-content-item-label">
                          {{ $t(`m.userOrOrg['操作对象']`) }}:
                        </span>
                        <span class="popover-content-item-value"> {{ formatUserName }}</span>
                      </div>
                      <div class="popover-content-item">
                        <span class="popover-content-item-label">
                          {{ $t(`m.userOrOrg['用户组名']`) }}:
                        </span>
                        <span class="popover-content-item-value"> {{ row.name }}</span>
                      </div>
                      <div class="popover-content-tip">
                        {{
                          $t(`m.userOrOrg['移出后，该用户/组织将不再继承该组的权限。']`)
                        }}
                      </div>
                    </div>
                  </div>
                  <bk-popover
                    placement="right"
                    :disabled="!formatAdminGroup(row)"
                    :content="$t(`m.perm['唯一管理员不可退出']`)"
                  >
                    <bk-button
                      theme="primary"
                      text
                      :disabled="formatAdminGroup(row)"
                    >
                      {{ $t(`m.userOrOrg['移出']`) }}
                    </bk-button>
                  </bk-popover>
                </bk-popconfirm>
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
            :min-width="['description'].includes(item.prop) ? 200 : 120"
          >
            <template slot-scope="{ row }">
              <span
                v-bk-tooltips="{
                  content: row[item.prop],
                  disabled: !row[item.prop] || ['created_time', 'expired_at_display'].includes(item.prop),
                  placements: ['right-start']
                }"
              >
                {{ row[item.prop] || '--'}}
              </span>
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

    <BatchOperateSlider
      :slider-width="960"
      :show.sync="isShowRenewalSlider"
      :is-batch="false"
      :cur-slider-name="curSliderName"
      :user-list="userList"
      :depart-list="departList"
      :title="$t(`m.renewal['续期']`)"
      :group-data="queryGroupData"
      :group-list="singleList"
      @on-submit="handleAddGroupSubmit"
    />

    <MemberTemplateDetailSlider :show.sync="isShowTempSlider" :cur-detail-data="tempDetailData" />
  </div>
</template>
  
  <script>
  import { cloneDeep } from 'lodash';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { bus } from '@/common/bus';
  import { xssFilter } from '@/common/util';
  import BatchOperateSlider from './batch-operate-slider.vue';
  import MemberTemplateDetailSlider from '@/views/member-template/components/member-template-detail-slider.vue';

  export default {
    components: {
      BatchOperateSlider,
      MemberTemplateDetailSlider
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
      curSelectedGroup: {
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
        isShowRenewalSlider: false,
        isShowTempSlider: false,
        tabActive: 'userOrOrg',
        renewalSliderTitle: '',
        curSliderName: '',
        tableProps: [],
        userList: [],
        departList: [],
        singleList: [],
        currentSelectList: [],
        queryGroupData: {},
        tempDetailData: {},
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
            return this.$t(`m.userOrOrg['查看人员模板详情']`);
          }
          if (payload.department_id) {
            return this.$t(`m.userOrOrg['查看该组织的用户组详情页']`);
          }
          return '';
        };
      },
      formatUserName () {
        const { id, name } = this.groupData;
        const typeMap = {
          user: () => {
            return `${id} (${name})`;
          },
          department: () => {
            return name;
          }
        };
        if (typeMap[this.groupData.type]) {
          return typeMap[this.groupData.type]();
        }
        return '';
      },
      formatAdminGroup () {
        return (payload) => {
          if (payload) {
            const { attributes, role_members } = payload;
            if (attributes && attributes.source_from_role && role_members.length === 1) {
              return true;
            }
            return false;
          }
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
      },
      groupData: {
        handler (value) {
          this.queryGroupData = cloneDeep(value);
        },
        immediate: true
      },
      curSelectedGroup: {
        handler (value) {
          this.currentSelectList = [...value];
        },
        deep: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-remove-toggle-checkbox');
        bus.$off('on-info-change');
      });
      // 同步更新checkbox状态
      bus.$on('on-remove-toggle-checkbox', (payload) => {
        this.$emit('on-selected-group', payload);
        this.$nextTick(() => {
          this.list.forEach((item) => {
            if (this.$refs.groupPermRef && !payload.map((v) => v.id).includes(item.id)) {
              this.$refs.groupPermRef.toggleRowSelection(item, false);
            }
          });
        });
      });
    },
    methods: {
      async fetchDetailInfo (id, name) {
        try {
          const { data } = await this.$store.dispatch('memberTemplate/subjectTemplateDetail', { id });
          const { readonly, group_count } = data;
          this.tempDetailData = {
            tabActive: 'template_member',
            mode: this.mode,
            id,
            name,
            readonly,
            group_count
          };
          this.isShowTempSlider = true;
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleRemove (payload) {
        const { type, id } = this.groupData;
        try {
          const params = {
            members: [{
              type,
              id
            }],
            group_ids: [payload.id]
          };
          const emitParams = {
            ...payload,
            ...{
              mode: this.mode
            }
          };
          await this.$store.dispatch('userOrOrg/deleteGroupMembers', params);
          this.messageSuccess(this.$t(`m.info['移出成功']`), 3000);
          this.$emit('on-remove-group', emitParams);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      getTableProps (payload) {
        const tabMap = {
          personalOrDepartPerm: () => {
            const { type } = this.queryGroupData;
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
          },
          userTempPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.common['加入时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' }
            ];
          },
          departTempPerm: () => {
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

      handleOpenTag ({ id, department_name, template_name, template_id }, type) {
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
          memberTemplate: async () => {
            await this.fetchDetailInfo(template_id, template_name);
          },
          userOrgPerm: () => {
            const routeData = this.$router.resolve({
              path: `user-org-perm`,
              query: {
                department_name
              }
            });
            window.open(routeData.href, '_blank');
          }
        };
        return routeMap[type]();
      },

      handleShowRenewal (payload) {
        this.curSliderName = 'renewal';
        this.handleGetMembers();
        this.renewalSliderTitle = this.$t(`m.common['续期']`);
        this.singleList = [payload];
        this.isShowRenewalSlider = true;
      },

      handleGetMembers () {
        const userList = [];
        const departList = [];
        const typeMap = {
          user: () => {
            userList.push(this.queryGroupData);
          },
          department: () => {
            departList.push(this.queryGroupData);
          }
        };
        typeMap[this.queryGroupData.type]();
        this.userList = [...userList];
        this.departList = [...departList];
      },

      handleAddGroupSubmit (payload) {
        const emitParams = {
          ...payload,
          ...{
            mode: this.mode
          }
        };
        this.$emit('on-add-group', emitParams);
      },
        
      handlePageChange (page) {
        this.$emit('on-page-change', page);
      },
  
      handleLimitChange (limit) {
        this.$emit('on-limit-change', limit);
      },

      handleAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },
  
      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: async () => {
            const hasData = {};
            const selectList = [...this.currentSelectList, ...this.curSelectedGroup].reduce((curr, next) => {
              // eslint-disable-next-line no-unused-expressions
              hasData[`${next.name}&${next.id}`] ? '' : hasData[`${next.name}&${next.id}`] = true && curr.push(next);
              return curr;
            }, []);
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              selectList.push(row);
              this.currentSelectList = [...selectList];
            } else {
              this.currentSelectList = selectList.filter((item) => String(item.id) !== String(row.id));
            }
            this.fetchCustomTotal(this.currentSelectList);
            this.$emit('on-selected-group', this.currentSelectList);
          },
          all: async () => {
            const tableList = cloneDeep(this.list);
            const hasData = {};
            const selectList = [...this.currentSelectList, ...this.curSelectedGroup].reduce((curr, next) => {
              // eslint-disable-next-line no-unused-expressions
              hasData[`${next.name}&${next.id}`] ? '' : hasData[`${next.name}&${next.id}`] = true && curr.push(next);
              return curr;
            }, []);
            const selectGroups = selectList.filter(
              (item) => !tableList.map((v) => String(v.id)).includes(String(item.id))
            );
            this.currentSelectList = [...selectGroups, ...payload];
            this.fetchCustomTotal(this.currentSelectList);
            this.$emit('on-selected-group', this.currentSelectList);
          }
        };
        return typeMap[type]();
      },
      
      fetchCustomTotal (payload) {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.groupPermRef && selectionCount && selectionCount.length && selectionCount[0].children) {
            selectionCount[0].children[0].innerHTML = xssFilter(payload.length);
          }
        });
      },

      handleEmptyClear () {
        this.$emit('on-clear');
      },
  
      handleEmptyRefresh () {
        this.$emit('on-refresh');
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

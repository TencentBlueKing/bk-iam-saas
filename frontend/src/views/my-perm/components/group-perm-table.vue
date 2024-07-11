<template>
  <div class="my-perm-group-perm">
    <bk-table
      ref="groupPermRef"
      size="small"
      ext-cls="user-org-perm-table my-perm-group-table"
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
            :fixed="'left'"
          >
            <template slot-scope="{ row }">
              <span
                :ref="`name_${row.id}`"
                :class="[
                  { 'can-view-name': isShowDetailEntry }
                ]"
                v-bk-tooltips="{
                  content: row.name,
                  placements: ['right-start']
                }"
                @click.stop="handleViewDetail(row, 'name')">
                {{ row.name || "--" }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'role.name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="200"
            :show-overflow-tooltip="true"
          >
            <template slot-scope="{ row }">
              <span class="role_name">{{ row.role ? row.role.name : '--' }}</span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'role_members'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="300"
          >
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
              <template v-if="row.template_id > 0">
                (<span
                  v-bk-tooltips="{ content: formatJoinTypeTip(row), disabled: !formatJoinTypeTip(row) }"
                  class="can-view-name"
                  @click.stop="handleViewDetail(row, 'memberTemplate')"
                >
                  {{ row.template_name }}
                </span>
                <span
                  v-if="row.template_name"
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
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'expired_at_display'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="120"
          >
            <template slot-scope="{ row }">
              <span
                :class="[
                  { 'is-expiring-soon': formatExpireSoon(row.expired_at) },
                  { 'is-expired': formatExpired(row.expired_at) }
                ]"
              >
                {{ row[item.prop] || '--'}}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'operate'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="formatOperate"
            :fixed="'right'"
          >
            <template slot-scope="{ row }">
              <bk-popconfirm
                v-if="['personalPerm'].includes(mode)"
                trigger="click"
                placement="bottom-start"
                ext-popover-cls="user-org-remove-confirm"
                :confirm-text="$t(`m.common['退出']`)"
                @confirm="handleOperate(row, 'quit')"
              >
                <div slot="content">
                  <div class="popover-title">
                    <div class="popover-title-text">
                      {{ $t(`m.dialog['确认退出该用户组？']`) }}
                    </div>
                  </div>
                  <div class="popover-content">
                    <div class="popover-content-item">
                      <span class="popover-content-item-label">
                        {{ $t(`m.userOrOrg['操作对象']`) }}:
                      </span>
                      <span class="popover-content-item-value"> {{ user.name }}</span>
                    </div>
                    <div class="popover-content-item">
                      <span class="popover-content-item-label">
                        {{ $t(`m.userOrOrg['用户组名']`) }}:
                      </span>
                      <span class="popover-content-item-value"> {{ row.name }}</span>
                    </div>
                    <div class="popover-content-tip">
                      {{
                        $t(`m.perm['退出后，将不再拥有该用户组的权限。']`)
                      }}
                    </div>
                  </div>
                </div>
                <bk-popover
                  placement="right"
                  :disabled="!(formatAdminGroup(row) || row.department_id > 0)"
                  :content="formatQuitContent(row)"
                >
                  <bk-button
                    theme="primary"
                    text
                    class="operate-btn"
                    :disabled="formatAdminGroup(row) || row.department_id > 0"
                  >
                    {{ $t(`m.common['退出']`) }}
                  </bk-button>
                </bk-popover>
              </bk-popconfirm>
              <bk-button
                v-if="isShowRenewal(row)"
                theme="primary"
                text
                class="operate-btn"
                @click="handleOperate(row, 'renewal')"
              >
                {{ $t(`m.renewal['续期']`) }}
              </bk-button>
              <bk-button
                v-if="isShowHandover"
                theme="primary"
                text
                class="operate-btn"
                @click="handleOperate(row, 'handover')"
              >
                {{ $t(`m.perm['交接']`) }}
              </bk-button>
            </template>
          </bk-table-column>
        </template>
        <template v-else>
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="['description'].includes(item.prop) ? 200 : 120"
            :show-overflow-tooltip="true"
          >
            <template slot-scope="{ row }">
              <span>
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

    <MemberTemplateDetailSlider :show.sync="isShowTempSlider" :cur-detail-data="tempDetailData" />

    <RenderGroupPermSideSlider
      :show="isShowPermSideSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd"
    />
  </div>
</template>
  
<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { bus } from '@/common/bus';
  import { getNowTimeExpired } from '@/common/util';
  // import BatchOperateSlider from './batch-operate-slider.vue';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import RenderGroupPermSideSlider from '../components/render-group-perm-sideslider';
  import MemberTemplateDetailSlider from '@/views/member-template/components/member-template-detail-slider.vue';

  export default {
    components: {
      IamEditMemberSelector,
      RenderGroupPermSideSlider,
      // BatchOperateSlider,
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
      isHasHandover: {
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
        isNoHandoverData: false,
        tabActive: 'userOrOrg',
        renewalSliderTitle: '',
        curSliderName: '',
        curGroupName: '',
        curGroupId: '',
        tableProps: [],
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
      ...mapGetters(['user']),
      isShowRenewal () {
        return (payload) => {
          return payload.expired_at !== PERMANENT_TIMESTAMP && ['personalPerm', 'customPerm'].includes(this.mode);
        };
      },
      isShowHandover () {
        return window.ENABLE_PERMISSION_HANDOVER.toLowerCase() === 'true' && this.isHasHandover;
      },
      isShowDetailEntry () {
        return !['customPerm', 'managerPerm'].includes(this.mode);
      },
      formatJoinType () {
        return (payload) => {
          if (payload.template_id) {
            return this.$t(`m.userOrOrg['通过人员模板']`);
          }
          if (payload.department_id) {
            return payload.department_name;
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
      },
      formatQuitContent () {
        return (payload) => {
          if (this.formatAdminGroup(payload)) {
            return this.$t(`m.perm['唯一管理员不可退出']`);
          }
          if (payload.department_id > 0) {
            return this.$t(`m.perm['通过组织加入的组无法退出']`);
          }
          return '';
        };
      },
      formatExpireSoon () {
        return (payload) => {
          const dif = payload - getNowTimeExpired();
          const days = Math.ceil(dif / (24 * 3600));
          return days < 6;
        };
      },
      formatExpired () {
        return (payload) => {
          return payload < getNowTimeExpired();
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
      },
      formatOperate () {
        const typeMap = {
          personalPerm: () => {
            return ['zh-cn'].includes(window.CUR_LANGUAGE) ? 150 : 200;
          },
          customPerm: () => {
            return ['zh-cn'].includes(window.CUR_LANGUAGE) ? 200 : 300;
          }
        };
        if (typeMap[this.mode]) {
          return typeMap[this.mode]();
        }
        return ['zh-cn'].includes(window.CUR_LANGUAGE) ? 80 : 100;
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

      handleOperate (payload, type) {
        const typeMap = {
          quit: async () => {
            try {
              const params = {
                type: 'group',
                id: payload.id
              };
              const emitParams = {
                ...params,
                ...{
                  mode: 'personalPerm'
                }
              };
              await this.$store.dispatch('perm/quitGroupPerm', params);
              this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
              this.$emit('on-quit-group', emitParams);
              this.currentSelectList = [];
            } catch (e) {
              this.messageAdvancedError(e);
            }
          },
          renewal: () => {
            
          },
          handover: () => {
            
          }
        };
        return typeMap[type]();
      },

      handleViewDetail ({ id, name, department_name, template_name, template_id }, type) {
        if (!this.isShowDetailEntry) {
          return;
        }
        const routeMap = {
          name: () => {
            this.curGroupName = name;
            this.curGroupId = id;
            this.isShowPermSideSlider = true;
          },
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
            selectionCount[0].children[0].innerHTML = payload.length;
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

      getTableProps (payload) {
        const tabMap = {
          personalPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.grading['管理空间']`), prop: 'role.name' },
              { label: this.$t(`m.levelSpace['管理员']`), prop: 'role_members' },
              { label: this.$t(`m.perm['加入用户组时间']`), prop: 'created_time' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          },
          departPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.grading['管理空间']`), prop: 'role.name' },
              { label: this.$t(`m.levelSpace['管理员']`), prop: 'role_members' },
              { label: this.$t(`m.perm['加入用户组时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['通过组织加入']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          },
          userTempPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.grading['管理空间']`), prop: 'role.name' },
              { label: this.$t(`m.levelSpace['管理员']`), prop: 'role_members' },
              { label: this.$t(`m.perm['加入用户组时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          },
          departTempPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.grading['管理空间']`), prop: 'role.name' },
              { label: this.$t(`m.levelSpace['管理员']`), prop: 'role_members' },
              { label: this.$t(`m.perm['加入用户组时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          },
          customPerm: () => {

          },
          managerPerm: () => {
            return [
              { label: this.$t(`m.permTransfer['管理员名称']`), prop: 'name' },
              { label: this.$t(`m.common['类型']`), prop: 'type' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          }
        };
        if (tabMap[payload]) {
          return tabMap[payload]();
        }
        return tabMap['personalPerm']();
      },

      getDefaultSelect () {
        return this.list.length > 0;
      }
    }
  };
</script>
  
<style lang="postcss" scoped>
@import '@/views/user-org-perm/user-org-perm.css';
/deep/ .my-perm-group-table {
  .operate-btn {
    margin-right: 8px;
  }
  .is-expired {
    background-color: #FFF1DB;
    color: #FE9C00;
    border-radius: 2px;
    padding: 4px 8px;
  }
  .is-expiring-soon {
    color: #FE9C00;
  }
  .bk-table-fixed,
  .bk-table-fixed-right {
    border-bottom: 0;
  }
}
</style>

<template>
  <div class="my-perm-group-perm" v-bkloading="{ isLoading: isLoading, opacity: 1 }">
    <bk-table
      ref="groupPermRef"
      size="small"
      :class="[
        'user-org-perm-table',
        { 'member-custom-perm-table': ['customPerm'].includes(mode) }
      ]"
      :data="list"
      :outer-border="false"
      :header-border="false"
      :cell-class-name="getCellClass"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handleChange"
      @select-all="handleAllChange"
    >
      <template v-for="item in tableProps">
        <template v-if="item.prop === 'selection'">
          <bk-table-column
            type="selection"
            align="center"
            :key="item.prop"
            :selectable="getDefaultSelect"
          />
        </template>
        <template v-else-if="item.prop === 'name'">
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
                class="can-view-name"
                v-bk-tooltips="{
                  content: row.name,
                  placements: ['right-start']
                }"
                @click.stop="handleOpenTag(row, 'userGroupDetail')"
              >
                {{ row.name || "--" }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'action_name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="160"
            :fixed="'left'"
          >
            <template slot-scope="{ row }">
              <span>
                {{ row.name }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'role_name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="150"
          >
            <template slot-scope="{ row }">
              <span>
                {{ row.role.name }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'created_time'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="150"
          >
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
            :min-width="curLanguageIsCn ? 200 : 300"
          >
            <template slot-scope="{ row }">
              <span
                v-bk-tooltips="{
                  content: `${formatJoinType(row)}( ${
                    row.template_name || row.department_name
                  }
                    ${
                    row.template_name && row.department_name
                      ? ' - ' + row.department_name + ' )'
                      : ' )'
                  }`
                }"
              >
                {{ formatJoinType(row) }}
              </span>
              (<span
                v-if="row.template_id > 0 || row.department_id > 0"
                v-bk-tooltips="{
                  content: formatJoinTypeTip(row),
                  disabled: !formatJoinTypeTip(row)
                }"
                class="can-view-name"
                @click.stop="
                  handleOpenTag(
                    row,
                    row.template_id > 0 ? 'memberTemplate' : 'userOrgPerm'
                  )
                "
              >
                {{ row.template_name || row.department_name }}
              </span>
              <span
                v-if="row.template_name && row.department_name"
                v-bk-tooltips="{
                  content: `${formatJoinType(row)}( ${
                    row.template_name || row.department_name
                  }
                    ${' - ' + row.department_name + ' )'}`
                }"
              >
                {{ ` - ${row.department_name}` }}
              </span>
              )
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'resource_instance'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
          >
            <template slot-scope="{ row }">
              <template v-if="!row.isEmpty">
                <div
                  v-for="(_, _index) in row.resource_groups"
                  :key="_.id"
                  class="related-resource-list"
                  :class="
                    row.resource_groups === 1 || _index === row.resource_groups.length - 1
                      ? ''
                      : 'related-resource-list-border'
                  "
                >
                  <p class="related-resource-item" v-for="related in _.related_resource_types" :key="related.type">
                    <render-resource-popover
                      :key="related.type"
                      :data="related.condition"
                      :value="`${related.name}: ${related.value}`"
                      :max-width="380"
                    />
                  </p>
                </div>
              </template>
              <template v-else>
                <span class="condition-table-cell empty-text">{{ $t(`m.common['无需关联实例']`) }}</span>
              </template>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'effective_conditions'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <div class="condition-table-cell" v-if="!!row.related_environments.length">
                <div
                  v-for="(_, groIndex) in row.resource_groups"
                  :key="_.id"
                  class="related-condition-list"
                  :class="[
                    row.resource_groups.length > 1 ? 'related-resource-list' : 'environ-group-one',
                    row.resource_groups === 1 || groIndex === row.resource_groups.length - 1
                      ? ''
                      : 'related-resource-list-border'
                  ]"
                >
                  <EffectCondition :value="_.environments" :is-empty="!_.environments.length" />
                  <Icon
                    v-if="isShowPreview(row)"
                    type="detail-new"
                    class="effect-detail-icon"
                    @click.stop="handleEnvironmentsViewResource(_, row)"
                  />
                </div>
              </div>
              <div v-else class="condition-table-cell empty-text">{{ $t(`m.common['无生效条件']`) }}</div>
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
                        <span class="popover-content-item-value">{{ formatUserName }}</span>
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
                    <bk-button theme="primary" text :disabled="formatAdminGroup(row)">
                      {{ $t(`m.userOrOrg['移出']`) }}
                    </bk-button>
                  </bk-popover>
                </bk-popconfirm>
              </template>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'custom_perm_operate'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="formateOperateWidth"
            :fixed="'right'"
          >
            <template slot-scope="{ row }">
              <div class="operate-column">
                <div v-if="isShowDeleteInstance" class="operate-column-btn">
                  <bk-popover
                    :content="$t(`m.userGroupDetail['暂无关联实例']`)"
                    :disabled="!row.isEmpty"
                  >
                    <bk-button
                      type="primary"
                      text
                      :disabled="row.isEmpty"
                      @click.stop="handleViewResource(row)"
                    >
                      {{ $t(`m.userGroupDetail['查看实例权限']`) }}
                    </bk-button>
                  </bk-popover>
                </div>
                <div v-if="isShowDeleteAction" class="operate-column-btn">
                  <bk-popconfirm
                    trigger="click"
                    ext-popover-cls="resource-perm-delete-confirm"
                    :ref="`memberDelActionConfirm_${row.id}`"
                    :width="280"
                    @confirm="handleDelete"
                  >
                    <div slot="content">
                      <div class="popover-title">
                        <div class="popover-title-text">
                          {{ formatDelConfirm(row, 'custom').title }}
                        </div>
                      </div>
                      <div class="popover-content">
                        <div class="popover-content-item">
                          <span class="popover-content-item-label">
                            {{ formatDelConfirm(row, 'custom').label }}{{ $t(`m.common['：']`)}}
                          </span>
                          <span class="popover-content-item-value"> {{ formatDelConfirm(row, 'custom').value }}</span>
                        </div>
                        <div class="popover-content-tip">
                          {{ formatDelConfirm(row, 'custom').tip }}
                        </div>
                        <div v-if="delActionList.length" class="popover-content-related">
                          <div class="delete-tips-title">
                            {{ delActionDialogTip }}
                          </div>
                          <div class="delete-tips-content">
                            <div
                              v-for="delAction in delActionList"
                              :key="delAction.id"
                              class="related-perm-name"
                            >
                              <Icon bk type="info-circle-shape" class="warn" />
                              {{ delAction.name }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <bk-button
                      type="primary"
                      text
                      @click.stop="handleDelActionOrInstance(row, 'action')"
                    >
                      {{ $t(`m.userGroupDetail['删除操作权限']`) }}
                    </bk-button>
                  </bk-popconfirm>
                </div>
              </div>
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
                  disabled:
                    !row[item.prop] ||
                    ['created_time', 'expired_at_display', 'expired_display'].includes(item.prop),
                  placements: ['right-start']
                }"
              >
                {{ row[item.prop] || "--" }}
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

    <MemberTemplateDetailSlider
      :show.sync="isShowTempSlider"
      :cur-detail-data="tempDetailData"
    />

    <bk-sideslider
      :is-show="isShowEnvironmentsSideSlider"
      :title="environmentsSideSliderTitle"
      :width="640"
      quick-close
      @update:isShow="handleResourceCancel"
      ext-cls="effect-condition-side"
    >
      <div slot="content">
        <EffectCondition
          :value="environmentsSideSliderData"
          :is-empty="!environmentsSideSliderData.length"
          @on-view="handleViewSideSliderCondition"
        />
      </div>
    </bk-sideslider>

    <!-- 生效时间编辑功能需要产品确认 暂时隐藏 -->
    <bk-sideslider
      :is-show="isShowResourceInstanceEffectTime"
      :title="environmentsSideSliderTitle"
      :width="640"
      quick-close
      @update:isShow="handleResourceEffectTimeCancel"
      :ext-cls="'relate-instance-sideslider'"
    >
      <div slot="content" class="sideslider-content">
        <SideSliderEffectCondition ref="sidesliderRef" :data="environmentsSideSliderData" />
      </div>
      <div slot="footer">
        <bk-button theme="primary" @click="handleResourceEffectTimeSubmit">
          {{ $t(`m.common['保存']`) }}
        </bk-button>
        <bk-button style="margin-left: 8px;" @click="handleResourceEffectTimeCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </bk-sideslider>

    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="sideSliderTitle"
      :width="sliderWidth"
      :quick-close="true"
      :before-close="handleBeforeClose"
      @update:isShow="handleResourceCancel"
    >
      <div slot="header" class="flex-between instance-detail-slider">
        <span class="single-hide instance-detail-slider-title">{{ sideSliderTitle }}</span>
        <div class="action-wrapper" v-if="isCanOperate">
          <bk-button
            v-if="isBatchDelete"
            text
            theme="primary"
            size="small"
            style="padding: 0"
            :disabled="batchDisabled"
            @click="handleBatchDelete"
          >
            {{ $t(`m.common['批量删除实例权限']`) }}
          </bk-button>
          <div v-else class="instance-detail-operate">
            <bk-popconfirm
              ext-popover-cls="instance-detail-operate-confirm"
              trigger="click"
              :disabled="disabled"
              :cancel-text="$t(`m.common['取消-dialog']`)"
              @confirm="handleDeleteInstances"
            >
              <div slot="content" class="popover-custom-content">
                {{ $t(`m.dialog['确认删除内容？']`, { value: $t(`m.dialog['删除实例权限']`) }) }}
              </div>
              <bk-button theme="primary" :disabled="disabled">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </bk-popconfirm>
            <bk-button class="cancel-delete-btn" @click="handleCancelDelete">
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </div>
        </div>
      </div>
      <div slot="content">
        <component
          ref="detailComRef"
          :is="'RenderDetailEdit'"
          :data="previewData"
          :can-edit="!isBatchDelete"
          @tab-change="handleTabChange"
          @on-change="handleInstanceChange"
          @on-select-all="handleInstanceAllChange"
        />
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { bus } from '@/common/bus';
  import { leaveConfirm } from '@/common/leave-confirm';
  import getActionsMixin from '../common/js/getActionsMixin';
  import EffectCondition from '@/views/perm/custom-perm/effect-conditon';
  import SideSliderEffectCondition from '@/views/perm/custom-perm/sideslider-effect-condition';
  import MemberTemplateDetailSlider from '@/views/member-template/components/member-template-detail-slider.vue';

  export default {
    components: {
      EffectCondition,
      SideSliderEffectCondition,
      MemberTemplateDetailSlider
    },
    mixins: [getActionsMixin],
    props: {
      mode: {
        type: String
      },
      isLoading: {
        type: Boolean,
        default: false
      },
      isShowDeleteInstance: {
        type: Boolean,
        default: true
      },
      isShowDeleteAction: {
        type: Boolean,
        default: true
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
        disabled: true,
        canOperate: true,
        batchDisabled: false,
        isSamePolicy: false,
        isBatchDelete: true,
        isShowSideSlider: false,
        isShowPermSideSlider: false,
        isShowRenewalSlider: false,
        isShowTempSlider: false,
        isShowEnvironmentsSideSlider: false,
        isShowPreviewDialog: false,
        isShowDeleteDialog: false,
        isShowResourceInstanceSideSlider: false,
        isShowResourceInstanceEffectTime: false,
        tabActive: 'userOrOrg',
        renewalSliderTitle: '',
        curSliderName: '',
        environmentsSideSliderTitle: this.$t(`m.common['生效条件']`),
        curId: '',
        curPolicyId: '',
        sideSliderTitle: '',
        previewDialogTitle: '',
        resourceInstanceSideSliderTitle: '',
        currentActionName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        curIndex: -1,
        curResIndex: -1,
        curGroupIndex: -1,
        tableList: [],
        previewData: [],
        delActionList: [],
        delPathList: [],
        policyIdList: [],
        customData: [],
        curInstancePaths: [],
        tableProps: [],
        userList: [],
        departList: [],
        currentSelectList: [],
        environmentsSideSliderData: [],
        params: {},
        previewResourceParams: {},
        curScopeAction: {},
        curCopyParams: {},
        newRow: {},
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
      isShowPreview () {
        return (payload) => {
          return !payload.isEmpty && payload.policy_id !== '';
        };
      },
      isCanOperate () {
        // 如果是资源权限管理操作查询不是同一个操作，则不能删除实例
        if (['resourcePermiss'].includes(this.$route.name)) {
          return this.isSamePolicy;
        }
        return this.canOperate;
      },
      sliderWidth () {
        return this.mode === 'detail' ? 960 : 640;
      },
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
        const { id, name, type } = this.queryGroupData;
        const typeMap = {
          user: () => {
            return `${id} (${name})`;
          },
          department: () => {
            return name;
          }
        };
        if (typeMap[type]) {
          return typeMap[type]();
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
      },
      formatDelConfirm () {
        return (payload, mode) => {
          let params = {};
          const { name } = payload;
          const typeMap = {
            template: () => {
              params = Object.assign({}, {
                title: this.$t(`m.dialog['确认移除该操作模板？']`),
                tip: this.$t(`m.resourcePermiss['移除后，用户组成员将失去操作模板对应的权限，请谨慎操作。']`),
                label: this.$t(`m.resourcePermiss['操作模板']`),
                value: name
              });
              return params;
            },
            custom: () => {
              params = Object.assign({}, {
                title: this.$t(`m.dialog['确认删除该操作权限？']`),
                tip: this.$t(`m.resourcePermiss['删除后，用户组成员将失去对应的自定义权限，请谨慎操作。']`),
                label: this.$t(`m.resourcePermiss['操作权限']`),
                value: name
              });
              return params;
            }
          };
          if (typeMap[mode]) {
            return typeMap[mode]();
          }
          return {};
        };
      },
      formateOperateWidth () {
        const langMap = {
          true: () => {
            if (this.isShowDeleteAction && this.isShowDeleteInstance) {
              return 200;
            }
            return 130;
          },
          false: () => {
            if (this.isShowDeleteAction && this.isShowDeleteInstance) {
              return 350;
            }
            return 192;
          }
        };
        if (langMap[this.curLanguageIsCn]) {
          return langMap[this.curLanguageIsCn]();
        }
        return 350;
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
          bus.$emit('on-drawer-side', { width: 1160 });
          this.isShowTempSlider = true;
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleRemove (payload) {
        const { type, id } = this.queryGroupData;
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
          this.messageAdvancedError(e);
        }
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

      handleDelete () {
        this.$emit('on-delete', this.newRow);
      },

      async handleDeleteInstances (payload) {
        const data = this.$refs.detailComRef.handleGetValue();
        const { ids, condition, type, resource_group_id } = data;
        const params = {
          id: this.curPolicyId,
          data: {
            system_id: data.system_id,
            type: type,
            ids,
            condition,
            resource_group_id
          }
        };
        try {
          await this.$store.dispatch('permApply/updatePerm', params);
          window.changeAlert = false;
          this.isShowSideSlider = false;
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.$emit('on-delete-instances');
          this.resetDataAfterClose();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          payload && payload.hide();
        }
      },

      // 处理操作和资源实例删除
      async handleDelActionOrInstance (payload, type) {
        const { id, name, condition } = payload;
        let delRelatedActions = [];
        this.delActionList = [];
        const isCustom = ['action', 'instance'].includes(type);
        const policyIdList = this.tableList.map(v => v.id);
        // 处理多系统展开时，只获取当前系统下的所有操作
        if (this.tableList.length > 0 && ['action'].includes(type)) {
          await this.fetchActions(this.tableList[0].detail);
        }
        const linearActionList = this.linearActionList.filter((item) => policyIdList.includes(item.id));
        const curAction = linearActionList.find(item => item.id === id);
        const hasRelatedActions = curAction && curAction.related_actions && curAction.related_actions.length;
        linearActionList.forEach(item => {
          // 如果这里过滤自己还能在其他数据找到相同的related_actions，就代表有其他数据也关联了相同的操作
          if (hasRelatedActions && item.related_actions && item.related_actions.length && item.id !== id) {
            delRelatedActions = item.related_actions.filter(v => curAction.related_actions.includes(v));
          }
          if (item.related_actions && item.related_actions.includes(id)) {
            this.delActionList.push(item);
          }
        });
        let policyIds = [payload.policy_id];
        if (this.delActionList.length) {
          const list = this.tableList.filter(
            item => this.delActionList.map(action => action.id).includes(item.id));
          policyIds = [payload.policy_id].concat(list.map(v => v.policy_id));
        }
        this.policyIdList = cloneDeep(policyIds);
        const typeMap = {
          action: () => {
            if (isCustom && !delRelatedActions.length && hasRelatedActions) {
              const list = [...this.tableList].filter((v) => curAction.related_actions.includes(v.id));
              if (list.length) {
                policyIds = policyIds.concat(list.map((v) => v.policy_id));
              }
            }
            this.delActionDialogTip = this.$t(`m.info['删除依赖操作产生的影响']`, {
              value: name
            });
            this.newRow = Object.assign(payload, { ids: policyIds });
            this.$nextTick(() => {
              console.log(this.$refs[`memberDelActionConfirm_${payload.id}`]);
              this.$refs[`memberDelActionConfirm_${payload.id}`]
                && this.$refs[`memberDelActionConfirm_${payload.id}`].length
                && this.$refs[`memberDelActionConfirm_${payload.id}`][0].$refs.popover
                && this.$refs[`memberDelActionConfirm_${payload.id}`][0].$refs.popover.showHandler();
            });
          },
          instance: () => {
            let curPaths = [];
            if (condition.length) {
              curPaths = condition.reduce((prev, next) => {
                prev.push(
                  ...next.instances.map(v => {
                    const paths = { ...v, ...next };
                    delete paths.instances;
                    return paths;
                  })
                );
                return prev;
              }, []);
              this.curInstancePaths = [...curPaths];
            }
          },
          groupInstance: () => {
            this.policyIdList = cloneDeep(policyIds);
            this.delActionDialogTitle = this.$t(`m.dialog['确认删除内容？']`, { value: this.$t(`m.dialog['删除一组实例权限']`) });
            this.delActionDialogTip = this.$t(`m.info['删除组依赖实例产生的影响']`, { value: this.currentActionName });
            this.isShowDeleteDialog = true;
          }
        };
        return typeMap[type]();
      },

      handleBeforeClose () {
        bus.$emit('on-drawer-side', { width: 960 });
        return true;
      },

      handleTabChange (payload) {
        const { disabled, canDelete } = payload;
        this.batchDisabled = disabled;
        this.canOperate = canDelete;
      },

      handleInstanceChange () {
        const data = this.$refs.detailComRef.handleGetValue();
        this.disabled = data.ids.length < 1 && data.condition.length < 1;
        if (!this.disabled) {
          this.handleDelActionOrInstance(Object.assign(data, {
            id: this.curId, policy_id: this.curPolicyId
          }), 'instance');
        }
      },

      handleInstanceAllChange (isAll, payload) {
        if (!isAll) {
          this.curInstancePaths = [];
          return;
        }
        const { instance } = payload;
        this.curInstancePaths = [...instance];
      },

      handleViewResource (payload) {
        const params = [];
        this.curId = payload.id;
        this.curPolicyId = payload.policy_id;
        // 如果不是同一个操作，则只有查看实例权限
        this.isSamePolicy = this.curId === this.queryGroupData.action_id;
        if (payload.resource_groups.length > 0) {
          payload.resource_groups.forEach((groupItem) => {
            if (groupItem.related_resource_types.length > 0) {
              groupItem.related_resource_types.forEach((sub) => {
                const { name, type, condition } = sub;
                params.push({
                  name: type,
                  tabType: 'resource',
                  label: this.$t(`m.info['tab操作实例']`, { value: name }),
                  data: condition,
                  systemId: sub.system_id,
                  resource_group_id: groupItem.id
                });
              });
            }
          });
        }
        this.previewData = cloneDeep(params);
        this.sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, {
          value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}`
        });
        if (this.previewData.length) {
          if (this.previewData[0].tabType === 'relate') {
            this.canOperate = false;
          }
          const noInstance = this.previewData[0].data.every((item) => !item.instance || item.instance.length < 1);
          if (this.previewData[0].tabType === 'resource' && (this.previewData[0].data.length < 1 || noInstance)) {
            this.batchDisabled = true;
          }
        }
        bus.$emit('on-drawer-side', { width: 1160 });
        this.isShowSideSlider = true;
      },

      handleEnvironmentsViewResource (payload, data) {
        this.environmentsSideSliderData = payload.environments || [];
        this.environmentsSideSliderTitle = this.$t(`m.info['关联侧边栏操作生效条件']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        this.isShowEnvironmentsSideSlider = true;
      },

      handleResourceEffectTimeSubmit () {
        const environments = this.$refs.sidesliderRef.handleGetValue();
        console.log(this.curIndex, this.curGroupIndex, environments);
        window.changeAlert = false;
      },

      handleViewSideSliderCondition () {
        this.isShowResourceInstanceEffectTime = true;
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: async () => {
            const hasData = {};
            const selectList = [...this.currentSelectList, ...this.curSelectedGroup].reduce(
              (curr, next) => {
                // eslint-disable-next-line no-unused-expressions
                hasData[`${next.name}&${next.id}`]
                  ? ''
                  : (hasData[`${next.name}&${next.id}`] = true && curr.push(next));
                return curr;
              },
              []
            );
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              selectList.push(row);
              this.currentSelectList = [...selectList];
            } else {
              this.currentSelectList = selectList.filter(
                (item) => String(item.id) !== String(row.id)
              );
            }
            this.fetchCustomTotal(this.currentSelectList);
            this.$emit('on-selected-group', this.currentSelectList);
          },
          all: async () => {
            const tableList = cloneDeep(this.list);
            const hasData = {};
            const selectList = [...this.currentSelectList, ...this.curSelectedGroup].reduce(
              (curr, next) => {
                // eslint-disable-next-line no-unused-expressions
                hasData[`${next.name}&${next.id}`]
                  ? ''
                  : (hasData[`${next.name}&${next.id}`] = true && curr.push(next));
                return curr;
              },
              []
            );
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
          if (
            this.$refs.groupPermRef
            && selectionCount
            && selectionCount.length
            && selectionCount[0].children
          ) {
            selectionCount[0].children[0].innerHTML = payload.length;
          }
        });
      },
      
      handleResourceEffectTimeCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowResourceInstanceEffectTime = false;
          this.resetDataAfterClose();
        }, _ => _);
      },

      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowSideSlider = false;
          this.isShowEnvironmentsSideSlider = false;
          this.resetDataAfterClose();
        }, _ => _);
      },

      handleBatchDelete () {
        window.changeAlert = true;
        this.isBatchDelete = false;
      },

      handleCancelDelete () {
        window.changeAlert = false;
        this.isBatchDelete = true;
      },

      handleEmptyClear () {
        this.$emit('on-clear');
      },

      handleEmptyRefresh () {
        this.$emit('on-refresh');
      },

      getDefaultSelect () {
        return this.list.length > 0;
      },

      getTableProps (payload) {
        const tabMap = {
          personalOrDepartPerm: () => {
            const { type } = this.queryGroupData;
            const typeMap = {
              user: () => {
                return [
                  { label: '', prop: 'selection' },
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
              { label: this.$t(`m.grading['管理空间']`), prop: 'role_name' },
              { label: this.$t(`m.resourcePermiss['加入用户组时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' }
            ];
          },
          userTempPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.grading['管理空间']`), prop: 'role_name' },
              { label: this.$t(`m.resourcePermiss['加入用户组时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' }
            ];
          },
          departTempPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.grading['管理空间']`), prop: 'role_name' },
              { label: this.$t(`m.resourcePermiss['加入用户组时间']`), prop: 'created_time' },
              { label: this.$t(`m.perm['加入方式']`), prop: 'join_type' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' }
            ];
          },
          customPerm: () => {
            return [
              { label: this.$t(`m.common['操作']`), prop: 'action_name' },
              { label: this.$t(`m.common['资源实例']`), prop: 'resource_instance' },
              { label: this.$t(`m.common['生效条件']`), prop: 'effective_conditions' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_display' },
              { label: this.$t(`m.common['操作-table']`), prop: 'custom_perm_operate' }
            ];
          }
        };
        return tabMap[payload] ? tabMap[payload]() : tabMap['personalOrDepartPerm']();
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1 || columnIndex === 2) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      resetDataAfterClose () {
        this.sideSliderTitle = '';
        this.curId = '';
        this.curPolicyId = '';
        this.batchDisabled = false;
        this.canOperate = true;
        this.disabled = true;
        this.isBatchDelete = true;
        this.previewData = [];
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import "@/views/user-org-perm/user-org-perm.css";
.my-perm-group-perm {
  /deep/ .user-org-perm-table {
    .bk-table-fixed-header-wrapper {
      th {
        &:first-child {
          .cell {
            padding-left: 32px;
          }
        }
      }
    }
    .bk-table-body {
      tr {
        &:hover {
          background-color: transparent;
          & > td {
            background-color: transparent;
          }
        }
      }
      td:first-child .cell,
      th:first-child .cell {
        padding-left: 32px;
      }
    }
  }
  /deep/ .member-custom-perm-table {
    .iam-perm-table-cell-cls {
      .cell {
        padding: 0px !important;
        height: 100%;
      }
      .condition-table-cell {
        height: 100%;
        flex-flow: column;
        display: flex;
        justify-content: center;
      }
      .effect-condition-side {
        .text{
          font-size: 14px;
          color: #63656e;
        }
      }
      .empty-text {
        padding: 0 15px;
      }
    }
    .operate-column {
      display: flex;
      align-items: center;
      .operate-column-btn  {
        margin-right: 12px;
      }
    }
    .bk-table-pagination-wrapper {
      display: none;
    }
  }
}
</style>

<template>
  <div>
    <!-- 申请自定义权限正常跳转 -->
    <smart-action class="biz-perm-apply">
      <render-horizontal-block :required="true" ext-cls="apply-way-wrapper" :label="$t(`m.permApply['选择操作']`)">
        <render-search>
          <bk-select
            v-model="systemValue"
            style="width: 480px;"
            :popover-min-width="480"
            :empty-text="$t(`m.common['暂无数据']`)"
            :search-placeholder="$t(`m.info['搜索关键字']`)"
            :searchable="true"
            :clearable="false"
            @selected="handleSysSelected">
            <bk-option v-for="option in systemList"
              :key="option.id"
              :id="option.id"
              :name="option.displayName">
              <span>{{ option.name }}</span>
              <span style="color: #c4c6cc;">({{ option.id }})</span>
            </bk-option>
          </bk-select>
          <div slot="right">
            <bk-input
              clearable
              v-model="actionSearchValue"
              :placeholder="$t(`m.info['操作搜索提示']`)"
              style="width: 320px;"
              @enter="handleActionSearch">
            </bk-input>
          </div>
        </render-search>
        <form class="bk-form bk-form-vertical inner-content">
          <div class="bk-form-item">
            <!-- eslint-disable max-len -->
            <div :class="['custom-tmpl-list-content-wrapper', { 'is-loading': customLoading }]" v-bkloading="{ isLoading: customLoading, opacity: 1 }">
              <render-action-tag
                v-if="commonActions.length > 0 && !customLoading"
                ref="commonActionRef"
                mode="detail"
                :system-id="systemValue"
                :tag-action-list="tagActionList"
                :data="commonActions"
                @on-change="handleActionTagChange"
                @on-mouse-enter="handleActionTagEnter"
                @on-mouse-leave="handleActionTagLeave" />
              <template v-if="originalCustomTmplList.length > 0 && !customLoading">
                <div class="action-empty-error" v-if="isShowActionError">{{ $t(`m.verify['请选择操作']`) }}</div>
                <div class="actions-wrapper">
                  <div
                    v-for="(item, index) in originalCustomTmplList"
                    :key="index"
                    :class="['action-item', { 'set-border': originalCustomTmplList.length > 1 }]">
                    <p style="cursor: pointer;" @click.stop="handleExpanded(item)" v-if="!(originalCustomTmplList.length === 1 && !isShowGroupAction(item))">
                      <section :class="['action-group-name', { 'set-cursor': originalCustomTmplList.length > 1 }]">
                        <Icon :type="item.expanded ? 'down-angle' : 'right-angle'" v-if="originalCustomTmplList.length > 1" />
                        <span :class="[{ 'action-hover': handleFormatTitleHover(item) }]">
                          {{ item.name }}
                        </span>
                        <span class="count">{{$t(`m.common['已选']`)}} {{ item.count }} / {{ item.allCount }} {{ $t(`m.common['个']`) }}</span>
                      </section>
                      <span :class="['check-all', { 'is-disabled': item.actionsAllDisabled }]" @click.stop="handleCheckAll(item)">
                        {{ item.actionsAllChecked ? $t(`m.common['取消全选']`) : $t(`m.common['选择全部']`) }}
                      </span>
                    </p>
                    <div class="action-content" v-if="item.expanded">
                      <div
                        :class="[
                          'self-action-content',
                          { 'set-border-bottom': isShowGroupAction(item) }
                        ]"
                        v-if="item.actions && item.actions.length > 0">
                        <bk-checkbox
                          v-for="(act, actIndex) in item.actions"
                          :key="actIndex"
                          :true-value="true"
                          :false-value="false"
                          v-model="act.checked"
                          :disabled="act.disabled"
                          :ext-cls="hoverActionData.actions.includes(act.id) ? 'iam-action-cls iam-action-hover' : 'iam-action-cls'"
                          @change="handleActionChecked(...arguments, act, item)">
                          <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                            <template v-if="act.disabled">
                              <span class="text" @click.stop="handleDisabledClick(act)">{{ act.name }}</span>
                            </template>
                            <template v-else>
                              <span class="text">{{ act.name }}</span>
                            </template>
                            <div slot="content" class="iam-perm-apply-action-popover-content">
                              <div>
                                <span class="name">{{ act.name }}</span>
                                <span :class="handleClassComputed(act)">({{ act.checked ? act.disabled ? $t(`m.common['已获得']`) : $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})</span>
                              </div>
                              <div class="description">{{ $t(`m.common['描述']`) + '：' + (act.description || '--') }}</div>
                              <div class="relate-action" v-if="act.related_actions.length > 0">
                                {{ getRelatedActionTips(act.related_actions) }}
                              </div>
                            </div>
                          </bk-popover>
                        </bk-checkbox>
                        <bk-checkbox
                          :true-value="true"
                          :false-value="false"
                          v-model="item.allChecked"
                          :disabled="item.actions.every(v => v.disabled)"
                          ext-cls="iam-action-all-cls"
                          @change="handleAllChange(...arguments, item)">
                          {{ $t(`m.common['全选']`) }}
                        </bk-checkbox>
                      </div>
                      <div class="sub-group-action-content" v-if="isShowGroupAction(item)">
                        <section
                          v-for="(subAct, subIndex) in item.sub_groups"
                          :key="subIndex"
                          :class="['sub-action-item', { 'set-margin': subIndex !== 0 }]">
                          <div class="sub-action-wrapper">
                            <span class="name" :title="subAct.name">{{ subAct.name }}</span>
                            <section>
                              <bk-checkbox
                                v-for="(act, actIndex) in subAct.actions"
                                :key="actIndex"
                                :true-value="true"
                                :false-value="false"
                                v-model="act.checked"
                                :disabled="act.disabled"
                                :ext-cls="hoverActionData.actions.includes(act.id) ? 'iam-action-cls iam-action-hover' : 'iam-action-cls'"
                                @change="handleSubActionChecked(...arguments, act, subAct, item)">
                                <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                                  <template v-if="act.disabled">
                                    <span class="text" @click.stop="handleDisabledClick(act)">{{ act.name }}</span>
                                  </template>
                                  <template v-else>
                                    <span class="text">{{ act.name }}</span>
                                  </template>
                                  <div slot="content" class="iam-perm-apply-action-popover-content">
                                    <div>
                                      <span class="name">{{ act.name }}</span>
                                      <span :class="handleClassComputed(act)">({{ act.checked ? act.disabled ? $t(`m.common['已获得']`) : $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})</span>
                                    </div>
                                    <div class="description">{{ $t(`m.common['描述']`) + '：' + (act.description || '--') }}</div>
                                    <div class="relate-action" v-if="act.related_actions.length > 0">
                                      {{ getRelatedActionTips(act.related_actions) }}
                                    </div>
                                  </div>
                                </bk-popover>
                              </bk-checkbox>
                            </section>
                          </div>
                          <bk-checkbox
                            :true-value="true"
                            :false-value="false"
                            v-model="subAct.allChecked"
                            :disabled="subAct.actions.every(v => v.disabled)"
                            ext-cls="iam-sub-action-all-cls"
                            @change="handleSubAllChange(...arguments, subAct, item)">
                            {{ $t(`m.common['全选']`) }}
                          </bk-checkbox>
                        </section>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
              <template v-if="originalCustomTmplList.length < 1 && !customLoading">
                <div class="empty-wrapper">
                  <!-- <Icon type="warning" />
                                    {{ isActionsFilter ? $t(`m.common['搜索无结果']`) : $t(`m.permApply['暂无可申请的操作']`) }} -->
                  <ExceptionEmpty
                    :type="emptyData.type"
                    :empty-text="emptyData.text"
                    :tip-text="emptyData.tip"
                    :tip-type="emptyData.tipType"
                    @on-clear="handleEmptyClear"
                    @on-refresh="handleEmptyRefresh"
                  />
                </div>
              </template>
            </div>
          </div>
        </form>
      </render-horizontal-block>
      <render-horizontal-block ext-cls="mt16" :label="$t(`m.permApply['关联资源实例']`)">
        <section ref="instanceTableRef" class="aggregate-tab-instance-table perm-apply-resource-instance-table">
          <resource-instance-table
            :list="tableData"
            :original-table-list="tableDataBackup"
            :system-id="systemValue"
            :is-all-expanded="isAllExpanded"
            ref="resInstanceTableRef"
            @on-select="handleResourceSelect"
            @on-realted-change="handleRelatedChange" />
          <div slot="append" class="expanded-action-wrapper">
            <div class="aggregate-action-tab-group">
              <div
                v-for="item in AGGREGATION_EDIT_ENUM"
                :key="item.value"
                :class="[
                  'aggregate-action-btn',
                  { 'is-active': isAllExpanded === item.value },
                  { 'is-disabled': isAggregateDisabled }
                ]"
                @click.stop="handleAggregateActionChange(item.value)"
              >
                <span>{{ $t(`m.grading['${item.name}']`)}}</span>
              </div>
            </div>
          </div>
        </section>
      </render-horizontal-block>
      <render-horizontal-block ext-cls="reason-wrapper" :label="$t(`m.common['理由']`)" :required="true">
        <section ref="resInstanceReasonRef">
          <bk-input
            type="textarea"
            v-model="reason"
            :maxlength="255"
            :ext-cls="isShowReasonError ? 'perm-apply-reason-error' : ''"
            @input="handleReasonInput"
            @blur="handleReasonBlur">
          </bk-input>
          <p class="reason-empty-wrapper" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
        </section>
      </render-horizontal-block>
      <div slot="action">
        <bk-button
          theme="primary"
          :loading="buttonLoading"
          @click="handleApplySubmit">
          {{ $t(`m.common['提交']`) }}
        </bk-button>
        <bk-button
          style="margin-left: 10px;"
          @click="handleCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </smart-action>
    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      :show-member="false"
      @animation-end="handleAnimationEnd" />
    <bk-sideslider
      :is-show.sync="isShowGradeSlider"
      :width="640"
      :title="gradeSliderTitle"
      :quick-close="true"
      @animation-end="gradeSliderTitle === ''">
      <div class="grade-members-content"
        slot="content"
        v-bkloading="{ isLoading: sliderLoading, opacity: 1 }">
        <template v-if="!sliderLoading">
          <div v-for="(item, index) in gradeMembers"
            :key="index"
            class="member-item">
            <span class="member-name">
              {{ item }}
            </span>
          </div>
          <p class="info">{{ $t(`m.info['管理空间成员提示']`) }}</p>
        </template>
      </div>
    </bk-sideslider>

    <confirmDialog
      :width="600"
      :show.sync="isShowConfirmDialog"
      :title="confirmDialogTitle"
      :is-custom-style="true"
      @on-cancel="isShowConfirmDialog = false"
      @on-sumbit="isShowConfirmDialog = false"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { guid, formatCodeData } from '@/common/util';
  import { PERMANENT_TIMESTAMP, AGGREGATION_EDIT_ENUM } from '@/common/constants';
  import RenderActionTag from '@/components/common-action';
  import ResourceInstanceTable from '../components/resource-instance-table';
  import Policy from '@/model/policy';
  import AggregationPolicy from '@/model/aggregation-policy';
  import Condition from '@/model/condition';
  import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider';
  import ConfirmDialog from '@/components/iam-confirm-dialog/index';

  export default {
    name: '',
    components: {
      RenderActionTag,
      ResourceInstanceTable,
      RenderPermSideslider,
      ConfirmDialog
    },
    data () {
      return {
        AGGREGATION_EDIT_ENUM,
        systemValue: '',
        systemList: [],
        buttonLoading: false,
        originalCustomTmplList: [],
        originalCustomTmplListBackup: [],
        containerNode: null,
        tableData: [],
        tableDataBackup: [],
        reason: '',
        isShowActionError: false,
        isShowReasonError: false,
        routerQuery: {},
        routerParams: {},
        linearActionList: [],

        requestQueue: ['action', 'aggregate', 'commonAction'],
        isAllExpanded: false,
        aggregationMap: [],
        aggregations: [],
        aggregationsBackup: [],
        aggregationsTableData: [],
        commonActions: [],
        actionSearchValue: '',
        // 用户组列表数据
        tableList: [],
        isShowPermSidesilder: false,
        isShowGradeSlider: false,
        gradeSliderTitle: '',
        curGroupName: '',
        curGroupId: '',
        isShowUserGroup: true,
        isShowIndependent: false,
        isShowExpiredError: false,
        isShowGroupError: false,
        sliderLoading: false,
        isShowHasUserGroup: false,
        currentSelectList: [],
        curUserGroup: [],
        expiredAt: 15552000,
        expiredAtUse: 15552000,
        // 默认按钮选中
        checkRadio: 'userGroup',
        tableLoading: false,
        gradeMembers: [],

        // route.query 里的 tid 参数改变名字为 cache_id
        sysAndtid: false,
        routerValue: {},
        newTableList: [],
        tagActionList: [],
        hoverActionData: {
          actions: []
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: 'search'
        },
        isShowConfirmDialog: false,
        isAllUnlimited: false,
        confirmDialogTitle: this.$t(`m.verify['admin无需申请权限']`)
      };
    },
    computed: {
            ...mapGetters(['user', 'externalSystemId']),
            // 是否无权限申请
            isNoPermApplay () {
                return this.routerQuery.system_id;
            },
            // 无权限组时
            isNoPermissionsSet () {
                return this.routerQuery.cache_id;
            },
            isShowGroupAction () {
                return (item) => {
                    const isExistSubGroup = (item.sub_groups || []).some(v => v.sub_groups && v.sub_groups.length > 0);
                    return item.sub_groups && item.sub_groups.length > 0 && !isExistSubGroup;
                };
            },
            customLoading () {
                return this.requestQueue.length > 0;
            },
            isAggregateDisabled () {
                return this.tableData.length < 1
                    || this.aggregations.length < 1 || (this.tableData.length === 1 && !this.tableData[0].isAggregate);
            },
            curSelectActions () {
                const allActionIds = [];
                this.originalCustomTmplList.forEach(payload => {
                    if (!payload.actionsAllDisabled) {
                        payload.actions.forEach(item => {
                            if (item.checked) {
                                allActionIds.push(item.id);
                            }
                        })
                        ;(payload.sub_groups || []).forEach(subItem => {
                            (subItem.actions || []).forEach(act => {
                                if (act.checked) {
                                    allActionIds.push(act.id);
                                }
                            });
                        });
                    }
                });
                return allActionIds;
            }
    },
    watch: {
      '$route': {
        handler (value) {
          if (value.query.system_id && value.query.cache_id) {
            const { system_id, cache_id } = value.query;
            this.routerQuery = Object.assign({}, {
              system_id,
              cache_id
            });
            this.sysAndtid = true;
          } else if (value.query.system_id) {
            this.routerQuery = Object.assign({}, {
              system_id: value.query.system_id,
              cache_id: '',
              ids: value.query.ids
            });
            this.sysAndtid = true;
          } else {
            this.routerQuery = Object.assign({}, {
              system_id: '',
              cache_id: ''
            });
          }

          if (value.params.ids) {
            const { ids, temporaryTableData } = value.params;
            this.routerParams = Object.assign({}, {
              ids,
              temporaryTableData
            });
          }
        },
        immediate: true
      },
      reason (value) {
        this.isShowReasonError = false;
      },
      curSelectActions (value) {
        this.aggregationsTableData = this.aggregationsTableData.filter(item => value.includes(item.id));
        this.getFilterAggregateAction();
      },
      tableData: {
        handler (value) {
          this.tagActionList = value.map(e => e.id);
          if (value.filter(item => item.isAggregate).length < 1) {
            this.isAllExpanded = false;
          }
        },
        deep: true
      },
      actionSearchValue (newVal, oldValue) {
        if (newVal === '' && oldValue !== '' && this.isActionsFilter) {
          this.isActionsFilter = false;
          this.originalCustomTmplList = _.cloneDeep(this.originalCustomTmplListBackup);
          this.handleActionLinearData(true);
        }
      }
    },
    created () {
      this.navStick = true;
      // 判断数组是否被另外一个数组包含
      this.isArrayInclude = (target, origin) => {
        const itemAry = [];
        target.forEach(function (p1) {
          if (origin.indexOf(p1) !== -1) {
            itemAry.push(p1);
          }
        });
        if (itemAry.length === target.length) {
          return true;
        }
        return false;
      };
      this.isActionsFilter = false;
    },
    methods: {
      // 用户组数据
      async fetchUserGroupList () {
        this.tableLoading = true;
        const params = {
          cache_id: this.routerQuery.cache_id,
          apply_disable: false
        };
        try {
          const res = await this.$store.dispatch('userGroup/getUserGroupList', params);
          if (res.data.count > 0) {
            this.isShowHasUserGroup = true;
          }
          this.tableList.splice(0, this.tableList.length, ...(res.data.results || []));
          this.$nextTick(() => {
            this.tableList.forEach(item => {
              if (this.curUserGroup.includes(item.id.toString())) {
                this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
              }
            });
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },
      handleView (payload) {
        this.curGroupName = payload.name;
        this.curGroupId = payload.id;
        this.isShowPermSidesilder = true;
      },
      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSidesilder = false;
      },
      handleViewDetail (payload) {
        if (payload.role && payload.role.name) {
          this.isShowGradeSlider = true;
          this.gradeSliderTitle = this.$t(`m.info['管理空间成员侧边栏标题信息']`, { value: `${this.$t(`m.common['【']`)}${payload.role.name}${this.$t(`m.common['】']`)}` });
          this.fetchRoles(payload.role.id);
        }
      },
      // 无权限跳转推荐用户组逻辑
      handlerChange () {
        if (this.checkRadio === 'userGroup') {
          this.isShowUserGroup = true;
          this.isShowIndependent = false;
        } else {
          this.isShowIndependent = true;
          this.isShowUserGroup = false;
        }
      },
      handleToUserGroup () {
        this.$router.push({
          name: 'applyJoinUserGroup'
        });
      },
      handleToCustompermissions () {
        this.$router.push({
          name: 'applyCustomPerm'
        });
      },
      handlerOneChange (selection, row) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },
      handlerAllChange (selection) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },
      handleCellAttributes ({ rowIndex, cellIndex, row, column }) {
        if (cellIndex === 0) {
          if (this.curUserGroup.includes(row.id.toString())) {
            return {
              title: this.$t(`m.info['你已加入该组']`)
            };
          }
          return {};
        }
        return {};
      },
      setDefaultSelect (payload) {
        return !this.curUserGroup.includes(payload.id.toString());
      },
      async fetchCurUserGroup () {
        try {
          const res = await this.$store.dispatch('perm/getPersonalGroups', {
            page_size: 100,
            page: 1
          });
          this.curUserGroup = res.data.results.filter(item => item.department_id === 0).map(item => item.id);
        } catch (e) {
          this.$emit('toggle-loading', false);
          console.error(e);
          this.messageAdvancedError(e);
        }
      },
      async fetchRoles (id) {
        this.sliderLoading = true;
        try {
          const res = await this.$store.dispatch('role/getGradeMembers', { id });
          this.gradeMembers = [...res.data];
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.sliderLoading = false;
        }
      },
      /**
       * 获取页面数据
       */
      async fetchPageData () {
        await this.fetchSystems();
        if (this.systemValue) {
          // await Promise.all([
          //     this.fetchPolicies(this.systemValue),
          //     this.fetchAggregationAction(this.systemValue),
          //     this.fetchCommonActions(this.systemValue)
          // ]);
          await this.fetchPolicies(this.systemValue);
          await this.fetchAggregationAction(this.systemValue);
          await this.fetchCommonActions(this.systemValue);
        }
        if (this.sysAndtid) {
          await Promise.all([
            // 获取用户组数据
            this.fetchUserGroupList(),
            // 获取个人用户的用户组列表
            this.fetchCurUserGroup()
          ]);
          if (this.routerParams.ids) {
            this.handleActionTagChange(true, this.routerParams.ids);
          }
        }
      },

      getRelatedActionTips (payload) {
        const relatedActions = this.linearActionList.filter(item => payload.includes(item.id));
        return `${this.$t(`m.common['依赖操作']`)}: ${relatedActions.map(item => item.name).join('，')}`;
      },

      handleRelatedActions (payload, flag) {
        this.originalCustomTmplList.forEach((item, index) => {
          item.actions.forEach(act => {
            if (!act.disabled) {
              if (payload.related_actions.includes(act.id) && flag && !act.checked) {
                act.checked = true;
                this.setTableDataByRelated(act, true, item);
              }
              if (act.related_actions.includes(payload.id) && !flag && act.checked) {
                act.checked = false;
                this.setTableDataByRelated(act, false, item);
              }
            }
          })
          ;(item.sub_groups || []).forEach(sub => {
            sub.actions.forEach(act => {
              if (!act.disabled) {
                if (payload.related_actions.includes(act.id) && flag) {
                  act.checked = true;
                  this.setTableDataByRelated(act, true, item);
                }
                if (act.related_actions.includes(payload.id) && !flag) {
                  act.checked = false;
                  this.setTableDataByRelated(act, false, item);
                }
              }
            });
            const isSubAllChecked = sub.actions.every(v => v.checked);
            sub.allChecked = isSubAllChecked;
          });
          const isAllChecked = item.actions.every(v => v.checked);
          item.allChecked = isAllChecked;
          if (item.sub_groups && item.sub_groups.length > 0) {
            item.actionsAllChecked = isAllChecked && item.sub_groups.every(v => v.allChecked);
          } else {
            item.actionsAllChecked = isAllChecked;
          }
        });
      },

      setTableDataByRelated (payload, flag, item) {
        // 操作表格数据前需判断其是否已经存在
        const isExist = this.tableData.some(item => {
          return item.id === payload.id
            || (item.isAggregate && item.actions.map(_ => _.id).includes(payload.id));
        });
        if (flag) {
          if (!isExist) {
            ++item.count;
            if (!payload.resource_groups || !payload.resource_groups.length) {
              payload.resource_groups = payload.related_resource_types.length ? [{ id: '', related_resource_types: payload.related_resource_types }] : [];
            }
            this.tableData.unshift(new Policy({ ...payload, tag: 'add' }, 'custom', false, true));
          }
        } else {
          if (isExist) {
            const index = this.tableData.findIndex(item => item.id === payload.id);
            if (index > -1) {
              this.tableData.splice(index, 1);
              --item.count;
            } else {
              this.tableData.forEach(item => {
                if (item.isAggregate) {
                  if (item.actions.map(_ => _.id).includes(payload.id)) {
                    item.actions = item.actions.filter(act => act.id !== payload.id);
                    --item.count;
                  }
                }
              });
              this.tableData = this.tableData.filter(
                item => !item.isAggregate || (item.isAggregate && item.actions.length > 0)
              );
            }
          }
        }
      },

      handleActionSearch (value) {
        const keyword = value.trim();
        if (keyword === '') {
          return;
        }
        this.isActionsFilter = true;
        this.emptyData = formatCodeData(0, Object.assign(this.emptyData, { tipType: 'search' }));
        let tempList = [];
        this.originalCustomTmplListBackup.forEach(item => {
          let tempAction = [];
          const tempSubGroups = [];
          if (item.actions && item.actions.length > 0) {
            tempAction = item.actions.filter(act => act.name.indexOf(keyword) > -1);
          }
          if (item.sub_groups && item.sub_groups.length > 0) {
            item.sub_groups.forEach(sub => {
              const temps = sub.actions.filter(act => act.name.indexOf(keyword) > -1);
              tempSubGroups.push({
                actions: temps,
                name: sub.name
              });
            });
          }
          tempList.push({
            name: item.name,
            actions: tempAction,
            sub_groups: tempSubGroups.filter(item => item.actions.length > 0)
          });
        });
        tempList = tempList.filter(item => item.actions.length > 0 || item.sub_groups.length > 0);
        this.originalCustomTmplList = _.cloneDeep(tempList);
        this.handleActionLinearData(true);
      },

      handleEmptyClear () {
        this.actionSearchValue = '';
        this.emptyData.tipType = '';
      },
            
      handleEmptyRefresh () {
        this.fetchPageData();
      },

      /**
       * 获取系统对应的常用操作
       *
       * @param {String} systemId 系统id
       */
      async fetchCommonActions (systemId) {
        try {
          const res = await this.$store.dispatch('permApply/getUserCommonAction', { systemId });
          this.commonActions.splice(0, this.commonActions.length, ...(res.data || []));
          this.commonActions.forEach(item => {
            item.$id = guid();
          });
          if (this.commonActions.length > 0) {
            if (this.originalCustomTmplList.length > 1) {
              this.originalCustomTmplList.forEach(item => {
                item.expanded = false;
              });
            }
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },
      handleActionTagChange (flag, payload) {
        if (payload.length < 1 || this.originalCustomTmplList.length < 1) {
          return;
        }
        this.handleActionMatchChecked(flag, payload);
        // 默认权限不能改变，所以不能参与匹配
        const temps = [];
        payload.forEach(item => {
          const data = this.linearActionList.find(act => act.id === item);
          if (!data.disabled) {
            temps.push(item);
          }
        });
        if (flag) {
          const differenceSetIds = temps.filter(v => !this.tableData.map(sub => sub.id).includes(v));
          differenceSetIds.forEach(v => {
            const data = this.linearActionList.find(act => act.id === v);
            // eslint-disable-next-line max-len
            const isTempora = this.routerParams.temporaryTableData && this.routerParams.temporaryTableData.length > 0;
            if (isTempora) {
              // eslint-disable-next-line max-len
              data.resource_groups = this.routerParams.temporaryTableData.find(e => e.id === data.id).resource_groups;
            }
            if (!data.resource_groups || !data.resource_groups.length) {
              data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
            }
            this.tableData.unshift(new Policy({ ...data, tag: 'add', isTempora }, isTempora ? '' : 'custom', false, true));
          });
        } else {
          this.tableData = this.tableData.filter(v => !temps.includes(v.id));
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !temps.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 1));
        }
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleActionTagEnter (payload) {
        this.hoverActionData = payload;
      },

      handleActionTagLeave (payload) {
        this.hoverActionData = Object.assign(payload, { actions: [] });
      },

      handleFormatTitleHover (payload) {
        let subGroupId = [];
        const originIds = payload.actions.map(item => item.id);
        payload.sub_groups.forEach(item => {
          item.actions.forEach((subItem) => {
            subGroupId = [...new Set(subGroupId.concat(subItem.id))];
          });
        });
        const list = [...new Set(subGroupId.concat(originIds))];
        const result = this.hoverActionData.actions.filter(item => list.includes(item));
        return !!result.length;
      },

      handleActionMatchChecked (flag, payload) {
        this.originalCustomTmplList.forEach(item => {
          let allCheckedLen = 0;
          let count = 0;
          let delCount = 0;
          item.actions.forEach(item => {
            if (!item.disabled) {
              if (payload.includes(item.id)) {
                if (!item.checked && flag) {
                  ++count;
                }
                if (item.checked && !flag) {
                  ++delCount;
                }
                item.checked = flag;
              }
            }
            if (item.disabled || item.checked) {
              allCheckedLen++;
            }
          });
          item.allChecked = allCheckedLen === item.actions.length

          ;(item.sub_groups || []).forEach(subItem => {
            let allSubCheckedLen = 0
            ;(subItem.actions || []).forEach(act => {
              if (!act.disabled) {
                if (payload.includes(act.id)) {
                  if (!act.checked && flag) {
                    ++count;
                  }
                  if (act.checked && !flag) {
                    ++delCount;
                  }
                  act.checked = flag;
                }
              }
              if (act.disabled || act.checked) {
                allSubCheckedLen++;
              }
            });
            subItem.allChecked = allSubCheckedLen === subItem.actions.length;
          });

          item.actionsAllChecked = item.actions.every(act => act.checked) && (item.sub_groups || []).every(
            v => {
              return v.actions.every(act => act.checked);
            });

          if (flag) {
            item.count = item.count + count;
          } else {
            item.count = item.count - delCount;
          }
        });
      },

      async fetchAggregationAction (payload) {
        try {
          const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: payload });
          if (res.data.aggregations.length < 1) {
            return;
          }
          // 过滤掉不存在当前系统下的操作
          const actionIds = [];
          this.originalCustomTmplList.forEach(item => {
            actionIds.push(...item.actions.map(_ => _.id));
            if (item.sub_groups && item.sub_groups.length > 0) {
              item.sub_groups.forEach(subItem => {
                actionIds.push(...subItem.actions.map(_ => _.id));
              });
            }
          });
          const aggregations = []
          ;(res.data.aggregations || []).forEach(item => {
            const { actions, aggregate_resource_types } = item;
            const curActions = actions.filter(_ => actionIds.includes(_.id));
            if (curActions.length > 0) {
              aggregations.push({
                actions: curActions,
                aggregate_resource_types
              });
            }
          });
          this.aggregationsBackup = _.cloneDeep(aggregations);
          this.aggregations = aggregations;
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },

      handleExpanded (payload) {
        if (this.originalCustomTmplList.length < 2) {
          return;
        }
        payload.expanded = !payload.expanded;
      },

      handleCheckAll (payload) {
        if (payload.actionsAllDisabled) {
          return;
        }
        const tempActionIds = [];
        const allActionIds = [];
        const tempActions = [];
        this.isShowActionError = false;
        payload.actionsAllChecked = !payload.actionsAllChecked;
        if (!payload.actions.every(v => v.disabled)) {
          payload.allChecked = payload.actionsAllChecked;
        }
        payload.actions.forEach(item => {
          if (!item.disabled) {
            item.checked = payload.actionsAllChecked;
            tempActionIds.push(item.id);
            tempActions.push(item);
          }
          allActionIds.push(item.id);
        })
        ;(payload.sub_groups || []).forEach(subItem => {
          subItem.actionsAllChecked = payload.actionsAllChecked;
          subItem.allChecked = payload.actionsAllChecked
          ;(subItem.actions || []).forEach(act => {
            if (!act.disabled) {
              act.checked = payload.actionsAllChecked;
              tempActionIds.push(act.id);
              tempActions.push(act);
            }
            allActionIds.push(act.id);
          });
        });

        if (!payload.actionsAllChecked) {
          const tempData = [];
          this.tableData.forEach(item => {
            if (!item.isAggregate && !tempActionIds.includes(item.id)) {
              tempData.push(item);
            }
            if (item.isAggregate && !this.isArrayInclude(item.actions.map(v => v.id), tempActionIds)) {
              tempData.push(item);
            }
          });
          this.tableData.splice(0, this.tableData.length, ...tempData);
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !tempActionIds.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 0));
        } else {
          const differenceSetIds = allActionIds.filter(v => !this.tableData.map(sub => sub.id).includes(v));
          differenceSetIds.forEach(v => {
            const data = this.linearActionList.find(act => act.id === v);
            if (!data.resource_groups || !data.resource_groups.length) {
              data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
            }
            this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom', false, true));
          });
        }

        tempActions.forEach(item => {
          this.handleRelatedActions(item, payload.actionsAllChecked);
        });
        payload.count = payload.actionsAllChecked ? payload.allCount : 0;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleSubAllChange (newVal, oldVal, val, payload, item) {
        const tempActionIds = [];
        let count = 0;
        this.isShowActionError = false;
        payload.actions.forEach(item => {
          if (!item.disabled) {
            if (!item.checked && newVal) {
              ++count;
            }
            item.checked = newVal;
            tempActionIds.push(item.id);
            this.handleRelatedActions(item, newVal);
          }
        });

        if (!newVal) {
          item.actionsAllChecked = false;
          const tempData = [];
          this.tableData.forEach(item => {
            if (!item.isAggregate && !tempActionIds.includes(item.id)) {
              tempData.push(item);
            }
            if (item.isAggregate && !this.isArrayInclude(item.actions.map(v => v.id), tempActionIds)) {
              tempData.push(item);
            }
          });
          this.tableData.splice(0, this.tableData.length, ...tempData);
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !tempActionIds.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 0));

          item.count = item.count - payload.actions.length;
          return;
        }

        item.actionsAllChecked = item.actions.every(act => act.checked) && item.sub_groups.every(v => {
          return v.actions.every(act => act.checked);
        });

        const differenceSetIds = payload.actions.map(v => v.id).filter(
          v => !this.tableData.map(sub => sub.id).includes(v)
        );
        differenceSetIds.forEach(v => {
          const data = this.linearActionList.find(act => act.id === v);
          if (!data.resource_groups || !data.resource_groups.length) {
            data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
          }
          this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom', false, true));
        });

        item.count = item.count + count;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleAllChange (newVal, oldVal, val, payload) {
        const tempActionIds = [];
        let count = 0;
        this.isShowActionError = false;
        payload.actions.forEach(item => {
          if (!item.disabled) {
            if (!item.checked && newVal) {
              ++count;
            }
            item.checked = newVal;
            tempActionIds.push(item.id);
          }
        });

        if (!newVal) {
          payload.actionsAllChecked = false;
          const tempData = [];
          this.tableData.forEach(item => {
            if (!item.isAggregate && !tempActionIds.includes(item.id)) {
              tempData.push(item);
            }
            if (item.isAggregate && !this.isArrayInclude(item.actions.map(v => v.id), tempActionIds)) {
              tempData.push(item);
            }
          });
          this.tableData.splice(0, this.tableData.length, ...tempData);
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !tempActionIds.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 0));

          payload.count = payload.count - payload.actions.length;
          return;
        }

        if (payload.sub_groups && payload.sub_groups.length > 0) {
          payload.actionsAllChecked = payload.sub_groups.every(v => {
            return v.actions.every(item => item.checked);
          });
        } else {
          payload.actionsAllChecked = true;
        }

        const differenceSetIds = payload.actions.map(v => v.id).filter(
          v => !this.tableData.map(sub => sub.id).includes(v)
        );
        differenceSetIds.forEach(item => {
          const data = this.linearActionList.find(act => act.id === item);
          if (!data.resource_groups || !data.resource_groups.length) {
            data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
          }
          this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom', false, true));
        });

        payload.count = payload.count + count;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      /**
       * 获取选中的操作具有的分组
       */
      getFilterAggregateAction () {
        let aggregationAction = [];
        const curSelectActions = (() => {
          const tempAction = [];
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              tempAction.push(...item.actions.map(_ => _.id));
            } else {
              tempAction.push(item.id);
            }
          });
          return tempAction;
        })();
        this.aggregationsBackup.forEach((item, index) => {
          const tempObj = _.cloneDeep(item);
          const tempAction = tempObj.actions.map(_ => _.id);
          const intersection = [...new Set(tempAction.filter(v => curSelectActions.includes(v)))];
          if (intersection.length > 0) {
            tempObj.actions = tempObj.actions.filter(v => intersection.includes(v.id));
            aggregationAction.push(tempObj);
          }
        });
        aggregationAction = aggregationAction.filter(item => item.actions.length > 1);
        this.aggregations = _.cloneDeep(aggregationAction);
      },

      handleAggregateActionChange (payload) {
        this.getFilterAggregateAction();
        this.handleAggregateAction(payload);
        // 扩展无限制、无实例下聚合操作和单操作去重场景
        this.handleUnlimitedActionChange(this.isAllUnlimited);
      },

      handleUnlimitedActionChange (payload) {
        const tableData = _.cloneDeep(this.tableData);
        tableData.forEach((item, index) => {
          if (!item.isAggregate) {
            if (item.resource_groups && item.resource_groups.length) {
              item.resource_groups.forEach(groupItem => {
                groupItem.related_resource_types && groupItem.related_resource_types.forEach(types => {
                  if (!payload && (types.condition.length > 0 && types.condition[0] !== 'none')) {
                    return;
                  }
                  if (payload) {
                    types.condition = [];
                    types.isError = false;
                  }
                });
              });
            } else {
              item.name = item.name.split('，')[0];
            }
          }
          if (item.instances && item.isAggregate) {
            item.isNoLimited = false;
            item.isError = !(item.instances.length || (!item.instances.length && item.isNoLimited));
            item.isNeedNoLimited = true;
            if (!payload || item.instances.length) {
              item.isNoLimited = false;
              item.isError = false;
            }
            if ((!item.instances.length && !payload && item.isNoLimited) || payload) {
              item.isNoLimited = true;
              item.isError = false;
              item.instances = [];
            }
            return this.$set(
              tableData,
              index,
              new AggregationPolicy(item)
            );
          }
        });
        this.tableData = _.cloneDeep(tableData);
      },

      handleRelatedChange (payload) {
        this.aggregationsTableData = _.cloneDeep(payload);
      },

      handleResourceSelect (payload) {
        const curAction = payload.actions.map(item => item.id);
        const instances = (function () {
          const arr = [];
          payload.aggregateResourceType.forEach(resourceItem => {
            const { id, name, system_id } = resourceItem;
            payload.instancesDisplayData[id] && payload.instancesDisplayData[id].forEach(v => {
              const curItem = arr.find(_ => _.type === id);
              if (curItem) {
                curItem.path.push([{
                  id: v.id,
                  name: v.name,
                  system_id,
                  type: id,
                  type_name: name
                }]);
              } else {
                arr.push({
                  name,
                  type: id,
                  path: [[{
                    id: v.id,
                    name: v.name,
                    system_id,
                    type: id,
                    type_name: name
                  }]]
                });
              }
            });
          });
          return arr;
        })();
        let selectPath = instances[0].path;
        if (instances.length > 0) {
          this.aggregationsTableData.forEach(item => {
            if (curAction.includes(item.id)) {
              if (item.tag === 'unchanged') {
                item.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types
                    && groupItem.related_resource_types.forEach(subItem => {
                      subItem.condition.forEach(conditionItem => {
                        conditionItem.instance.forEach(instanceItem => {
                          if (instanceItem.type === instances[0].type) {
                            selectPath = selectPath.filter(v => {
                              const target = v.map(_ => `${_.type}${_.id}`).sort();
                              return instanceItem.path.map(pathItem => pathItem.map(v => `${v.type}${v.id}`).sort()).filter(pathSub => _.isEqual(target, pathSub)).length < 1;
                            });
                            if (selectPath.length > 0) {
                              instanceItem.path.push(...selectPath);
                              instanceItem.paths.push(...selectPath);
                            }
                          }
                        });
                      });
                    });
                });
              } else {
                item.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types
                    && groupItem.related_resource_types.forEach(subItem => {
                      subItem.condition = [new Condition({ instances }, '', 'add')];
                    });
                });
              }
            }
          });
        }
      },

      handleAggregateAction (payload) {
        this.isAllExpanded = payload;
        const aggregationAction = this.aggregations;
        const actionIds = [];
        aggregationAction.forEach(item => {
          actionIds.push(...item.actions.map(_ => _.id));
        });
        if (payload) {
          // 缓存新增加的操作权限数据
          aggregationAction.forEach(item => {
            const filterArray = this.tableData.filter(
              subItem => item.actions.map(_ => _.id).includes(subItem.id)
            );

            const addArray = _.cloneDeep(filterArray.filter(
              subItem => !this.aggregationsTableData.map(_ => _.id).includes(subItem.id)
            ));
            if (addArray.length > 0) {
              this.aggregationsTableData.push(...addArray);
            }
          });
          const aggregations = aggregationAction.filter(item => {
            const target = item.actions.map(v => v.id).sort();
            const existData = this.tableData.find(subItem => {
              return subItem.isAggregate && _.isEqual(target, subItem.actions.map(v => v.id).sort());
            });
            return !existData;
          }).map((item, index) => {
            const existTableData = this.aggregationsTableData.filter(
              subItem => item.actions.map(act => act.id).includes(subItem.id)
            );

            if (existTableData.length > 0) {
              item.tag = existTableData.every(subItem => subItem.tag === 'unchanged') ? 'unchanged' : 'add';
              const tempObj = existTableData.find(subItem => subItem.tag === 'add');
              if (tempObj) {
                item.expired_at = tempObj.expired_at || 15552000;
                item.expired_display = tempObj.expired_display || this.$t(`m.common['6个月']`);
              } else {
                item.expired_at = existTableData[0].expired_at || 15552000;
                item.expired_display = existTableData[0].expired_display || this.$t(`m.common['6个月']`);
              }
              if (item.tag === 'add') {
                const conditions = existTableData.map(
                  subItem => subItem.resource_groups[0].related_resource_types[0].condition
                );
                // 是否都选择了实例
                const isAllHasInstance = conditions.every(subItem => subItem[0] !== 'none'); // 这里可能有bug, 都设置了属性点击批量编辑时数据变了
                if (isAllHasInstance) {
                  const instances = conditions.map(subItem => subItem.map(v => v.instance || []));
                  let isAllEqual = true;
                  for (let i = 0; i < instances.length - 1; i++) {
                    if (!_.isEqual(instances[i], instances[i + 1])) {
                      isAllEqual = false;
                      break;
                    }
                  }
                  if (isAllEqual) {
                    const instanceData = instances[0][0];
                    item.instances = [];
                    instanceData.map(pathItem => {
                      const instance = pathItem.path.map(e => {
                        return {
                          id: e[0].id,
                          name: e[0].name,
                          type: e[0].type
                        };
                      });
                      item.instances.push(...instance);
                    });
                    this.setInstancesDisplayData(item);
                  } else {
                    item.instances = [];
                  }
                } else {
                  item.instances = [];
                }
              }
            }
            return new AggregationPolicy(item);
          });
          this.tableData = this.tableData.filter(item => !actionIds.includes(item.id));
          this.tableData.unshift(...aggregations);
          return;
        }

        const aggregationData = [];
        const newTableData = [];
        this.tableData.forEach(item => {
          if (!item.isAggregate) {
            newTableData.push(item);
          } else {
            aggregationData.push(_.cloneDeep(item));
          }
        });
        this.tableData = _.cloneDeep(newTableData);
        const reallyActionIds = actionIds.filter(item => !this.tableData.map(v => v.id).includes(item));
        reallyActionIds.forEach(item => {
          // 优先从已有权限取值
          const curObj = this.aggregationsTableData.find(_ => _.id === item);
          if (curObj) {
            this.tableData.unshift(curObj);
          } else {
            const curAction = this.linearActionList.find(_ => _.id === item);
            const curAggregation = aggregationData.find(_ => _.actions.map(v => v.id).includes(item));
            this.tableData.unshift(new Policy({ ...curAction, tag: 'add' }, 'custom', false, true));
            if (curAggregation && curAggregation.instances.length > 0) {
              const curData = this.tableData[0];
              const instances = (function () {
                const arr = [];
                const aggregateResourceType = curAggregation.aggregateResourceType[0];
                const { id, name, system_id } = aggregateResourceType;
                curAggregation.instances.forEach(v => {
                  const curItem = arr.find(_ => _.type === id);
                  if (curItem) {
                    curItem.path.push([{
                      id: v.id,
                      name: v.name,
                      system_id,
                      type: id,
                      type_name: name
                    }]);
                  } else {
                    arr.push({
                      name,
                      type: id,
                      path: [[{
                        id: v.id,
                        name: v.name,
                        system_id,
                        type: id,
                        type_name: name
                      }]]
                    });
                  }
                });
                return arr;
              })();
              if (instances.length > 0) {
                curData.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types
                    && groupItem.related_resource_types.forEach(subItem => {
                      subItem.condition = [new Condition({ instances }, '', 'add')];
                    });
                });
              }
            }
          }
        });
      },

      // 设置InstancesDisplayData
      setInstancesDisplayData (data) {
        data.instancesDisplayData = data.instances.reduce((p, v) => {
          if (!p[v['type']]) {
            p[v['type']] = [];
          }
          p[v['type']].push({
            id: v.id,
            name: v.name
          });
          return p;
        }, {});
      },
            
      handleActionChecked (newVal, oldVal, val, actData, payload) {
        const data = this.linearActionList.find(item => item.id === actData.id);
        this.isShowActionError = false;
        if (!newVal) {
          payload.allChecked = false;
          payload.actionsAllChecked = false;

          const isExistIndex = this.tableData.findIndex(item => item.id === actData.id);
          isExistIndex !== -1 && this.tableData.splice(isExistIndex, 1);

          if (isExistIndex === -1) {
            for (let i = 0; i < this.tableData.length; i++) {
              const item = this.tableData[i];
              if (item.isAggregate) {
                for (let j = 0; j < item.actions.length; j++) {
                  const actionItem = item.actions[j];
                  if (actionItem.id === actData.id) {
                    item.actions.splice(j, 1);
                    if (item.actions.length === 1) {
                      const curAction = this.linearActionList.find(
                        _ => _.id === item.actions[0].id
                      );
                      const curData = new Policy({ ...curAction, tag: 'add' }, 'custom', false, true);
                      const instances = (function () {
                        const arr = [];
                        const aggregateResourceType = item.aggregateResourceType;
                        const { id, name, system_id } = aggregateResourceType;
                        item.instances.forEach(v => {
                          const curItem = arr.find(_ => _.type === id);
                          if (curItem) {
                            curItem.path.push([{
                              id: v.id,
                              name: v.name,
                              system_id,
                              type: id,
                              type_name: name
                            }]);
                          } else {
                            arr.push({
                              name,
                              type: id,
                              path: [[{
                                id: v.id,
                                name: v.name,
                                system_id,
                                type: id,
                                type_name: name
                              }]]
                            });
                          }
                        });
                        return arr;
                      })();
                      curData.expired_at = item.expired_at;
                      curData.expired_display = item.expired_display;
                      if (instances.length > 0) {
                        curData.resource_groups.forEach(groupItem => {
                          groupItem.related_resource_types
                            && groupItem.related_resource_types.forEach(subItem => {
                              subItem.condition = [new Condition({ instances }, '', 'add')];
                            });
                        });
                      }
                      this.tableData.splice(i, 1, curData);
                      break;
                    }
                    break;
                  }
                }
              }
            }
          }

          this.handleRelatedActions(actData, false);
          payload.count--;
          return;
        }
        payload.allChecked = payload.actions.every(item => item.checked);
        if (payload.sub_groups && payload.sub_groups.length > 0) {
          payload.actionsAllChecked = payload.allChecked && payload.sub_groups.every(v => {
            return v.actions.every(act => act.checked);
          });
        } else {
          payload.actionsAllChecked = payload.allChecked;
        }

        if (!data.resource_groups || !data.resource_groups.length) {
          data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
        }
        this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom', false, true));

        this.handleRelatedActions(actData, true);
        payload.count++;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleSubActionChecked (newVal, oldVal, val, actData, payload, item) {
        const data = this.linearActionList.find(v => v.id === actData.id);
        this.isShowActionError = false;
        if (!newVal) {
          payload.allChecked = false;
          item.actionsAllChecked = false;

          const isExistIndex = this.tableData.findIndex(v => v.id === actData.id);
          isExistIndex !== -1 && this.tableData.splice(isExistIndex, 1);

          if (isExistIndex === -1) {
            for (let i = 0; i < this.tableData.length; i++) {
              const item = this.tableData[i];
              if (item.isAggregate) {
                for (let j = 0; j < item.actions.length; j++) {
                  const actionItem = item.actions[j];
                  if (actionItem.id === actData.id) {
                    item.actions.splice(j, 1);
                    if (item.actions.length === 1) {
                      const curAction = this.linearActionList.find(
                        _ => _.id === item.actions[0].id
                      );
                      const curData = new Policy({ ...curAction, tag: 'add' }, 'custom', false, true);
                      const instances = (function () {
                        const arr = [];
                        const aggregateResourceType = item.aggregateResourceType;
                        const { id, name, system_id } = aggregateResourceType;
                        item.instances.forEach(v => {
                          const curItem = arr.find(_ => _.type === id);
                          if (curItem) {
                            curItem.path.push([{
                              id: v.id,
                              name: v.name,
                              system_id,
                              type: id,
                              type_name: name
                            }]);
                          } else {
                            arr.push({
                              name,
                              type: id,
                              path: [[{
                                id: v.id,
                                name: v.name,
                                system_id,
                                type: id,
                                type_name: name
                              }]]
                            });
                          }
                        });
                        return arr;
                      })();
                      curData.expired_at = item.expired_at;
                      curData.expired_display = item.expired_display;
                      if (instances.length > 0) {
                        curData.resource_groups.forEach(groupItem => {
                          groupItem.related_resource_types
                            && groupItem.related_resource_types.forEach(subItem => {
                              subItem.condition = [new Condition({ instances }, '', 'add')];
                            });
                        });
                      }
                      this.tableData.splice(i, 1, curData);
                      break;
                    }
                    break;
                  }
                }
              }
            }
          }

          this.handleRelatedActions(actData, false);
          item.count--;
          return;
        }
        payload.allChecked = payload.actions.every(item => item.checked);

        item.actionsAllChecked = item.actions.every(act => act.checked) && item.sub_groups.every(v => {
          return v.actions.every(act => act.checked);
        });

        if (!data.resource_groups || !data.resource_groups.length) {
          data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
        }
        this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom', false, true));

        this.handleRelatedActions(actData, true);
        item.count++;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },
            
      /**
       *
       * @param {Boolean} setChecked
       * 此方法获取数据赋值给this.linearActionList
       */
      handleActionLinearData (setChecked = false) {
        const linearActions = [];
        const hasCheckedList = [];
        if (setChecked) {
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              hasCheckedList.push(...item.actions.map(act => act.id));
            } else {
              hasCheckedList.push(item.id);
            }
          });
        }
        this.originalCustomTmplList.forEach((item, index) => {
          this.$set(item, 'expanded', index === 0);
          let allCount = 0;
          let count = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          item.actions = item.actions.filter(v => !v.hidden);
          item.actions.forEach(act => {
            // this.$set(act, 'checked', ['checked'].includes(act.tag) || hasCheckedList.includes(act.id));
            // this.$set(act, 'checked', ['checked', 'readonly'].includes(act.tag) || hasCheckedList.includes(act.id));
            // this.$set(act, 'disabled', act.tag === 'readonly');
            linearActions.push(act);
            if (act.checked) {
              ++count;
            }
          });
          allCount = allCount + item.actions.length;
          (item.sub_groups || []).forEach(sub => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions = sub.actions.filter(v => !v.hidden);
            sub.actions.forEach(act => {
              // this.$set(act, 'checked', ['checked'].includes(act.tag) || hasCheckedList.includes(act.id));
              // this.$set(act, 'checked', ['checked', 'readonly'].includes(act.tag) || hasCheckedList.includes(act.id));
              // this.$set(act, 'disabled', act.tag === 'readonly');
              linearActions.push(act);
              if (act.checked) {
                ++count;
              }
            });

            allCount = allCount + sub.actions.length;

            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });

          // 存在已选择的操作所在的分组未展开时，让其展开
          const isHasCheckedFlag = item.actions.some(act => act.checked && act.tag === 'checked')
            || (item.sub_groups || []).some(sub => sub.actions.some(act => act.checked && act.tag === 'checked'));
          if (index !== 0) {
            item.expanded = isHasCheckedFlag;
          }

          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
          this.$set(item, 'allCount', allCount);
          this.$set(item, 'count', count);
          if (item.sub_groups && item.sub_groups.length > 0) {
            this.$set(item, 'actionsAllChecked', isAllChecked && item.sub_groups.every(v => v.allChecked));
            this.$set(item, 'actionsAllDisabled', isAllDisabled && item.sub_groups.every(v => {
              return v.actions.every(sub => sub.disabled);
            }));
          } else {
            this.$set(item, 'actionsAllChecked', isAllChecked);
            this.$set(item, 'actionsAllDisabled', isAllDisabled);
          }
        });

        this.linearActionList = _.cloneDeep(linearActions);
      },

      handleResetExpandedStatus () {
        // 面板收起时默认回到初始态只是第一个分类操作展开其它收起
        this.originalCustomTmplList.forEach((item, index) => {
          item.expanded = index === 0;
        });
      },

      /**
       * 获取系统列表
       */
      async fetchSystems () {
        if (this.routerQuery.system_id) {
          this.systemValue = this.routerQuery.system_id;
        }
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const res = await this.$store.dispatch('system/getSystems', params);
          (res.data || []).forEach(item => {
            item.displayName = `${item.name}(${item.id})`;
          });
          this.systemList = res.data || [];
          if (!this.systemValue) {
            if (this.systemList.length) {
              this.systemValue = this.systemList[0].id;
            } else {
              this.fetchResetData();
              this.requestQueue = [];
              return;
            }
          }
          await this.fetchActions(this.systemValue);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },

      handleClassComputed (payload) {
        return payload.checked ? payload.disabled ? 'has-obtained' : 'has-selected' : 'no-obtained';
      },

      /**
       * 获取系统下的权限列表
       *
       * @param {String} systemId 系统id
       * 此方法获取数据，继承处理赋值给this.tableData
       * this.linearActionList 在handleActionLinearData获取并处理
       */
      async fetchPolicies (systemId) {
        try {
          this.tableData = [];
          this.newTableList = [];
          this.tableDataBackup = _.cloneDeep(this.tableData);
          this.aggregationsTableData = _.cloneDeep(this.tableData);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },

      /**
       * 获取系统对应的自定义操作
       *
       * @param {String} systemId 系统id
       * 执行handleActionLinearData方法
       */
      async fetchActions (systemId) {
        const params = {
          system_id: systemId,
          user_id: this.user.username
        };
        if (this.routerQuery.cache_id) {
          params.cache_id = this.routerQuery.cache_id;
        }
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const { code, data } = await this.$store.dispatch('permApply/getActions', params);
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
          this.originalCustomTmplListBackup = _.cloneDeep(data);
          this.originalCustomTmplList = _.cloneDeep(data);
          this.handleActionLinearData();
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },

      handleDisabledClick (payload) {
        const curPermData = this.tableData.find(item => item.id === payload.id);
        if (curPermData) {
          if (curPermData.isExistPermAnimation) {
            return;
          }
          curPermData.isExistPermAnimation = true;
          setTimeout(() => {
            curPermData.isExistPermAnimation = false;
          }, 1500);
        }
      },

      handleReasonInput (payload) {
        this.isShowReasonError = false;
      },

      handleReasonBlur (payload) {
        if (payload === '') {
          this.isShowReasonError = true;
        }
      },
      /**
       * 系统选择回调函数
       *
       * @param {String} 系统id
       * @param {Object} option
       */
      async handleSysSelected (value, option) {
        // 切换系统时重置数据
        this.reason = '';
        this.isShowReasonError = false;
        this.isShowActionError = false;
        this.fetchResetData();
        // await Promise.all([
        //     this.fetchActions(value),
        //     this.fetchPolicies(value),
        //     this.fetchAggregationAction(value),
        //     this.fetchCommonActions(value)
        // ]);
        await this.fetchActions(value);
        await this.fetchActions(value);
        await this.fetchPolicies(value);
        await this.fetchAggregationAction(value);
        await this.fetchCommonActions(value);
      },

      /**
       * 提交权限申请
       */
      async handleApplySubmit () {
        await this.$store.dispatch('userInfo');
        const tableData = this.$refs.resInstanceTableRef.handleGetValue();
        const { actions, flag, aggregations } = tableData;
        if (flag || this.reason === '') {
          this.isShowReasonError = this.reason === '';
          if (actions.length < 1 && aggregations.length < 1) {
            this.isShowActionError = true;
          }
          const tableRef = this.$refs.instanceTableRef;
          const reasonRef = this.$refs.resInstanceReasonRef;
          if (!flag && this.reason === '') {
            this.scrollToLocation(reasonRef);
          } else {
            this.scrollToLocation(tableRef);
          }
          return;
        }
        const systemName = this.systemList.find(item => item.id === this.systemValue).name;
        const params = {
          system: {
            id: this.systemValue,
            name: systemName
          },
          templates: [],
          actions,
          aggregations,
          reason: this.reason
        };
        this.buttonLoading = true;
        try {
          await this.$store.dispatch('applyProvisionPerm/permTemporaryApply', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          if (['admin'].includes(this.user.username)) {
            this.isShowConfirmDialog = true;
          } else {
            this.messageAdvancedError(e);
          }
        } finally {
          this.buttonLoading = false;
        }
      },
      // 申请期限逻辑
      handleDeadlineChange (payload) {
        if (payload) {
          this.isShowExpiredError = false;
        }
        if (payload !== PERMANENT_TIMESTAMP && payload) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex(item => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expiredAtUse = payload + nowSecond;
          return;
        }
        this.expiredAtUse = payload;
      },
      handleExpiredAt () {
        const nowTimestamp = +new Date() / 1000;
        const tempArr = String(nowTimestamp).split('');
        const dotIndex = tempArr.findIndex(item => item === '.');
        const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
        const expiredAt = this.expiredAtUse + nowSecond;
        return expiredAt;
      },
      // 用户组权限提交
      async handleSubmit () {
        let validateFlag = true;
        if (this.reason === '') {
          this.isShowReasonError = true;
          validateFlag = false;
          this.scrollToLocation(this.$refs.reasonRef);
        }
        if (this.expiredAtUse === 0) {
          this.isShowExpiredError = true;
          this.scrollToLocation(this.$refs.expiredAtRef);
          validateFlag = false;
        }
        if (this.currentSelectList.length < 1) {
          this.isShowGroupError = true;
          validateFlag = false;
        }
        if (!validateFlag) {
          return;
        }
        this.buttonLoading = true;
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const params = {
          expired_at: this.expiredAtUse,
          reason: this.reason,
          groups: this.currentSelectList.map(({ id, name, description }) => ({ id, name, description }))
        };
        try {
          await this.$store.dispatch('permApply/applyJoinGroup', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          if (['admin'].includes(this.user.username)) {
            this.isShowConfirmDialog = true;
          } else {
            this.messageAdvancedError(e);
          }
        } finally {
          this.buttonLoading = false;
        }
      },

      /**
       * 取消
       */
      handleCancel () {
        this.$router.push({
          name: 'applyJoinUserGroup'
        });
      },

      /**
       * 去续期
       */
      handleBatchRenewal () {
        this.$router.push({
          name: 'permRenewal',
          query: {
            tab: 'custom'
          }
        });
      },

      fetchResetData () {
        this.isAllExpanded = false;
        this.sysAndtid = false;
        this.aggregationMap = [];
        this.aggregations = [];
        this.aggregationsBackup = [];
        this.aggregationsTableData = [];
        this.actionSearchValue = '';
        this.requestQueue = ['action', 'policy', 'aggregate', 'commonAction'];
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import './index.css';
@import '@/css/mixins/aggregate-action-group.css';
.action-hover {
    color: #3a84ff;
}
.iam-action-cls {
    margin-right: 5px;
    margin-bottom: 5px;
}
.iam-action-hover {
    background: #E7EFFE;
    color: #3a84ff;
}
</style>

<template>
  <div>
    <template v-if="curActionStep === 1">
      <smart-action :class="['iam-action-temp-content-wrapper', { 'is-padding': isEdit }]">
        <render-horizontal-block
          v-if="!isEdit"
          ext-cls="actions-form basic-info-wrapper"
          :label="$t(`m.common['基本信息']`)"
        >
          <div>
            <div class="actions-form-item mb24">
              <div class="actions-form-item-label is-required">{{ $t(`m.common['模板名称']`) }}</div>
              <div class="actions-form-item-content" ref="templateNameRef">
                <bk-input
                  v-model="basicInfo.name"
                  :clearable="true"
                  :style="formatFormItemStyle"
                  :ext-cls="isShowNameError ? 'template-name-error' : ''"
                  @input="handleNameInput"
                  @blur="handleNameBlur"
                />
                <div class="error-tips" v-if="isShowNameError">{{ nameValidateText }}</div>
              </div>
            </div>
            <div class="actions-form-item">
              <div class="actions-form-item-label is-required">{{ $t(`m.common['所属系统']`) }}</div>
              <div class="actions-form-item-content">
                <bk-select
                  v-model="basicInfo.system_id"
                  :style="formatFormItemStyle"
                  :popover-min-width="480"
                  :placeholder="$t(`m.verify['请选择']`)"
                  searchable
                  :clearable="false"
                  @selected="handleSysSelected">
                  <bk-option
                    v-show="!isSystemListLoading"
                    v-for="option in systemList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.displayName"
                  >
                    <span>{{ option.name }}</span>
                    <span style="color: #c4c6cc;">({{ option.id }})</span>
                  </bk-option>
                </bk-select>
              </div>
            </div>
          </div>
          <div class="actions-form-item description-item">
            <div class="actions-form-item-label">{{ $t(`m.memberTemplate['模板描述']`) }}</div>
            <div class="actions-form-item-content">
              <bk-input
                type="textarea"
                v-model="basicInfo.description"
                :maxlength="255"
                ext-cls="iam-create-template-desc-cls"
              />
            </div>
          </div>
        </render-horizontal-block>
        <render-horizontal-block
          ext-cls="actions-form apply-way-wrapper"
          :label="$t(`m.permApply['选择操作']`)"
        >
          <div class="actions-form-item">
            <div class="actions-perm-table" v-bkloading="{ isLoading: customLoading, opacity: 1, zIndex: 1000 }">
              <div class="actions-perm-table-header">
                <div class="action-temp-search">
                  <bk-input
                    v-model="actionsValue"
                    ext-cls="action-temp-search-input"
                    :clearable="true"
                    :placeholder="$t(`m.actionsTemplate['搜索 操作名称']`)"
                    :right-icon="'bk-icon icon-search'"
                    @enter="handleSearchAction"
                    @clear="handleClearSearch"
                    @right-icon-click="handleSearchAction"
                  />
                  <bk-checkbox
                    class="action-temp-search-checkbox"
                    v-model="isSelectAllActions"
                    @change="handleSelectAllActions"
                  >
                    {{ $t(`m.common['全选']`) }}
                  </bk-checkbox>
                </div>
                <div v-if="commonActions.length > 0 && !customLoading" class="common-actions-list">
                  <render-action-tag
                    ref="commonActionRef"
                    :system-id="basicInfo.system_id"
                    :tag-action-list="tagActionList"
                    :data="commonActions"
                    :cur-select-actions="curSelectActions"
                    @on-delete="handleCommonActionDelete"
                    @on-add="handleCommonActionAdd"
                    @on-change="handleActionTagChange"
                  />
                </div>
              </div>
              <div
                ref="actionRef"
                :class="[
                  'iam-action-content-wrapper',
                  { 'set-margin': commonActions.length > 0 }
                ]"
                :style="{ 'height': `${actionContentHeight}px` }"
              >
                <template v-if="isShowAction && !customLoading">
                  <render-action
                    ref="actionsRef"
                    mode="edit"
                    :actions="allCustomActionList"
                    :linear-action="linearAction"
                    @on-select="handleSelectAction"
                  />
                </template>
                <div
                  v-if="!isShowAction && !customLoading"
                  class="empty-wrapper"
                >
                  <ExceptionEmpty
                    :type="emptyActionData.type"
                    :empty-text="emptyActionData.text"
                    :tip-text="emptyActionData.tip"
                    :tip-type="emptyActionData.tipType"
                    @on-clear="handleClearSearch"
                  />
                </div>
              </div>
              <div v-if="isShowActionError" class="error-tips">{{ $t(`m.verify['请选择操作']`) }}</div>
            </div>
            <div class="right-layout">
              <div class="flex-between right-layout-header">
                <div class="right-layout--header-title">{{ $t(`m.common['结果预览']`) }}</div>
              </div>
              <template v-if="curSelectActions.length > 0">
                <div class="flex-between right-layout-item">
                  <div class="right-layout-item-title" @click.stop="handleExpandAction">
                    <Icon bk class="expanded-icon" :type="isExpandAction ? 'down-shape' : 'right-shape'" />
                    <span>{{ $t(`m.common['已选择']`) }}</span>
                    <span class="count">{{ curSelectActions.length }}</span>
                    <span>{{ $t(`m.common['个操作']`) }}</span>
                  </div>
                  <bk-button
                    size="small"
                    theme="primary"
                    :text="true"
                    class="right-layout-item-clear"
                    @click.stop="handleClearAllAction"
                  >
                    {{ $t(`m.common['清空']`) }}
                  </bk-button>
                </div>
                <div
                  v-if="isExpandAction"
                  class="right-layout-content"
                  :style="{ 'height': `${ actionContentHeight + commonActionsHeight }px` }"
                >
                  <div
                    class="flex-between right-layout-content-item"
                    v-for="item in curSelectActions"
                    :key="item.id"
                  >
                    <div class="action-text">
                      <bk-tag class="action-text-tag" :theme="formatTagContent(item, 'theme')">
                        {{ formatTagContent(item, 'text') }}
                      </bk-tag>
                      <div
                        v-bk-tooltips="{ content: item.name, disabled: checkActionWidth(item) }"
                        :ref="`select_actions_${item.id}`"
                        class="single-hide action-text-name"
                      >
                        {{ item.name }}
                      </div>
                    </div>
                    <Icon bk type="close" class="close-icon" @click.stop="handleDelAction(item, [])" />
                  </div>
                </div>
              </template>
              <div v-else class="empty-wrapper">
                <ExceptionEmpty />
              </div>
            </div>
          </div>
        </render-horizontal-block>
        <div slot="action" class="action-footer-btn">
          <template v-if="isEdit">
            <bk-button
              theme="primary"
              :disabled="isCurSelectActions"
              :loading="nextLoading"
              @click.stop="handleNextStep">
              {{ curActionStep > 1 ? $t(`m.common['提交']`) : $t(`m.common['下一步']`) }}
            </bk-button>
            <bk-button @click.stop="handleCancel">
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </template>
          <template v-else>
            <bk-button
              theme="primary"
              :loading="saveLoading"
              @click="handleCreateSubmit">
              {{ $t(`m.common['提交']`) }}
            </bk-button>
            <bk-button
              @click="handleCancel">
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </template>
        </div>
      </smart-action>
    </template>
    <div v-if="curActionStep === 2">
      <RenderSyncGroup
        :id="id"
        :has-related-group="hasGroupPreview"
        :select-actions="curSelectActions"
        :select-actions-back="curSelectActionsBack"
        :all-actions="allCustomActionList"
        :default-checked-actions="defaultCheckedActions"
      />
    </div>
    <!-- 查看组权限实例详情 -->
    <bk-sideslider
      :is-show.sync="instanceDetailSlider.isShow"
      :title="instanceDetailSlider.title"
      :width="instanceDetailSlider.width"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      <div slot="content">
        <component :is="'RenderDetail'" :data="instanceDetailSlider.previewData" />
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, guid } from '@/common/util';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import { addPreUpdateInfo, getActionsData as getHasSelectedActions } from '../common/actions';
  import RenderDetail from '@/views/group/common/render-detail';
  import RenderActionTag from '@/components/common-action';
  import RenderAction from './render-action';
  import RenderSyncGroup from './difference';

  export default {
    components: {
      RenderDetail,
      RenderAction,
      RenderActionTag,
      RenderSyncGroup
    },
    props: {
      id: {
        type: [Number, String],
        default: 0
      },
      mode: {
        type: String,
        default: 'create'
      }
    },
    data () {
      return {
        saveLoading: false,
        nextLoading: false,
        isShowDetailSlider: false,
        isShowNameError: false,
        isShowActionError: false,
        isSystemListLoading: false,
        isSelectAllActions: false,
        isCurSelectActions: true,
        isExpandAction: true,
        hasGroupPreview: false,
        nameValidateText: '',
        initialTempName: '',
        initialDescription: '',
        actionsValue: '',
        systemList: [],
        allCustomActionList: [],
        allCustomActionListBack: [],
        commonActions: [],
        linearAction: [],
        curSelectActions: [],
        curSelectActionsBack: [],
        initialValue: [],
        tagActionList: [],
        defaultCheckedActions: [],
        requestQueue: ['actions', 'commonActions'],
        leavePageForm: {},
        leavePageFormBack: {},
        basicInfo: {
          name: '',
          description: '',
          system_id: '',
          system_name: ''
        },
        instanceDetailSlider: {
          title: '',
          isShow: false,
          width: 960,
          previewData: []
        },
        emptyActionData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        },
        // 跑马灯组件高度
        noticeBarHeight: 40,
        // 基本信息表单高度
        basicInfoHeight: 186,
        actionContentHeight: 0,
        commonActionsHeight: 0,
        curActionStep: 1
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isShowGroupAction () {
        return (item) => {
          const isExistSubGroup = (item.sub_groups || []).some(v => v.sub_groups && v.sub_groups.length > 0);
          return item.sub_groups && item.sub_groups.length > 0 && !isExistSubGroup;
        };
      },
      isEdit () {
        return this.mode === 'edit';
      },
      isShowAction () {
        if (this.allCustomActionList.length) {
          return this.allCustomActionList.some((item) =>
            item.actions.length > 0
            || item.sub_groups.some((v) => v.actions.length > 0 || v.sub_groups.length > 0)
          );
        }
        return false;
      },
      customLoading () {
        return this.requestQueue.length > 0;
      },
      formatFormItemStyle () {
        return {
          width: '480px'
        };
      },
      formatTagContent () {
        return (payload, tagType) => {
          const { flag, tag } = payload;
          const isAdd = ['added'].includes(flag) || ['unchecked'].includes(tag);
          const typeMap = {
            theme: () => {
              return isAdd ? 'success' : 'false';
            },
            text: () => {
              return isAdd ? this.$t(`m.common['新增']`) : this.$t(`m.common['已有']`);
            }
          };
         return typeMap[tagType] ? typeMap[tagType]() : '';
        };
      }
    },
    watch: {
      mode: {
        handler (value) {
          this.requestQueue = ['edit'].includes(value) ? ['detail', 'commonActions'] : ['actions', 'commonActions'];
        },
        immediate: true
      },
      curSelectActions (newValue) {
        this.isCurSelectActions = JSON.stringify(newValue) === JSON.stringify(this.initialValue);
        this.leavePageForm = Object.assign(this.leavePageForm, { selected_actions: newValue });
        if (!newValue.length) {
          this.isSelectAllActions = false;
        }
        if (newValue.length) {
          this.isSelectAllActions = newValue.length === this.linearAction.length;
        }
        this.handleGetLeaveData();
        this.handleGetResizeHeight();
      },
      'basicInfo': {
        handler (payload) {
          this.leavePageForm = Object.assign(this.leavePageForm, payload);
          this.handleGetLeaveData();
        },
        deep: true
      },
      isShowActionError: {
        handler () {
          this.handleGetResizeHeight();
        },
        deep: true
      }
    },
    mounted () {
      const { step } = this.$route.query;
      if (this.$route.query.step) {
        this.handleSetCurActionStep(step);
      }
      this.handleGetBusQueryData();
      this.handleGetResizeHeight();
      window.addEventListener('resize', this.handleGetResizeHeight);
    },
    beforeDestroy () {
      window.removeEventListener('resize', this.handleGetResizeHeight);
    },
    methods: {
      async fetchInitData () {
        this.initialValue = cloneDeep(this.curSelectActions);
        if (this.isEdit) {
          await this.fetchDetail();
          await this.fetchGroupPreview();
          await this.fetchPreUpdateInfo();
        } else {
          await this.fetchSystems();
        }
        // 备份一份数据判断是否有操作变更
        this.curSelectActionsBack = cloneDeep(this.curSelectActions);
        this.leavePageForm = cloneDeep(Object.assign(
          this.basicInfo,
          {
            selected_actions: this.curSelectActions
          }
        ));
        this.leavePageFormBack = cloneDeep(this.leavePageForm);
        this.handleGetLeaveData();
        this.handleGetResizeHeight();
      },

      async fetchGroupPreview () {
        const params = {
          id: this.id,
          types: 'group',
          limit: 10,
          offset: 0
        };
        try {
          const { data } = await this.$store.dispatch('permTemplate/getTemplateMember', params);
          this.hasGroupPreview = data.count > 0;
          this.$store.commit('permTemplate/updatePreGroupOnePage', Math.ceil(data.count / 5) === 1);
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async fetchDetail () {
        try {
          const { data } = await this.$store.dispatch('permTemplate/getTemplateDetail', { id: this.id, grouping: true });
          const { actions, name, description, system } = data;
          this.basicInfo = Object.assign(this.basicInfo, {
            name,
            description,
            system_id: system.id,
            system_name: system.name
          });
          this.initialTempName = cloneDeep(name || '');
          this.initialDescription = cloneDeep(description || '');
          this.allCustomActionList = cloneDeep(actions || []);
          this.$store.commit('setHeaderTitle', name);
          await this.handleActionLinearData(false);
          this.allCustomActionListBack = cloneDeep(this.allCustomActionList);
          await this.fetchCommonActions(system.id || '');
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      async handleCommonActionDelete (id, $id, index) {
        try {
          await this.$store.dispatch('permTemplate/deleteCommonAction', { id });
          this.commonActions.splice(index, 1);
          this.$refs.commonActionRef && this.$refs.commonActionRef.handleSetSelectData($id);
          this.handleGetResizeHeight();
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleCommonActionAdd ({ actions, name }) {
        const actionIds = actions.map((item) => item.id);
        const params = {
          system_id: this.basicInfo.system_id,
          name,
          action_ids: actionIds
        };
        try {
          const { data } = await this.$store.dispatch('permTemplate/addCommonAction', params);
          const addData = {
            ...params,
            id: data.id,
            $id: guid()
          };
          this.commonActions.push(addData);
          this.$refs.commonActionRef && this.$refs.commonActionRef.handleSetActive(addData.$id);
          this.handleGetResizeHeight();
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleActionTagChange (flag, payload) {
        if (payload.length < 1) {
          return;
        }
        this.tagActionList = payload;
        this.handleActionMatchChecked(flag, payload);
        this.handleGetResizeHeight();
      },

      handleActionMatchChecked (flag, payload) {
        this.allCustomActionList.forEach(item => {
          let allCheckedLen = 0;
          let count = 0;
          let delCount = 0;
          let deleteCount = 0;
          item.actions.forEach(subItem => {
            if (!subItem.disabled) {
              if (payload.includes(subItem.id)) {
                if (!subItem.checked && flag) {
                  ++count;
                }
                if (subItem.checked && !flag) {
                  ++delCount;
                }
                subItem.checked = flag;
                this.$set(item, 'expanded', flag);
                this.$refs.actionsRef.handleRelatedActions(subItem, flag);
              }
            }
            if (item.tag === 'delete') {
              ++deleteCount;
            }
            if (item.disabled || item.checked) {
              allCheckedLen++;
            }
          });
          item.allChecked = allCheckedLen === item.actions.length;
          (item.sub_groups || []).forEach(subItem => {
            let allSubCheckedLen = 0;
            (subItem.actions || []).forEach(act => {
              if (!act.disabled) {
                if (payload.includes(act.id)) {
                  if (!act.checked && flag) {
                    ++count;
                  }
                  if (act.checked && !flag) {
                    ++delCount;
                  }
                  act.checked = flag;
                  this.$set(item, 'expanded', flag);
                  this.$refs.actionsRef.handleRelatedActions(act, flag);
                }
              }
              if (item.tag === 'delete') {
                ++deleteCount;
              }
              if (act.disabled || act.checked) {
                allSubCheckedLen++;
              }
            });
            subItem.allChecked = allSubCheckedLen === subItem.actions.length;
          });
          item.actionsAllChecked = item.actions.every(act => act.checked) && (item.sub_groups || []).every(v => {
            return v.actions.every(act => act.checked);
          }
          );
          item.count = flag ? item.count + count : item.count - delCount;
          this.$set(item, 'deleteCount', deleteCount);
          this.$set(item, 'expanded', item.count > 0);
        });
        this.tagActionList = [...payload];
      },

      async fetchSystems () {
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { data } = await this.$store.dispatch('system/getSystems', params);
          (data || []).forEach(item => {
            item.displayName = `${item.name}(${item.id})`;
          });
          this.systemList = data || [];
          if (this.systemList.length) {
            this.basicInfo.system_id = 'bk_job' || data[0].id;
            // 这里必须先调用action获取到所有操作，在判断常用操作里包含了哪些操作
            await this.fetchActions(this.basicInfo.system_id);
            await this.fetchCommonActions(this.basicInfo.system_id);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.isSystemListLoading = false;
        }
      },

      async fetchCommonActions (systemId) {
        try {
          const { data } = await this.$store.dispatch('permTemplate/getCommonAction', { systemId });
          const list = data || [];
          const linearActionIdList = this.linearAction.map((item) => item.id);
          const commonActions = [];
          list.forEach((item) => {
            item.$id = guid();
            if (item.action_ids.every((item) => linearActionIdList.indexOf((item)) > -1)) {
              commonActions.push(item);
            }
          });
          this.commonActions.splice(0, this.commonActions.length, ...commonActions);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      async fetchActions (systemId) {
        const params = {
          system_id: systemId,
          template_id: this.id
        };
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const { data } = await this.$store.dispatch('permApply/getActions', params);
          this.allCustomActionList = cloneDeep(data);
          this.handleActionLinearData();
          this.allCustomActionListBack = cloneDeep(this.allCustomActionList);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },
      
      handleActionLinearData (isSearch = false) {
        const linearActions = [];
        // 获取actions和sub_groups所有数据，并根据单双行渲染不同背景颜色
        let colorIndex = 0;
        this.allCustomActionList.forEach((item, index) => {
          this.$set(item, 'expanded', index === 0);
          let allCount = 0;
          let count = 0;
          let deleteCount = 0;
          this.$set(item, 'count', 0);
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          if (!item.sub_groups) {
            this.$set(item, 'sub_groups', []);
          }
          item.actions = item.actions.filter(v => !v.hidden);
          if (item.actions.length === 1 || !item.sub_groups.length) {
            this.$set(item, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
          }
          if (isSearch) {
            item.actions = item.actions.filter((v) => v.name.indexOf(this.actionsValue) > -1);
          }
          item.actions.forEach(act => {
            this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
            this.$set(act, 'disabled', act.tag === 'readonly');
            linearActions.push(act);
            if (act.checked) {
              this.curSelectActions.push(act);
              this.$set(act, 'flag', 'selected');
              ++count;
              if (act.tag === 'delete') {
                ++deleteCount;
              }
            }
          });
          allCount = allCount + item.actions.length;
          item.sub_groups.forEach(sub => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            this.$set(sub, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions = sub.actions.filter(v => !v.hidden);
            if (isSearch) {
              sub.actions = sub.actions.filter((v) => v.name.indexOf(this.actionsValue) > -1);
            }
            sub.actions.forEach(act => {
              this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
              this.$set(act, 'disabled', act.tag === 'readonly');
              linearActions.push(act);
              if (act.checked) {
                this.curSelectActions.push(act);
                this.$set(act, 'flag', 'selected');
                ++count;
                if (act.tag === 'delete') {
                  ++deleteCount;
                }
              }
            });
            allCount = allCount + sub.actions.length;
            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });
          this.$set(item, 'allCount', allCount);
          this.$set(item, 'count', count);
          this.$set(item, 'deleteCount', deleteCount);
          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
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
        this.linearAction = cloneDeep(linearActions);
      },

      handleSearchAction () {
        this.searchTableData = cloneDeep(this.allCustomActionList);
        this.isShowActionError = false;
        this.emptyActionData.tipType = 'search';
        this.handleRefreshAction(true);
        if (!this.isShowAction) {
          this.emptyActionData = formatCodeData(0, this.emptyActionData, true);
        }
      },

      handleClearSearch () {
        this.emptyActionData.tipType = '';
        this.actionsValue = '';
        this.handleRefreshAction(false);
      },

      handleRefreshAction (payload) {
        const list = cloneDeep(this.allCustomActionListBack);
        this.allCustomActionList = this.getActionsData(list, payload);
      },

      handleExpandAction () {
        this.isExpandAction = !this.isExpandAction;
      },

      async handleSelectAllActions (payload) {
        const modeMap = {
          true: () => {
            if (payload) {
              this.allCustomActionList = this.getActionsData(this.allCustomActionList, false);
            } else {
              this.handleClearAllAction();
            }
          },
          false: () => {
            this.allCustomActionList = this.getActionsData(this.allCustomActionList, false);
          }
        };
        modeMap[this.isEdit]();
      },

      handleClearAllAction () {
        this.isSelectAllActions = false;
        const list = Object.freeze(cloneDeep(this.allCustomActionList));
        this.curSelectActions.forEach((item) => {
          this.handleDelAction(item, list);
        });
      },

      handleNameInput () {
        this.isShowNameError = false;
        this.nameValidateText = '';
      },

      handleNameBlur (payload) {
        const maxLength = 128;
        payload = payload.trim();
        if (payload === '') {
          this.nameValidateText = this.$t(`m.verify['模板名称必填']`);
          this.isShowNameError = true;
        }
        if (!this.isShowNameError) {
          if (payload.trim().length > maxLength) {
            this.nameValidateText = this.$t(`m.verify['模板名称最长不超过128个字符']`);
            this.isShowNameError = true;
          }
        }
      },

      handleSysSelected (value) {
        this.isSelectAllActions = false;
        this.commonActions = [];
        this.linearAction = [];
        this.curSelectActions = [];
        this.curSelectActionsBack = [];
        this.tagActionList = [];
        this.requestQueue = ['actions', 'commonActions'];
        Promise.all([this.fetchActions(value), this.fetchCommonActions(value)]);
      },

      handleSelectAction (payload) {
        this.curSelectActions = [...payload];
        this.tagActionList = [...payload].map((item) => item.id);
        if (payload.length) {
          this.isShowActionError = false;
        }
      },

      handleDelAction (payload, arr) {
        const list = arr.length > 0 ? arr : Object.freeze(cloneDeep(this.allCustomActionListBack));
        list.forEach((item) => {
          (item.actions || []).forEach((act) => {
            if (`${act.id}&${act.name}` === `${payload.id}&${payload.name}`) {
              payload.checked = false;
              this.$refs.actionsRef && this.$refs.actionsRef.handleActionChecked(payload, item, false);
            }
          });
          (item.sub_groups || []).forEach((sub) => {
            sub.actions.forEach((act) => {
              if (`${act.id}&${act.name}` === `${payload.id}&${payload.name}`) {
                payload.checked = false;
                this.$refs.actionsRef && this.$refs.actionsRef.handleSubActionChecked(payload, sub, item, false);
              }
            });
          });
        });
      },

      getActionsData (payload, isSearch = false) {
        // 获取actions和sub_groups所有数据，并根据单双行渲染不同背景颜色
        let colorIndex = 0;
        const temps = cloneDeep(payload);
        temps.forEach((item) => {
          this.$set(item, 'expanded', true);
          let count = 0;
          let allCount = 0;
          let deleteCount = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          if (!item.sub_groups) {
            this.$set(item, 'sub_groups', []);
          }
          if (isSearch) {
            item.actions = item.actions.filter((v) => v.name.indexOf(this.actionsValue) > -1);
          }
          if (item.actions.length === 1 || !item.sub_groups.length) {
            this.$set(item, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
          }
          item.actions.forEach((act) => {
            this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag) || this.isSelectAllActions);
            this.$set(act, 'disabled', ['readonly'].includes(act.tag));
            if (item.actions.length > 1 && item.sub_groups.length > 0) {
              this.$set(act, 'bgColor', colorIndex % 2 === 0 ? '#ffffff' : '#f7f9fc');
              colorIndex++;
            }
            if (act.checked) {
              ++count;
              this.defaultCheckedActions.push(act.id);
            }
            if (act.tag === 'delete') {
              ++deleteCount;
            }
            ++allCount;
          });
          item.sub_groups.forEach((sub) => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            this.$set(sub, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            if (isSearch) {
              sub.actions = sub.actions.filter((v) => v.name.indexOf(this.actionsValue) > -1);
            }
            sub.actions.forEach((act) => {
              this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag) || this.isSelectAllActions);
              this.$set(act, 'disabled', ['readonly'].includes(act.tag));
              if (act.checked) {
                ++count;
                this.defaultCheckedActions.push(act.id);
              }
              if (act.tag === 'delete') {
                ++deleteCount;
              }
              ++allCount;
            });
            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });
          this.$set(item, 'deleteCount', deleteCount);
          this.$set(item, 'count', count);
          this.$set(item, 'allCount', allCount);
          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
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
        return temps;
      },

      async fetchPreUpdateInfo () {
        try {
          const { data } = await this.$store.dispatch('permTemplate/getPreUpdateInfo', { id: this.id });
          const flag = Object.keys(data).length > 0;
          if (flag) {
            const actionIdList = data.action_ids || [];
            const params = {
              id: this.id,
              data: {
                action_ids: actionIdList
              }
            };
            const list = cloneDeep(this.allCustomActionListBack);
            this.$store.commit('permTemplate/updatePreActionIds', actionIdList);
            console.log(getHasSelectedActions(actionIdList, list, this.defaultCheckedActions), 55);
            this.$store.commit('permTemplate/updateAction', getHasSelectedActions(actionIdList, list, this.defaultCheckedActions));
            await addPreUpdateInfo(params);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleNextStep () {
        const nameRef = this.$refs.templateNameRef;
        const actionRef = this.$refs.actionRef;
        const hasDelCount = this.allCustomActionList.some(e => e.deleteCount);
        this.handleNameBlur(this.basicInfo.name);
        this.isShowActionError = this.curSelectActions.length < 1;
        if (this.isShowNameError) {
          this.scrollToLocation(nameRef);
          return;
        }
        if (this.isShowActionError) {
          this.scrollToLocation(actionRef);
          return;
        }
        if (!this.hasGroupPreview) {
          if (hasDelCount) {
            this.messageWarn(this.$t(`m.permTemplate['由于分级管理员的授权范围没有包含此操作，如需使用该模板进行新的授权必须先删除该操作。']`), 3000);
            return;
          }
          window.changeDialog = false;
          this.handleSetCurActionStep(2);
          return;
        }
        // 如果没有操作变更不需要调用接口
        if (JSON.stringify(this.curSelectActionsBack) === JSON.stringify(this.curSelectActions)) {
          return this.messageWarn(this.$t(`m.actionsTemplate['操作模板未变更, 无需更新!']`), 3000);
        }
        this.nextLoading = true;
        try {
          window.changeDialog = false;
          this.handleSetCurActionStep(2);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.nextLoading = false;
        }
      },

      async handleCreateSubmit () {
        const { name, description, system_id } = this.basicInfo;
        this.handleNameBlur(name);
        this.isShowActionError = this.curSelectActions.length < 1;
        const nameRef = this.$refs.templateNameRef;
        const actionRef = this.$refs.actionRef;
        if (this.isShowNameError) {
          this.scrollToLocation(nameRef);
          return;
        }
        if (this.isShowActionError) {
          this.scrollToLocation(actionRef);
          return;
        }
        const params = {
          name,
          description,
          system_id,
          action_ids: this.curSelectActions.map((item) => item.id)
        };
        this.saveLoading = true;
        try {
          await this.$store.dispatch('permTemplate/createTemplate', params);
          this.messageSuccess(this.$t(`m.info['新建操作模板成功']`), 3000);
          this.$router.push({
            name: 'actionsTemplate'
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.saveLoading = false;
        }
      },

      handlePrevStep () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          this.$router.push({
            name: 'actionsTemplate'
          });
        }, _ => _);
      },

      handleCancel () {
        this.handleGetLeaveData();
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          window.changeDialog = false;
          this.$router.push({
            name: 'actionsTemplate'
          });
        }, _ => _);
      },

      handleGetLeaveData () {
        window.changeDialog = JSON.stringify(this.leavePageForm) !== JSON.stringify(this.leavePageFormBack);
      },

      handleGetResizeHeight () {
        // 两个51代表面包屑和导航栏的高度， 186代表基本信息的高度， 48代表底footer高度
        const distance = window.innerHeight - 51 - 51 - 48;
        let listHeight = this.isEdit ? distance - 100 : distance - this.basicInfoHeight - 126;
        if (this.isShowActionError) {
          listHeight -= 32;
        }
        if (this.isShowNoticeAlert) {
          listHeight = listHeight - this.noticeBarHeight;
        }
        if (this.commonActions.length > 0 && this.$refs.commonActionRef) {
          setTimeout(() => {
            this.commonActionsHeight = this.$refs.commonActionRef.$el.offsetHeight;
            this.actionContentHeight = listHeight - this.commonActionsHeight;
          }, 0);
        } else {
          this.actionContentHeight = listHeight;
        }
      },

      handleGetBusQueryData () {
        bus.$on('on-drawer-side', (payload) => {
          this.instanceDetailSlider = Object.assign(this.instanceDetailSlider, payload);
        });
        this.$once('hook:beforeDestroy', () => {
          bus.$off('on-drawer-side');
        });
      },

      handleSetCurActionStep (payload) {
        payload = Number(payload);
        this.curActionStep = payload;
        window.history.replaceState({}, '', `?${buildURLParams({ step: payload })}`);
        bus.$emit('on-action-temp-step-change', { step: payload });
      },

      checkActionWidth (payload) {
        this.$nextTick(() => {
          const selectActions = this.$refs[`select_actions_${payload.id}`];
          if (selectActions && selectActions.length) {
            const offsetWidth = selectActions[0].offsetWidth;
            return !(offsetWidth > 134);
          }
        });
      },

      handleAnimationEnd () {
        this.instanceDetailSlider = Object.assign(this.instanceDetailSlider, { isShow: false, sideSliderDetailTitle: '', previewData: [] });
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '../css/render-content.css';
</style>

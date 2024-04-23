<template>
  <smart-action class="iam-action-temp-content-wrapper">
    <render-horizontal-block v-if="!isEdit" ext-cls="actions-form basic-info-wrapper" :label="$t(`m.common['基本信息']`)">
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
      :style="{ 'max-height': `${actionContentHeight}px` }"
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
            <render-action-tag
              v-if="commonActions.length > 0 && !customLoading"
              ref="commonActionRef"
              style="margin-top: 12px;"
              :system-id="basicInfo.system_id"
              :tag-action-list="tagActionList"
              :data="commonActions"
              :cur-select-actions="curSelectActions"
              @on-delete="handleCommonActionDelete"
              @on-add="handleCommonActionAdd"
              @on-change="handleActionTagChange"
            />
          </div>
          <div
            ref="actionRef"
            :class="[
              'iam-action-content-wrapper',
              { 'set-margin': commonActions.length > 0 }
            ]"
            :style="{ 'height': `${actionContentHeight}px` }"
          >
            <render-action
              v-if="isShowAction && !customLoading"
              ref="actionsRef"
              mode="edit"
              :actions="originalCustomTmplList"
              :linear-action="linearAction"
              @on-select="handleSelect"
            />
            <div
              v-if="!isShowAction && !customLoading"
              class="empty-wrapper"
            >
              <ExceptionEmpty
                :type="emptyActionData.type"
                :empty-text="emptyActionData.text"
                :tip-text="emptyActionData.tip"
                :tip-type="emptyActionData.tipType"
                @on-clear="handleClear"
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
              :style="{ 'height': `${actionContentHeight - 43}px` }"
            >
              <div
                class="flex-between right-layout-content-item"
                v-for="item in curSelectActions"
                :key="item.id"
              >
                <div class="action-text">
                  <bk-tag class="action-text-tag" :theme="item.flag === 'added' ? 'success' : 'danger'">
                    {{ item.flag === 'added' ? $t(`m.common['新增']`) : $t(`m.common['移除']`) }}
                  </bk-tag>
                  <div :class="[
                    'single-hide action-text-name',
                    { 'lang-name': !curLanguageIsCn }
                  ]">
                    {{ item.name }}
                  </div>
                </div>
                <Icon bk type="close" class="close-icon" />
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
          :disabled="isCurSelectActions && isTempName && isDescription"
          :loading="nextLoading"
          @click="handleNextStep">
          {{ hasGroupPreview ? $t(`m.common['下一步']`) : $t(`m.common['提交']`) }}
        </bk-button>
        <bk-button
          :loading="prevLoading"
          @click="handlePrevStep">
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

<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData, guid } from '@/common/util';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import RenderActionTag from '@/components/common-action';
  import RenderAction from './render-action';

  export default {
    inject: ['showNoticeAlert'],
    components: {
      RenderActionTag,
      RenderAction
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
        prevLoading: false,
        isShowNameError: false,
        isShowActionError: false,
        isEditTemplate: false,
        isSystemListLoading: false,
        isSelectAllActions: false,
        isTempName: true,
        isDescription: true,
        isCurSelectActions: true,
        isExpandAction: true,
        hasGroupPreview: true,
        nameValidateText: '',
        initialTempName: '',
        initialDescription: '',
        actionsValue: '',
        systemList: [],
        originalCustomTmplList: [],
        originalCustomTmplListBack: [],
        commonActions: [],
        linearAction: [],
        curSelectActions: [],
        nextRequestQueue: [],
        initialValue: [],
        tagActionList: [],
        defaultCheckedActions: [],
        requestQueue: ['actions', 'commonActions'],
        basicInfo: {
          name: '',
          description: '',
          system_id: '',
          system_name: ''
        },
        leavePageForm: {},
        leavePageFormBack: {},
        emptyActionData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        // 跑马灯组件高度
        noticeBarHeight: 40,
        // 基本信息表单高度
        basicInfoHeight: 186,
        // 两个51代表面包屑和导航栏的高度， 186代表基本信息的高度， 30代表内边距
        actionContentHeight: 0
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
        if (this.originalCustomTmplList.length) {
          return this.originalCustomTmplList.some((item) =>
            item.actions.length > 0
            || item.sub_groups.some((v) => v.actions.length > 0 || v.sub_groups.length > 0)
          );
        }
        return false;
      },
      customLoading () {
        return this.requestQueue.length > 0;
      },
      nextLoading () {
        return this.nextRequestQueue.length > 0;
      },
      formatFormItemStyle () {
        return {
          width: '480px'
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
      curSelectActions (newValue, oldValue) {
        this.isEditTemplate = oldValue.length !== newValue.length;
        this.isCurSelectActions = JSON.stringify(newValue) === JSON.stringify(this.initialValue);
        this.leavePageForm = Object.assign(this.leavePageForm, { selected_actions: newValue });
        this.handleGetLeaveData();
      },
      'basicInfo': {
        handler (payload) {
          const { name, description } = payload;
          this.isTempName = name === this.initialTempName;
          this.isDescription = description === this.initialDescription;
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
      this.handleGetResizeHeight();
      window.addEventListener('resize', this.handleGetResizeHeight);
    },
    beforeDestroy () {
      window.removeEventListener('resize', this.handleGetResizeHeight);
    },
    methods: {
      async fetchPageData () {
        this.initialValue = cloneDeep(this.curSelectActions);
        if (this.isEdit) {
          await this.fetchDetail();
          await this.fetchGroupPreview();
        } else {
          await this.fetchSystems();
        }
        this.leavePageForm = cloneDeep(this.basicInfo, {
          selected_actions: this.curSelectActions
        });
        this.leavePageFormBack = cloneDeep(this.leavePageForm);
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
          this.originalCustomTmplList = cloneDeep(actions || []);
          this.originalCustomTmplListBack = cloneDeep(actions || []);
          await this.handleActionLinearData(false);
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
      },

      handleActionMatchChecked (flag, payload) {
        this.originalCustomTmplList.forEach(item => {
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
          this.basicInfo.system_id = 'bk_cmdb' || (data && data.length ? data[0].id : '');
          if (this.basicInfo.system_id) {
            Promise.all([
              this.fetchActions(this.basicInfo.system_id),
              this.fetchCommonActions(this.basicInfo.system_id)
            ]);
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
          const linearActionIdList = this.linearAction.map(la => la.id);
          const commonActions = [];
          list.forEach((item) => {
            item.$id = guid();
            if (item.action_ids.every(aId => linearActionIdList.indexOf(aId) > -1)) {
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
          this.originalCustomTmplList = cloneDeep(data);
          this.originalCustomTmplListBack = cloneDeep(data);
          this.handleActionLinearData();
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
        this.originalCustomTmplList.forEach((item, index) => {
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
          // item.actions = item.actions.filter(v => !v.hidden);
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
              this.curSelectActions.push(act.id);
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
            // sub.actions = sub.actions.filter(v => !v.hidden);
            if (isSearch) {
              sub.actions = sub.actions.filter((v) => v.name.indexOf(this.actionsValue) > -1);
            }
            sub.actions.forEach(act => {
              this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
              this.$set(act, 'disabled', act.tag === 'readonly');
              linearActions.push(act);
              if (act.checked) {
                this.curSelectActions.push(act.id);
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
        this.originalCustomTmplList = cloneDeep(this.originalCustomTmplListBack);
        this.handleActionLinearData(payload);
      },

      handleExpandAction () {
        this.isExpandAction = !this.isExpandAction;
      },

      async handleSelectAllActions () {
        this.originalCustomTmplList = this.getActionsData(this.originalCustomTmplList, false);
      },

      handleClearAllAction () {
        this.isSelectAllActions = false;
        this.originalCustomTmplList = this.getActionsData(this.originalCustomTmplList, false);
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
        this.commonActions = [];
        this.linearAction = [];
        this.curSelectActions = [];
        this.tagActionList = [];
        this.requestQueue = ['actions', 'commonActions'];
        Promise.all([this.fetchActions(value), this.fetchCommonActions(value)]);
      },

      handleSelect (payload) {
        this.curSelectActions = [...payload];
        this.tagActionList = [...payload].map((item) => item.id);
        this.isShowActionError = !(payload.length > 0);
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

      async handleUpdateCommit () {
        try {
          await this.$store.dispatch('permTemplate/updateCommit', {
            id: this.id
          });
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'success',
            message: this.$t(`m.info['提交成功']`)
          });
          this.$router.push({
            name: 'actionsTemplate'
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.nextRequestQueue.shift();
        }
      },

      async editTemplate () {
        try {
          const { name, description } = this.basicInfo;
          await this.$store.dispatch('permTemplate/updateTemplate', {
            name: name.trim(),
            description,
            id: this.id
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.nextRequestQueue.shift();
        }
      },

      async handleNextStep () {
        if (!this.hasGroupPreview && this.originalCustomTmplList.some(e => e.deleteCount)) {
          this.messageWarn(this.$t(`m.permTemplate['由于分级管理员的授权范围没有包含此操作，如需使用该模板进行新的授权必须先删除该操作。']`), 3000);
          return;
        }
        this.handleNameBlur(this.basicInfo.name);
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
        this.nextRequestQueue = ['edit', 'addPre'];
        // 如果编辑中修改的是模板名称和描述
        if (!this.isEditTemplate) {
          await this.editTemplate();
          this.$router.push({
            name: 'permTemplateDetail',
            params: this.$route.params
          });
        } else {
          try {
            await this.editTemplate();
            const { data } = await this.$store.dispatch('permTemplate/addPreUpdateInfo', {
              id: this.id,
              data: {
                action_ids: this.curSelectActions
              }
            });
            if (!this.hasGroupPreview) {
              this.nextRequestQueue = ['addPre', 'updateCommit'];
              this.handleUpdateCommit();
              return;
            }
            this.$store.commit('permTemplate/updateCloneActions', data);
            this.$store.commit('permTemplate/updatePreActionIds', this.curSelectActions);
            this.$store.commit('permTemplate/updateAction', this.getActionsData(this.originalCustomTmplList, false));
            this.$router.push({
              name: 'actionsTemplateDiff',
              params: this.$route.params
            });
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          } finally {
            this.nextRequestQueue.shift();
          }
        }
      },

      async handlePrevStep () {
        // let cancelHandler = Promise.resolve();
        // window.changeDialog = JSON.stringify(this.leavePageForm) !== JSON.stringify(this.leavePageFormBack);
        // if (window.changeDialog) {
        //   cancelHandler = leavePageConfirm();
        // }
        // cancelHandler.then(async () => {
        //   this.$router.push({
        //     name: 'permTemplateDetail',
        //     params: this.$route.params
        //   });
        // }, _ => _);
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

      handleCancel () {
        let cancelHandler = Promise.resolve();
        this.handleGetLeaveData();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          this.$router.push({
            name: 'actionsTemplate'
          });
        }, _ => _);
      },

      handleGetLeaveData () {
        window.changeDialog = JSON.stringify(this.leavePageForm) !== JSON.stringify(this.leavePageFormBack);
      },

      handleGetResizeHeight () {
        const distance = window.innerHeight - 51 - 51 - 52 - 30 - 120;
        let listHeight = this.isEdit ? distance - 30 : distance - this.basicInfoHeight;
        if (this.isShowActionError) {
          listHeight = listHeight - 18;
        }
        if (this.isShowNoticeAlert) {
          this.actionContentHeight = listHeight - this.noticeBarHeight;
          return;
        }
        this.actionContentHeight = listHeight;
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '../css/render.content.css';
</style>

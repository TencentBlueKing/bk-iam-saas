<template>
  <smart-action class="iam-pem-tempalte-content-wrapper">
    <render-horizontal-block
      :label="$t(`m.common['基本信息']`)">
      <div class="bk-form bk-form-vertical inner-content">
        <div class="bk-form-item is-required">
          <label class="bk-label">
            <span>{{ $t(`m.common['模板名称']`) }}</span>
          </label>
          <div class="bk-form-content" ref="templateNameRef" style="margin-left: 200px;">
            <bk-input
              v-model="tempName"
              style="width: 450px;"
              data-test-id="permTemplate_input_templateName"
              clearable
              :placeholder="$t(`m.common['模板名称可随时修改']`)"
              :ext-cls="isShowNameError ? 'tempalte-name-error' : ''"
              @input="handleNameInput"
              @blur="handleNameBlur">
            </bk-input>
            <p class="error-tips mt5" v-if="isShowNameError">{{ nameValidateText }}</p>
          </div>
        </div>
        <div class="bk-form-item is-required">
          <label class="bk-label">
            <span>{{ $t(`m.common['所属系统']`) }}</span>
          </label>
          <div class="bk-form-content" style="margin-left: 200px;">
            <bk-select
              v-if="!isEdit"
              v-model="systemValue"
              data-test-id="permTemplate_select_system"
              style="width: 450px;"
              :popover-min-width="450"
              :placeholder="$t(`m.verify['请选择']`)"
              searchable
              :clearable="false"
              @selected="handleSysSelected">
              <div
                v-show="isSystemListLoading"
                style="height: 200px;"
                v-bkloading="{ isLoading: isSystemListLoading, zIndex: 10 }">
              </div>
              <bk-option v-show="!isSystemListLoading" v-for="option in systemList"
                :key="option.id"
                :id="option.id"
                :name="option.displayName"
                :data-test-id="`permTemplate_selectOption_system_${option.id}`">
                <span>{{ option.name }}</span>
                <span style="color: #c4c6cc;">({{ option.id }})</span>
              </bk-option>
              <!-- <div slot="extension" class="select-extension-wrapper">
                                <div class="left" @click.stop="handleSkip" v-if="user.role.type === 'rating_manager'">
                                    <i class="iam-icon iamcenter-edit-fill mr5"></i>{{ $t(`m.grading['修改分级管理员授权范围']`) }}
                                </div>
                                <div class="right" @click.stop="refreshList">
                                    <i class="iam-icon iamcenter-refresh mr5"></i>{{ $t(`m.grading['刷新列表']`) }}
                                </div>
                            </div> -->
            </bk-select>
            <bk-input v-model="systemName" disabled style="width: 450px;" v-else></bk-input>
          </div>
        </div>
        <div class="bk-form-item">
          <label class="bk-label">
            <span>{{ $t(`m.common['描述']`) }}</span>
          </label>
          <div class="bk-form-content" style="margin-left: 200px;">
            <bk-input
              type="textarea"
              v-model="description"
              :maxlength="255"
              ext-cls="iam-create-template-desc-cls"
              @input="handleDescInput">
            </bk-input>
          </div>
        </div>
      </div>
    </render-horizontal-block>
    <render-horizontal-block ext-cls="apply-way-wrapper" :required="true" :label="$t(`m.permApply['选择操作']`)">
      <div class="bk-form bk-form-vertical">
        <div class="bk-form-item" style="margin-top: 0;"
          v-bkloading="{ isLoading: customLoading, opacity: 1, zIndex: 1000 }">
          <render-action-tag
            ref="commonActionRef"
            style="margin-top: 0;"
            :system-id="systemValue"
            :tag-action-list="tagActionList"
            :data="commonActions"
            :cur-select-actions="curSelectActions"
            v-if="!customLoading"
            @on-delete="handleCommonActionDelete"
            @on-add="handleCommonActionAdd"
            @on-change="handleActionTagChange" />
          <div :class="['iam-action-content-wrapper', { 'is-loading': customLoading }]" ref="actionRef">
            <render-action
              ref="actionsRef"
              v-if="originalCustomTmplList.length > 0 && !customLoading"
              :actions="originalCustomTmplList"
              :linear-action="linearAction"
              mode="edit"
              @on-select="handleSelect" />
            <div class="empty-wrapper"
              v-if="originalCustomTmplList.length < 1 && !customLoading">
              <Icon type="warning" />
              {{ $t(`m.permApply['暂无可申请的操作']`) }}
            </div>
          </div>
          <p v-if="isShowActionError" class="error-tips mt mb10">{{ $t(`m.verify['请选择操作']`) }}</p>
        </div>
      </div>
    </render-horizontal-block>
    <div slot="action">
      <template v-if="isEdit">
        <bk-button
          theme="primary"
          :disabled="isCurSelectActions && isTempName && isDescription"
          :loading="nextLoading"
          @click="handleNextStep">
          {{ hasGroupPreview ? $t(`m.common['下一步']`) : $t(`m.common['提交']`) }}
        </bk-button>
        <bk-button
          style="margin-left: 10px;"
          :loading="prevLoading"
          @click="handlePrevStep">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </template>
      <template v-else>
        <bk-button
          theme="primary"
          :loading="saveLoading"
          data-test-id="permTemplate_btn_createSubmit"
          @click="handleCreateSubmit">
          {{ $t(`m.common['提交']`) }}
        </bk-button>
        <bk-button
          style="margin-left: 10px;"
          @click="handleCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </template>
    </div>
  </smart-action>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { guid } from '@/common/util';
  import { bus } from '@/common/bus';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import RenderActionTag from '@/components/common-action';
  import RenderAction from './render-action';

  export default {
    name: '',
    components: {
      RenderActionTag,
      RenderAction
    },
    props: {
      id: {
        type: Number,
        default: 0
      },
      mode: {
        type: String,
        default: 'create'
      }
    },
    data () {
      return {
        tempName: '',
        nameValidateText: '',
        isShowNameError: false,
        systemValue: '',
        systemList: [],
        saveLoading: false,
        originalCustomTmplList: [],
        description: '',
        commonActions: [],
        requestQueue: ['actions', 'commonActions'],
        linearAction: [],
        curSelectActions: [],
        systemName: '',
        isShowActionError: false,
        prevLoading: false,
        hasGroupPreview: true,
        nextRequestQueue: [],
        isEditTemplate: false,
        isCurSelectActions: true,
        isTempName: true,
        isDescription: true,
        initialValue: [],
        initialTempName: '',
        initialDescription: '',
        tagActionList: [],
        isSystemListLoading: false
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
            customLoading () {
                return this.requestQueue.length > 0;
            },
            isEdit () {
                return this.mode === 'edit';
            },
            nextLoading () {
                return this.nextRequestQueue.length > 0;
            }
    },
    watch: {
      mode: {
        handler (value) {
          if (value === 'edit') {
            this.requestQueue = ['detail', 'commonActions'];
          } else {
            this.requestQueue = ['actions', 'commonActions'];
          }
        },
        immediate: true
      },
      curSelectActions (newValue, value) {
        if (value.length > 0) {
          this.isShowActionError = false;
        }
        if (value.length !== newValue.length) {
          this.isEditTemplate = true;
        }
        if (newValue.toString() !== this.initialValue.toString()) {
          this.isCurSelectActions = false;
        } else {
          this.isCurSelectActions = true;
        }
      },
      tempName (newValue) {
        if (newValue.toString() !== this.initialTempName.toString()) {
          this.isTempName = false;
        } else {
          this.isTempName = true;
        }
      },
      description (newValue) {
        if (newValue.toString() !== this.initialDescription.toString()) {
          this.isDescription = false;
        } else {
          this.isDescription = true;
        }
      }
    },
    created () {
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
      this.initialValue = this.curSelectActions;
    },
    methods: {
      async fetchPageData () {
        if (this.isEdit) {
          await this.fetchDetail();
          await this.fetchGroupPreview();
        } else {
          await this.fetchSystems();
        }
      },

      async fetchGroupPreview () {
        const params = {
          id: this.id,
          types: 'group',
          limit: 10,
          offset: 0
        };
        try {
          const res = await this.$store.dispatch('permTemplate/getTemplateMember', params);
          this.hasGroupPreview = res.data.count > 0;
          this.$store.commit('permTemplate/updatePreGroupOnePage', Math.ceil(res.data.count / 5) === 1);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      async fetchDetail () {
        try {
          const res = await this.$store.dispatch('permTemplate/getTemplateDetail', { id: this.id, grouping: true });
          this.tempName = res.data.name;
          this.systemValue = res.data.system.id;
          this.description = res.data.description;
          this.systemName = res.data.system.name;
          this.originalCustomTmplList = _.cloneDeep(res.data.actions);
          await this.handleActionLinearData();
          await this.fetchCommonActions(this.systemValue);
          this.initialTempName = this.tempName;
          this.initialDescription = this.description;
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.requestQueue.shift();
        }
      },

      async handleCommonActionDelete (id, $id, index) {
        window.changeDialog = true;
        try {
          await this.$store.dispatch('permTemplate/deleteCommonAction', { id });
          this.commonActions.splice(index, 1);
          this.$refs.commonActionRef && this.$refs.commonActionRef.handleSetSelectData($id);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      async handleCommonActionAdd ({ actions, name }) {
        window.changeDialog = true;
        const params = {
          system_id: this.systemValue,
          name,
          action_ids: actions
        };
        try {
          const res = await this.$store.dispatch('permTemplate/addCommonAction', params);
          const addData = {
                        ...params,
                        id: res.data.id,
                        $id: guid()
          };
          this.commonActions.push(addData);
          this.$refs.commonActionRef && this.$refs.commonActionRef.handleSetActive(addData.$id);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      handleActionTagChange (flag, payload) {
        window.changeDialog = true;
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
          // const haveActions = item.actions.filter(v => v.id);
          // const haveActionsChecked = !!item.actions.find(v => v.checked === true);
          // this.$set(item, 'expanded', haveActionsChecked);
          // if (!flag && haveActions) {
          //     // const isExpand = [...haveActions].filter(v => payload.includes(v));
          //     this.$set(item, 'expanded', haveActionsChecked);
          // }
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
            // const haveGroupActions = subItem.actions.filter(v => v.id);
            // const haveGroupActionsChecked = !!subItem.actions.find(v => v.checked === true);
            subItem.allChecked = allSubCheckedLen === subItem.actions.length;
            // if (!flag && haveGroupActions) {
            //     this.$set(item, 'expanded', haveGroupActionsChecked);
            // }
          });
          item.actionsAllChecked = item.actions.every(act => act.checked) && (item.sub_groups || []).every(
            v => {
              return v.actions.every(act => act.checked);
            }
          );

          if (flag) {
            item.count = item.count + count;
          } else {
            item.count = item.count - delCount;
          }
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
          this.systemValue = data && data.length ? data[0].id : '';
          if (this.systemValue) {
            await this.fetchActions(this.systemValue);
            await this.fetchCommonActions(this.systemValue);
          }
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.isSystemListLoading = false;
        }
      },

      handleActionLinearData () {
        const linearActions = [];
        this.originalCustomTmplList.forEach((item, index) => {
          this.$set(item, 'expanded', index === 0);
          let allCount = 0;
          let count = 0;
          let deleteCount = 0;
          this.$set(item, 'count', 0);
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          item.actions = item.actions.filter(v => !v.hidden);
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
          (item.sub_groups || []).forEach(sub => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions = sub.actions.filter(v => !v.hidden);
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
        this.linearAction = _.cloneDeep(linearActions);
      },

      async fetchCommonActions (systemId) {
        try {
          const res = await this.$store.dispatch('permTemplate/getCommonAction', { systemId });
          const list = res.data || [];

          const linearActionIdList = this.linearAction.map(la => la.id);
          const commonActions = [];
          list.forEach(ca => {
            ca.$id = guid();
            if (ca.action_ids.every(aId => linearActionIdList.indexOf(aId) > -1)) {
              commonActions.push(ca);
            }
          });
          this.commonActions.splice(0, this.commonActions.length, ...commonActions);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
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
          const res = await this.$store.dispatch('permApply/getActions', params);
          this.originalCustomTmplList = _.cloneDeep(res.data);
          this.handleActionLinearData();
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.requestQueue.shift();
        }
      },

      handleNameInput () {
        window.changeDialog = true;
        this.isShowNameError = false;
        this.nameValidateText = '';
      },

      handleDescInput () {
        window.changeDialog = true;
      },

      handleNameBlur (payload) {
        const maxLength = 128;
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

      async handleSysSelected (value, option) {
        window.changeDialog = true;
        this.commonActions = [];
        this.linearAction = [];
        this.curSelectActions = [];
        this.tagActionList = [];
        this.requestQueue = ['actions', 'commonActions'];
        await this.fetchActions(value);
        await this.fetchCommonActions(value);
      },

      handleSelect (payload) {
        this.curSelectActions = [...payload];
        this.tagActionList = [...payload];
      },

      getActionsData (payload) {
        const temps = _.cloneDeep(payload);
        temps.forEach(item => {
          let count = 0;
          let deleteCount = 0;
          item.actions.forEach(act => {
            if (act.checked) {
              ++count;
              if (act.tag === 'delete') {
                ++deleteCount;
              }
            }
          })
          ;(item.sub_groups || []).forEach(sub => {
            sub.actions.forEach(act => {
              if (act.checked) {
                ++count;
                if (act.tag === 'delete') {
                  ++deleteCount;
                }
              }
            });
          });
          this.$set(item, 'count', count);
          this.$set(item, 'deleteCount', deleteCount);
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
            name: 'permTemplate'
          });
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.nextRequestQueue.shift();
        }
      },

      async editTemplate () {
        try {
          await this.$store.dispatch('permTemplate/updateTemplate', {
            name: this.tempName.trim(),
            description: this.description,
            id: this.id
          });
          window.localStorage.setItem('iam-header-title-cache', this.tempName);
          window.localStorage.setItem('iam-header-name-cache', this.tempName);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.nextRequestQueue.shift();
        }
      },

      async handleNextStep () {
        if (!this.hasGroupPreview && this.originalCustomTmplList.some(e => e.deleteCount)) {
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: '由于分级管理员的授权范围没有包含此操作，如需使用该模板进行新的授权必须先删除该操作。',
            ellipsisLine: 2,
            ellipsisCopy: true
          });
          return;
        }
        this.handleNameBlur(this.tempName);
        this.isShowActionError = this.curSelectActions.length < 1;
        if (this.isShowNameError || this.isShowActionError) {
          const nameRef = this.$refs.templateNameRef;
          const actionRef = this.$refs.actionRef;
          if (this.isShowNameError) {
            this.scrollToLocation(nameRef);
          }
          if (!this.isShowNameError && this.isShowActionError) {
            this.scrollToLocation(actionRef);
          }
          return;
        }
        this.nextRequestQueue = ['edit', 'addPre'];
        // 如果编辑中修改的是模板名称和描述
        if (!this.isEditTemplate) {
          await this.editTemplate();
          window.changeDialog = false;
          this.$router.push({
            name: 'permTemplateDetail',
            params: this.$route.params
          });
        } else {
          try {
            await this.editTemplate();
            const res = await this.$store.dispatch('permTemplate/addPreUpdateInfo', {
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
            this.$store.commit('permTemplate/updateCloneActions', res.data);
            this.$store.commit('permTemplate/updatePreActionIds', this.curSelectActions);
            this.$store.commit('permTemplate/updateAction', this.getActionsData(this.originalCustomTmplList));
            window.changeDialog = false;
            this.$router.push({
              name: 'permTemplateDiff',
              params: this.$route.params
            });
          } catch (e) {
            console.error(e);
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText
            });
          } finally {
            this.nextRequestQueue.shift();
          }
        }
      },
      async handlePrevStep () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(async () => {
          this.$router.push({
            name: 'permTemplateDetail',
            params: this.$route.params
          });
        }, _ => _);
      },

      async handleCreateSubmit () {
        this.handleNameBlur(this.tempName);
        this.isShowActionError = this.curSelectActions.length < 1;
        if (this.isShowNameError || this.isShowActionError) {
          const nameRef = this.$refs.templateNameRef;
          const actionRef = this.$refs.actionRef;
          if (this.isShowNameError) {
            this.scrollToLocation(nameRef);
          }
          if (!this.isShowNameError && this.isShowActionError) {
            this.scrollToLocation(actionRef);
          }
          return;
        }
        const params = {
          name: this.tempName,
          system_id: this.systemValue,
          action_ids: this.curSelectActions,
          description: this.description
        };
        this.saveLoading = true;
        try {
          await this.$store.dispatch('permTemplate/createTemplate', params);
          this.messageSuccess(this.$t(`m.info['新建权限模板成功']`), 1000);
          bus.$emit('show-guide', 'group');
          window.changeDialog = false;
          this.$router.push({
            name: 'permTemplate'
          });
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.saveLoading = false;
        }
      },

      handleCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          this.$router.push({
            name: 'permTemplate'
          });
        }, _ => _);
      },

      async handleSkip () {
        // 跳转至我的分级管理员
        bus.$emit('nav-change', { id: this.$store.getters.navCurRoleId }, 0);
        await this.$store.dispatch('role/updateCurrentRole', { id: 0 });
        if (this.user.role.type === 'rating_manager') {
          const routeData = this.$router.resolve({ path: `${this.$store.getters.navCurRoleId}/rating-manager-edit`, params: { id: this.$store.getters.navCurRoleId } });
          window.open(routeData.href, '_blank');
        }
      },

      refreshList () {
        this.isSystemListLoading = true;
        this.fetchSystems();
      }
    }
  };
</script>

<style lang="postcss" scoped>
    .iam-pem-tempalte-content-wrapper {
        position: relative;
        font-size: 14px;
        .iam-create-template-desc-cls {
            .bk-form-textarea {
                margin-bottom: 0;
                min-height: 60px;
            }
        }
        .apply-way-wrapper {
            position: relative;
            padding: 30px 30px 5px 30px !important;
            .expanded-wrapper {
                transform: translateX(-50%);
                position: absolute;
                bottom: -10px;
                left: 50%;
                width: 200px;
                height: 10px;
                border-radius: 0 0 6px 6px;
                background: #dcdee5;
                text-align: center;
                cursor: pointer;
                .expand-icon {
                    display: block;
                    margin-top: -3px;
                    font-size: 16px;
                }
            }
        }

        .belong-system {
            .icon-angle-down {
                font-size: 14px;
            }
        }
        .tempalte-name-error {
            .bk-form-input {
                border-color: #ff5656;
            }
        }
        .error-tips {
            position: relative;
            font-size: 12px;
            color: #ff4d4d;
            top: 0;
            &.mt {
                margin-top: 10px;
            }
        }

        .iam-action-content-wrapper {
            position: relative;
            &.is-loading {
                min-height: 200px;
            }
            .empty-wrapper {
                margin-top: 14px;
                font-size: 12px;
                i {
                    position: relative;
                    top: -1px;
                }
            }
        }
    }

    .bk-select-extension .select-extension-wrapper {
        display: flex;
        text-align: center;
        position: relative;

        .left {
            flex: 1;
            cursor: pointer;
            &::after {
                content: '';
                position: absolute;
                width: 1px;
                height: 18px;
                top: 7px;
                right: calc(50% - 16px);
                background: #dcdee5;
            }
        }
        .right {
            flex: 1;
            cursor: pointer;
        }
    }
</style>

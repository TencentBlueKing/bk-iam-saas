<template>
  <smart-action class="iam-action-temp-content-wrapper">
    <render-horizontal-block ext-cls="actions-form basic-info-wrapper" :label="$t(`m.common['基本信息']`)">
      <div>
        <div class="actions-form-item">
          <div class="actions-form-item-label is-required">{{ $t(`m.common['模板名称']`) }}</div>
          <div class="actions-form-item-content" ref="templateNameRef">
            <bk-input
              v-model="basicInfo.name"
              style="width: 480px;"
              clearable
              :placeholder="$t(`m.common['请输入']`)"
              :ext-cls="isShowNameError ? 'template-name-error' : ''"
              @input="handleNameInput"
              @blur="handleNameBlur"
            />
            <p class="error-tips mt5" v-if="isShowNameError">{{ nameValidateText }}</p>
          </div>
        </div>
        <div class="actions-form-item">
          <div class="actions-form-item-label is-required">{{ $t(`m.common['所属系统']`) }}</div>
          <div class="actions-form-item-content">
            <bk-select
              v-if="!isEdit"
              v-model="basicInfo.system_id"
              style="width: 480px;"
              :popover-min-width="480"
              :placeholder="$t(`m.verify['请选择']`)"
              searchable
              :clearable="false"
              @selected="handleSysSelected">
              <div
                v-show="isSystemListLoading"
                style="height: 200px;"
                v-bkloading="{ isLoading: isSystemListLoading, zIndex: 10 }">
              </div>
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
            <bk-input v-else v-model="basicInfo.system_name" disabled style="width: 480px;" />
          </div>
        </div>
      </div>
      <div class="actions-form-item">
        <div class="actions-form-item-label">{{ $t(`m.common['描述']`) }}</div>
        <div class="actions-form-item-content">
          <bk-input
            type="textarea"
            v-model="basicInfo.description"
            :maxlength="255"
            ext-cls="iam-create-template-desc-cls"
            @input="handleDescInput"
          />
        </div>
      </div>
    </render-horizontal-block>
    <render-horizontal-block
      ext-cls="actions-form apply-way-wrapper"
      :label="$t(`m.permApply['选择操作']`)"
    >
      <div class="actions-form-item" v-bkloading="{ isLoading: customLoading, opacity: 1, zIndex: 1000 }">
        <render-action-tag
          ref="commonActionRef"
          style="margin-top: 0;"
          :system-id="basicInfo.system_id"
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
          <div
            v-if="originalCustomTmplList.length < 1 && !customLoading"
            class="empty-wrapper"
          >
            <Icon type="warning" />
            {{ $t(`m.permApply['暂无可申请的操作']`) }}
          </div>
        </div>
        <p v-if="isShowActionError" class="error-tips mt mb10">{{ $t(`m.verify['请选择操作']`) }}</p>
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
  import { cloneDeep } from 'lodash';
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
        isTempName: true,
        isDescription: true,
        isCurSelectActions: true,
        hasGroupPreview: true,
        nameValidateText: '',
        initialTempName: '',
        initialDescription: '',
        systemList: [],
        originalCustomTmplList: [],
        commonActions: [],
        linearAction: [],
        curSelectActions: [],
        nextRequestQueue: [],
        initialValue: [],
        tagActionList: [],
        requestQueue: ['actions', 'commonActions'],
        basicInfo: {
          name: '',
          description: '',
          system_id: '',
          system_name: ''
        }
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
        this.isShowActionError = !(value.length > 0);
        this.isEditTemplate = value.length !== newValue.length;
        this.isCurSelectActions = String(newValue) === String(this.initialValue);
      },
      'basicInfo.name': {
        handler (newValue) {
          this.isTempName = String(newValue) === String(this.initialTempName);
        },
        deep: true
      },
      'basicInfo.description': {
        handler (newValue) {
          this.isDescription = String(newValue) === String(this.initialTempName);
        },
        deep: true
      }
    },
    created () {
      this.initialValue = cloneDeep(this.curSelectActions);
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
          await this.handleActionLinearData();
          await this.fetchCommonActions(system.id || '');
        } catch (e) {
          this.messageAdvancedError(e);
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
          this.messageAdvancedError(e);
        }
      },

      async handleCommonActionAdd ({ actions, name }) {
        window.changeDialog = true;
        const params = {
          system_id: this.basicInfo.system_id,
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
          this.messageAdvancedError(e);
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
          item.actionsAllChecked = item.actions.every(act => act.checked) && (item.sub_groups || []).every(
            v => {
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
          this.basicInfo.system_id = data && data.length ? data[0].id : '';
          if (this.basicInfo.system_id) {
            Promise.all([
              this.fetchActions(this.basicInfo.system_id),
              this.fetchCommonActions(this.basicInfo.system_id)
            ]);
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.isSystemListLoading = false;
        }
      },

      handleActionLinearData () {
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
          this.handleActionLinearData();
        } catch (e) {
          this.messageAdvancedError(e);
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

      async handleSysSelected (value) {
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
        const temps = cloneDeep(payload);
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
          });
          (item.sub_groups || []).forEach(sub => {
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
          window.localStorage.setItem('iam-header-title-cache', name);
          window.localStorage.setItem('iam-header-name-cache', name);
        } catch (e) {
          console.error(e);
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
        if (!this.isShowNameError && this.isShowActionError) {
          this.scrollToLocation(actionRef);
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
            this.$store.commit('permTemplate/updateAction', this.getActionsData(this.originalCustomTmplList));
            window.changeDialog = false;
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
          action_ids: this.curSelectActions
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
.iam-action-temp-content-wrapper {
  position: relative;
  font-size: 14px;
  /deep/ .actions-form {
    position: relative;
    padding: 16px 24px 30px 24px !important;
    .label {
      font-weight: 700;
    }
    &-item {
      margin-bottom: 24px;
      &-label {
        position: relative;
        margin-bottom: 6px;
        font-size: 12px;
        color: #63656E;
        &.is-required {
          &::after {
              content: "*";
              color: #ea3636;
              height: 8px;
              line-height: 1;
              display: inline-block;
              vertical-align: middle;
              position: absolute;
              top: 50%;
              transform: translate(3px,-50%);
          }
        }
      }
    }
    &.basic-info-wrapper {
      .content {
        display: flex;
        align-items: baseline;
        .iam-create-template-desc-cls {
          width: calc(100vh - 480px);
          .actions-form-textarea {
            margin-bottom: 0;
            min-height: 114px;
            height: 100%;
          }
        }
      }
    }
    /* &.apply-way-wrapper {
    } */
  }
  .belong-system {
    .icon-angle-down {
      font-size: 14px;
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
  .error-tips {
    position: relative;
    font-size: 12px;
    color: #ff4d4d;
    top: 0;
    &.mt {
      margin-top: 6px;
    }
  }
  /deep/ .template-name-error {
    .actions-form-input {
      border-color: #ff5656;
    }
  }
}
.bk-select-extension {
  .select-extension-wrapper {
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
}
</style>

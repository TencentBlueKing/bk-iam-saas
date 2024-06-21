<template>
  <div class="resource-perm-manage-instance-table-wrapper">
    <bk-table
      v-if="!isLoading"
      :data="tableList"
      :ext-cls="!isEdit ? 'is-detail-view' : ''"
      :border="false"
      :header-border="false"
      :outer-border="false"
      :cell-class-name="getCellClass"
    >
      <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" :width="350">
        <template slot-scope="{ row }">
          <span class="action-name">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" :min-width="300">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div v-for="_ in row.resource_groups" :key="_.id">
              <!-- <p class="related-resource-item"
                v-for="item in _.related_resource_types"
                :key="item.type">
                <render-resource-popover
                  :key="item.type"
                  :data="item.condition"
                  :value="`${item.name}: ${item.value}`"
                  :max-width="300"
                />
              </p> -->
              <div
                class="flex-between related-resource-item"
                v-for="(related, relatedIndex) in _.related_resource_types"
                :key="related.type"
              >
                <template v-if="relatedIndex < 1">
                  <div class="instance-label">
                    <span>{{ $t(`m.resourcePermiss['配置模板']`) }}{{ $t(`m.common['：']`) }}</span>
                    <span class="instance-count">{{ formatInstanceCount(related, _) || 0 }}</span>
                  </div>
                </template>
              </div>
            </div>
          </template>
          <template v-else>
            {{ $t(`m.common['无需关联实例']`) }}
          </template>
        </template>
      </bk-table-column>
      <template v-if="isCustomActionButton">
        <bk-table-column
          :label="$t(`m.common['操作-table']`)"
          :width="formateOperateWidth"
          fixed="right"
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
                  :ref="`delActionConfirm_${row.id}`"
                  :width="280"
                  @confirm="handleDelete"
                >
                  <div slot="content">
                    <div class="popover-title">
                      <div class="popover-title-text">
                        {{ deleteConfirm.title }}
                      </div>
                    </div>
                    <div class="popover-content">
                      <div class="popover-content-item">
                        <span class="popover-content-item-label">
                          {{ deleteConfirm.label }}{{ $t(`m.common['：']`)}}
                        </span>
                        <span class="popover-content-item-value"> {{ deleteConfirm.value }}</span>
                      </div>
                      <div class="popover-content-tip">
                        {{ deleteConfirm.tip }}
                      </div>
                      <div v-if="delActionList.length" class="popover-content-related">
                        <div class="delete-tips-title">
                          {{ delActionDialogTip }}
                        </div>
                        <div class="delete-tips-content">
                          <div
                            v-for="item in delActionList"
                            :key="item.id"
                            class="related-perm-name">
                            <Icon bk type="info-circle-shape" class="warn" />
                            {{ item.name }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <bk-button
                    type="primary"
                    text
                    :disabled="isDisabledOperate"
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
      <template slot="empty">
        <ExceptionEmpty />
      </template>
    </bk-table>

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
  import { bus } from '@/common/bus';
  import { mapGetters } from 'vuex';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { cloneDeep, uniqWith, isEqual } from 'lodash';
  // import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import RenderDetailEdit from '@/views/perm/components/render-detail-edit';
  import getActionsMixin from '../common/js/getActionsMixin';

  export default {
    components: {
      RenderDetailEdit
      // RenderResourcePopover
    },
    mixins: [getActionsMixin],
    props: {
      list: {
        type: Array,
        default: () => []
      },
      remoteAction: {
        type: Array,
        default: () => []
      },
      templateId: {
        type: [String, Number],
        default: ''
      },
      isLoading: {
        type: Boolean,
        default: true
      },
      isEdit: {
        type: Boolean,
        default: false
      },
      mode: {
        type: String,
        default: 'create'
      },
      isCustom: {
        type: Boolean,
        default: false
      },
      type: {
        type: String,
        default: 'action'
      },
      groupId: {
        type: [String, Number],
        default: ''
      },
      authorization: {
        type: Object,
        default: () => {
          return {};
        }
      },
      isShowErrorTips: {
        type: Boolean,
        default: false
      },
      isAllExpanded: {
        type: Boolean,
        default: false
      },
      externalDelete: {
        type: Boolean,
        default: false
      },
      // 单独处理需要自定义操作按钮的页面
      isCustomActionButton: {
        type: Boolean,
        default: false
      },
      isShowDeleteAction: {
        type: Boolean,
        default: true
      },
      isShowDeleteInstance: {
        type: Boolean,
        default: true
      },
      isDisabledOperate: {
        type: Boolean,
        default: true
      },
      deleteConfirm: {
        type: Object,
        default: () => {
          return {};
        }
      },
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        disabled: true,
        canOperate: true,
        batchDisabled: false,
        isSamePolicy: false,
        isBatchDelete: true,
        isShowSideSlider: false,
        isShowPreviewDialog: false,
        isShowDeleteDialog: false,
        isShowResourceInstanceSideSlider: false,
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
        params: {},
        previewResourceParams: {},
        curScopeAction: {},
        curCopyParams: {},
        newRow: {},
        tableList: [],
        previewData: [],
        delActionList: [],
        delPathList: [],
        policyIdList: [],
        customData: [],
        curInstancePaths: [],
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters(['user']),
      sliderWidth () {
        return this.mode === 'detail' ? 960 : 640;
      },
      isSuperManager () {
        return this.user.role.type === 'super_manager';
      },
      isCreateMode () {
        return this.mode === 'create';
      },
      isCanOperate () {
        // 如果是资源权限管理操作查询不是同一个操作，则不能删除实例
        if (['resourcePermiss'].includes(this.$route.name)) {
          return false;
        }
        return this.canOperate;
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
              return 360;
            }
            return 192;
          }
        };
        return langMap[this.curLanguageIsCn]();
      },
      formatInstanceCount () {
        return (payload, related) => {
          let curPaths = [];
          if (related.related_resource_types && related.related_resource_types.length > 1) {
            const list = related.related_resource_types.map((v) => {
              if (v.condition.length) {
                const { instance, instances } = v.condition[0];
                const list = instance || instances;
                curPaths = list.reduce((prev, next) => {
                  prev.push(
                    ...next.path.map(v => {
                      const paths = { ...v, ...next };
                      delete paths.instance;
                      delete paths.path;
                      return paths[0];
                    })
                  );
                  return prev;
                }, []);
                return curPaths.length;
              }
            });
            const count = list.reduce((prev, next) => prev + next, 0);
            return count;
          } else {
            if (payload.condition.length) {
              const { instance, instances } = payload.condition[0];
              const list = instance || instances;
              curPaths = list.reduce((prev, next) => {
                prev.push(
                  ...next.path.map(v => {
                    const paths = { ...v, ...next };
                    delete paths.instance;
                    delete paths.path;
                    return paths[0];
                  })
                );
                return prev;
              }, []);
              return curPaths.length;
            }
          }
        };
      }
    },
    watch: {
      list: {
        handler (value) {
          value = uniqWith(value, isEqual);
          const customData = value.filter((item) => item.mode === 'custom');
          const templateData = value.filter((item) => item.mode === 'template');
          this.tableList.splice(0, this.tableList.length, ...customData, ...templateData);
        },
        immediate: true
      }
    },
    mounted () {
      window.addEventListener('resize', (this.formatFormItemWidth));
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
    },
    methods: {
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      formatFormItemWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
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
        const { id, mode, name, condition } = payload;
        let delRelatedActions = [];
        this.delActionList = [];
        const isCustom = ['custom'].includes(mode);
        const policyIdList = this.tableList.map(v => v.id);
        // 处理多系统展开时，只获取当前系统下的所有操作
        if (this.tableList.length > 0 && ['action'].includes(type)) {
          await this.fetchActions(this.tableList[0].detail);
        }
        const linearActionList = this.linearActionList.filter(item => policyIdList.includes(item.id));
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
              this.$refs[`delActionConfirm_${payload.id}`] && this.$refs[`delActionConfirm_${payload.id}`].$refs.popover
                && this.$refs[`delActionConfirm_${payload.id}`].$refs.popover.showHandler();
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

      handleBatchDelete () {
        window.changeAlert = true;
        this.isBatchDelete = false;
      },

      handleDelete () {
        this.$emit('on-delete', this.newRow);
      },

      handleViewResource (payload) {
        const params = [];
        this.curId = payload.id;
        this.curPolicyId = payload.policy_id;
        // 如果不是同一个操作，则只有查看实例权限
        this.isSamePolicy = this.curId === this.curDetailData.action_id;
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

      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowSideSlider = false;
          this.resetDataAfterClose();
        }, _ => _);
      },

      handleBeforeClose () {
        bus.$emit('on-drawer-side', { width: 960 });
        return true;
      },

      handleAfterDeleteLeave () {
        this.currentActionName = '';
        this.delActionList = [];
        this.policyIdList = [];
      },

      handleCancelDelete () {
        window.changeAlert = false;
        this.isBatchDelete = true;
      },

      resetDataAfterClose () {
        this.curId = '';
        this.curPolicyId = '';
        this.sideSliderTitle = '';
        this.previewData = [];
        this.canOperate = true;
        this.disabled = true;
        this.isBatchDelete = true;
        this.batchDisabled = false;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.resource-perm-manage-instance-table-wrapper {
  /deep/ .bk-table {
    width: 100%;
    border: none;
    font-size: 12px;
    .relation-content-wrapper,
    .conditions-wrapper {
      height: 100%;
      padding: 17px 0;
      color: #63656e;
      .resource-type-name {
        display: block;
        margin-bottom: 9px;
      }
    }
    .related-resource-item {
      .instance-count {
        color: #3a84ff;
        font-weight: 700;
      }
    }
    .remove-icon {
      position: absolute;
      right: 2px;
      top: 2px;
      font-size: 20px;
      cursor: pointer;
      &:hover {
        color: #3a84ff;
      }
    }
    .action-name {
      display: inline-block;
      vertical-align: bottom;
      word-wrap: break-word;
      word-break: break-all;
    }
    .operate-column {
      display: flex;
      align-items: center;
      .operate-column-btn  {
        margin-right: 12px;
      }
    }
    &.is-detail-view {
      .bk-table-header-wrapper {
        th {
          &:first-child {
            .cell {
              padding-left: 48px;
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
          padding-left: 48px;
        }
      }
    }
  }
  /deep/ .instance-detail-slider {
    &-title {
      max-width: 750px;
    }
  }
}
.instance-detail-operate-confirm {
  font-size: 0;
  .popover-custom-content {
    font-size: 14px;
    margin-bottom: 16px;
  }
  .cancel-delete-btn {
    margin-left: 8px;
  }
}
</style>

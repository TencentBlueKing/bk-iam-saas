<template>
  <!-- eslint-disable max-len -->
  <div class="iam-grade-update-template-instance-wrapper">
    <table class="bk-table iam-grade-instance-table">
      <thead>
        <tr>
          <th style="padding-left: 28px;">{{ $t(`m.common['操作']`) }}</th>
          <th>{{ $t(`m.grading['资源实例范围']`) }}</th>
        </tr>
      </thead>
      <tbody>
        <template v-if="policyList.length > 0">
          <tr
            v-for="(item, index) in policyList"
            :key="index">
            <template v-if="item.isPolymerize">
              <td class="action-content">
                <div
                  :class="['action-content-wrapper', { 'reset-left': item.canPolymerize }]">
                  <Icon
                    v-if="item.canPolymerize"
                    bk
                    :type="item.isPolymerize ? 'angle-right' : 'angle-down'"
                    @click.stop="handleExpanded(item)" />
                  <span :title="item.actionNameDisplay">{{ item.actionNameDisplay }}</span>
                </div>
              </td>
              <td class="instance-content has-padding">
                <template v-if="item.canPolymerize">
                  <div class="relation-content-item"
                    v-for="(content, contentIndex) in item.instanceSelections"
                    :key="contentIndex">
                    <div class="content-name">{{ content.name }}</div>
                    <div class="content has-cursor" @click.stop="handleLoadInstances(content, index, contentIndex)">
                      <bk-select
                        v-model="content.selectValue"
                        searchable
                        :disabled="content.disabled"
                        :ref="`${index}&${contentIndex}Ref`"
                        :ext-cls="content.disabled ? 'grade-select-instance-cls' : ''"
                        :loading="content.loading">
                        <bk-option v-for="option in content.list"
                          :key="option.id"
                          :id="option.id"
                          :name="option.name">
                        </bk-option>
                      </bk-select>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <template v-if="!item.actions[0].isEmpty">
                    <div class="relation-content-item"
                      v-for="(content, contentIndex) in item.actions[0].related_resource_types"
                      :key="contentIndex">
                      <div class="content-name">{{ content.name }}</div>
                      <div class="content">
                        <render-condition
                          :value="content.value"
                          :is-empty="content.empty"
                          :can-view="item.actions[0].canView"
                          :can-paste="canPaste"
                          :is-error="content.isError"
                          @on-mouseover="handleConditionMouseover(content)"
                          @on-mouseleave="handleConditionMouseleave(content)"
                          @on-view="handleOnView(item.actions[0], content, contentIndex)"
                          @on-copy="handleOnCopy(content)"
                          @on-paste="handleOnPaste(content)"
                          @on-click="showResourceInstance(item.actions[0], content, index, 0, contentIndex)" />
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    {{ $t(`m.common['无需关联实例']`) }}
                  </template>
                </template>

                <div class="remove-action-ext" @click.stop="handleRemove(item, index)">
                  <Icon type="close-small" />
                </div>
              </td>
            </template>
            <template v-else>
              <td colspan="2" class="sub-action-td">
                <table class="bk-table iam-grade-instance-sub-table has-no-border">
                  <tr
                    v-for="(actionItem, actionIndex) in item.actions"
                    :key="actionIndex"
                    style="background: #f6f9ff;"
                    :class="actionIndex !== item.actions.length - 1 ? 'has-border-tr' : 'no-border-tr'">
                    <td class="action-content">
                      <div
                        :class="['action-content-wrapper', { 'reset-left': item.canPolymerize }]">
                        <Icon
                          v-if="item.canPolymerize && actionIndex === 0"
                          bk
                          :type="item.isPolymerize ? 'angle-right' : 'angle-down'"
                          @click.stop="handleExpanded(item)" />
                        <span>{{ actionItem.name }}</span>
                      </div>
                    </td>
                    <td class="instance-content has-padding">
                      <template v-if="!actionItem.isEmpty">
                        <div class="relation-content-item"
                          v-for="(content, contentIndex) in actionItem.related_resource_types"
                          :key="contentIndex">
                          <div class="content-name">{{ content.name }}</div>
                          <div class="content">
                            <render-condition
                              :value="content.value"
                              :is-empty="content.empty"
                              :can-view="actionItem.canView"
                              :can-paste="canPaste"
                              :is-error="content.isError"
                              @on-mouseover="handleConditionMouseover(content)"
                              @on-mouseleave="handleConditionMouseleave(content)"
                              @on-view="handleOnView(actionItem, content, contentIndex)"
                              @on-copy="handleOnCopy(content)"
                              @on-paste="handleOnPaste(content)"
                              @on-click="showResourceInstance(actionItem, content, index, actionIndex, contentIndex)" />
                          </div>
                        </div>
                      </template>
                      <template v-else>
                        {{ $t(`m.common['无需关联实例']`) }}
                      </template>
                      <div class="remove-action" @click.stop="handleRemoveActions(item, actionItem, actionIndex)">
                        <Icon type="close-small" />
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </template>
          </tr>
        </template>
        <template v-else>
          <tr class="empty-tr-wrapper">
            <td colspan="3">
              <!-- <p><Icon bk type="empty" /></p>
                            <span class="text">{{ $t(`m.common['暂无数据']`) }}</span> -->
              <ExceptionEmpty
                :type="emptyData.type"
                :empty-text="emptyData.text"
                :tip-text="emptyData.tip"
                :tip-type="emptyData.tipType"
                @on-refresh="handleEmptyRefresh"
              />
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <bk-sideslider
      :is-show.sync="isShowResourceInstanceSideslider"
      :title="resourceInstanceSidesliderTitle"
      width="640"
      :ext-cls="'relate-instance-sideslider'"
      @animation-end="handleResourceSliderClose">
      <div slot="content" class="sideslider-content">
        <render-resource
          ref="renderResourceRef"
          :data="condition"
          :selection-mode="curSelectionMode"
          :disabled="curDisabled"
          :params="params"
          @on-limit-change="handleLimitChange"
          @on-init="handleOnInit" />
      </div>
      <div slot="footer" style="margin-left: 25px;">
        <bk-button theme="primary" :disabled="disabled" @click="handleResourceSumit">{{ $t(`m.common['保存']`) }}</bk-button>
        <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel">{{ $t(`m.common['取消']`) }}</bk-button>
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import RenderCondition from '../../perm-apply/components/render-condition';
  import RenderResource from '../../perm-apply/components/render-resource';
  export default {
    name: '',
    components: {
      RenderCondition,
      RenderResource
    },
    props: {
      data: {
        type: Array,
        default: () => []
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
      },
      onRefresh: {
        type: Function
      }
    },
    data () {
      return {
        canPaste: false,
        curCopyData: ['none'],
        curCopyType: '',
        curCopyKey: '',

        isShowResourceInstanceSideslider: false,
        resourceInstanceSidesliderTitle: '',
        // 查询参数
        params: {},
        disabled: false,
        curIndex: -1,
        curActionIndex: -1,
        curResIndex: -1,
        condition: [],
        curSelectionMode: 'all',
        curDisabled: false,
        policyList: []
      };
    },
    computed: {
      // condition () {
      //     if (this.curIndex === -1 || this.curResIndex === -1) {
      //         return []
      //     }
      //     const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
      //     return _.cloneDeep(curData.condition)
      // },
      // curDisabled () {
      //     if (this.curIndex === -1 || this.curResIndex === -1) {
      //         return false
      //     }
      //     const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
      //     return curData.isDefaultLimit
      // },
      // curSelectionMode () {
      //     if (this.curIndex === -1 || this.curResIndex === -1) {
      //         return 'all'
      //     }
      //     const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
      //     return curData.selectionMode
      // }
    },
    watch: {
      data: {
        handler (value) {
          // console.warn(value)
          this.policyList = value;
        },
        immediate: true
      }
    },
    methods: {
      handleConditionActionMessage (payload) {
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: payload
        });
      },

      handleExpanded (payload) {
        payload.isPolymerize = !payload.isPolymerize;
      },

      handleConditionMouseover (payload) {
        if (this.curCopyData[0] === 'none') {
          return;
        }
        // type相同且不是自身的才可以粘贴
        if (this.curCopyType === payload.type && this.curCopyKey !== `${payload.action.type}${payload.type}`) {
          this.canPaste = true;
        }
      },

      handleLimitChange () {
        // const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
        // curData.isChange = true
      },

      handleOnInit (payload) {
        this.disabled = !payload;
      },

      handleRemove (payload, index) {
        this.policyList.splice(index, 1);
        const actionIds = payload.actions.map(item => item.id);
        this.$emit('on-delete', actionIds);
      },

      handleRemoveActions (payload, item, index) {
        payload.actions.splice(index, 1);
        if (payload.actions.length === 1) {
          payload.canPolymerize = false;
          payload.isPolymerize = true;
        }
        this.$emit('on-delete', [item.id]);
      },

      handleConditionMouseleave (payload) {
        this.canPaste = false;
      },

      handleLoadInstances (payload, index, contentIndex) {
        if (!payload.disabled) {
          return;
        }
        payload.loading = true;
        setTimeout(() => {
          payload.loading = false;
          payload.disabled = false;
          this.$nextTick(() => {
            const curRefs = this.$refs[`${index}&${contentIndex}Ref`];
            curRefs && curRefs[0].show();
          });
        }, 500);
      },

      handleResourceSliderClose () {
        this.curIndex = -1;
        this.curResIndex = -1;
        this.curActionIndex = -1;
        // this.previewResourceParams = {}
        this.condition = [];
        this.params = {};
        this.curSelectionMode = 'all';
        this.curDisabled = false;
        this.resourceInstanceSidesliderTitle = '';
      },

      handleResourceCancel () {
        this.isShowResourceInstanceSideslider = false;
      },

      handleOnView (payload, item, itemIndex) {
        // const { system_id, type, name } = item
        // const condition = []
        // item.condition.forEach(item => {
        //     const { id, attribute, instance } = item
        //     condition.push({
        //         id,
        //         attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
        //         instances: instance ? instance.filter(item => item.path.length > 0) : []
        //     })
        // })
        // this.previewResourceParams = {
        //     policy_id: payload.policy_id,
        //     related_resource_type: {
        //         system_id,
        //         type,
        //         name,
        //         condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
        //     }
        // }
        // this.previewDialogTitle = `${this.$t(`m.common['操作']`)}【${payload.name}】${this.$t(`m.common['的资源实例']`)} ${this.$t(`m.common['差异对比']`)}`
        // this.isShowPreviewDialog = true
      },

      handleOnCopy (payload) {
        this.curCopyType = payload.type;
        this.curCopyKey = `${payload.action.type}${payload.type}`;
        this.curCopyData = _.cloneDeep(payload.condition);
        this.handleConditionActionMessage(this.$t(`m.info['复制成功']`));
      },

      handleOnPaste (payload) {
        if (this.curCopyData[0] === 'none') {
          return;
        }
        const tempCurData = this.curCopyData.map(item => {
          delete item.id;
          return item;
        });
        tempCurData.forEach((item, index) => {
          if (payload.condition[index]) {
            if (payload.condition[index].id) {
              item.id = payload.condition[index].id;
            } else {
              item.id = '';
            }
          } else {
            item.id = '';
          }
        });
        payload.condition = _.cloneDeep(tempCurData);
        this.handleConditionActionMessage(this.$t(`m.info['粘贴成功']`));
      },

      handleResourceSumit () {
        const conditionData = this.$refs.renderResourceRef.handleGetValue();
        const { isEmpty, data } = conditionData;
        if (isEmpty) {
          return;
        }

        this.policyList[this.curIndex]
          .actions[this.curActionIndex]
          .related_resource_types[this.curResIndex]
          .condition = data;

        this.policyList[this.curIndex]
          .actions[this.curActionIndex]
          .related_resource_types[this.curResIndex]
          .isError = false;

        this.curIndex = -1;
        this.curActionIndex = -1;
        this.curResIndex = -1;
        this.isShowResourceInstanceSideslider = false;
      },

      showResourceInstance (data, resItem, index, actionIndex, resIndex) {
        this.params = {
          system_id: data.system_id,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };

        this.curIndex = index;
        this.curActionIndex = actionIndex;
        this.curResIndex = resIndex;

        this.condition = _.cloneDeep(resItem.condition);
        this.curSelectionMode = resItem.selectionMode;
        this.curDisabled = resItem.isDefaultLimit;
        this.resourceInstanceSidesliderTitle = `${this.$t(`m.common['关联操作']`)}${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
        this.isShowResourceInstanceSideslider = true;
      },

      handleGetValue () {
        const data = [];
        let flag = false;
        this.policyList.forEach(policy => {
          policy.actions.forEach(item => {
            const relatedResourceTypes = [];
            if (item.related_resource_types.length > 0) {
              item.related_resource_types.forEach(resItem => {
                if (resItem.empty) {
                  resItem.isError = true;
                  flag = true;
                }
                const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                  ? resItem.condition.map(conItem => {
                    const { id, instance, attribute } = conItem;
                    const attributeList = (attribute && attribute.length > 0)
                      ? attribute.map(({ id, name, values }) => ({ id, name, values }))
                      : [];

                    const instanceList = (instance && instance.length > 0)
                      ? instance.map(({ name, type, path }) => {
                        const tempPath = _.cloneDeep(path);
                        tempPath.forEach(pathItem => {
                          pathItem.forEach(pathSubItem => {
                            delete pathSubItem.disabled;
                          });
                        });
                        return {
                          name,
                          type,
                          path: tempPath
                        };
                      })
                      : [];
                    return {
                      id,
                      instances: instanceList,
                      attributes: attributeList
                    };
                  })
                  : [];

                relatedResourceTypes.push({
                  type: resItem.type,
                  system_id: resItem.system_id,
                  condition: conditionList
                });
              });
            }
            const params = {
              system_id: item.system_id,
              actions: [
                {
                  id: item.id,
                  related_resource_types: relatedResourceTypes
                }
              ]
            };
            const isExistData = data.find(subItem => subItem.system_id === item.system_id);
            if (isExistData) {
              isExistData.actions.push({
                id: item.id,
                related_resource_types: relatedResourceTypes
              });
            } else {
              data.push(params);
            }
          });
        });

        return {
          flag,
          data
        };
      },

      handleEmptyRefresh () {
        this.onRefresh();
      }
    }
  };
</script>
<style lang="postcss">
    .iam-grade-update-template-instance-wrapper {
        /* margin-top: 8px; */
        .iam-grade-instance-table {
            /* border-bottom: none; */
            border: none;
            /* &.has-no-border {
                border: none;
            } */
            thead {
                tr {
                    background: #fafbfd;
                    th {
                        border-top: none;
                        font-size: 12px;
                        color: #313238;
                    }
                }
            }
            tbody {
                tr {
                    position: relative;
                    &:hover {
                        background: #fff;
                        .remove-action-ext {
                            display: block;
                        }
                    }
                    &.empty-tr-wrapper {
                        td {
                            height: 201px;
                            text-align: center;
                            p {
                                i {
                                    font-size: 65px;
                                    color: #c3cdd7;
                                }
                            }
                            .text {
                                color: #63656e;
                            }
                        }
                    }
                    td {
                        height: 42px;
                        font-size: 12px;
                        color: #63656e;
                    }
                    .action-content-wrapper {
                        position: relative;
                        &.reset-left {
                            left: -16px;;
                        }
                    }
                    .action-content {
                        position: relative;
                        padding-left: 28px;
                        width: 200px;
                        i {
                            position: relative;
                            left: -3px;
                            cursor: pointer;
                        }
                    }
                    /* .system-content {
                        width: 200px;
                    } */
                    .instance-content {
                        position: relative;
                        .relation-content-item {
                            margin-top: 17px;
                            &.has-cursor {
                                cursor: pointer;
                            }
                            &:first-child {
                                margin-top: 0;
                            }
                            .content-name {
                                margin-bottom: 9px;
                            }
                            .grade-select-instance-cls {
                                background-color: #fff !important;
                                cursor: pointer !important;
                                border-color: #c4c6cc !important;
                            }
                        }
                    }

                    .remove-action-ext {
                        display: none;
                        position: absolute;
                        top: 0;
                        right: 10px;
                        width: 24px;
                        height: 24px;
                        cursor: pointer;
                        &:hover {
                            color: #3a84ff;
                        }
                        i {
                            font-size: 24px;
                        }
                    }
                }

                .sub-action-td {
                    padding: 0 10px;
                    background: #f6f9ff;
                    border-bottom: none !important;
                }
            }
        }

        .iam-grade-instance-sub-table {
            &.has-no-border {
                border: none;
            }
            &::before {
                display: none;
            }
            tr {
                position: relative;
                &:hover {
                    background: #fff;
                    .remove-action {
                        display: block;
                    }
                }
                &.has-border-tr {
                    td {
                        border-bottom: 1px dashed #dfe0e5;
                    }
                }
                &.no-border-tr {
                    td {
                        border-bottom: none !important;
                    }
                }
                td {
                    height: 42px;
                    font-size: 12px;
                    color: #63656e;
                }
                .action-content-wrapper {
                    position: relative;
                    &.reset-left {
                        left: -16px;;
                    }
                }
                .action-content {
                    position: relative;
                    padding-left: 28px;
                    width: 200px;
                    i {
                        position: relative;
                        left: -3px;
                        cursor: pointer;
                    }
                }
                /* .system-content {
                    width: 200px;
                } */
                .instance-content {
                    position: relative;
                    &.has-padding {
                        padding: 10px 0;
                    }
                    .relation-content-item {
                        margin-top: 17px;
                        &.has-cursor {
                            cursor: pointer;
                        }
                        &:first-child {
                            margin-top: 0;
                        }
                        .content-name {
                            margin-bottom: 9px;
                        }
                        .grade-select-instance-cls {
                            background-color: #fff !important;
                            cursor: pointer !important;
                            border-color: #c4c6cc !important;
                        }
                    }
                }

                .remove-action {
                    display: none;
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 24px;
                    height: 24px;
                    cursor: pointer;
                    &:hover {
                        color: #3a84ff;
                    }
                    i {
                        font-size: 24px;
                    }
                }
            }
        }
    }
</style>

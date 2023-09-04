<template>
  <!-- eslint-disable max-len -->
  <div class="iam-perm-template-action-wrapper">
    <div
      v-for="(item, index) in originalCustomTmplList"
      :key="index"
      :class="['action-item', { 'set-border': originalCustomTmplList.length > 1 }, { 'reset-padding-top': index === 0 }]">
      <p style="cursor: pointer;"
        v-if="!(originalCustomTmplList.length === 1 && !isShowGroupAction(item))"
        @click.stop="handleExpanded(item)">
        <section :class="['action-group-name', { 'set-cursor': originalCustomTmplList.length > 1 }]">
          <Icon :type="item.expanded ? 'down-angle' : 'right-angle'" v-if="originalCustomTmplList.length > 1" />
          <span>{{ item.name }}</span>
          <span v-if="isShowCount" class="count">{{$t(`m.common['已选']`)}} {{ item.count }} / {{ item.allCount }} {{ $t(`m.common['个']`) }} <span v-if="item.deleteCount" class="delete-count"> 包含{{item.deleteCount}}个需要被删除的操作</span></span>
        </section>
        <span
          v-if="!isDisabled"
          :class="['check-all', { 'is-disabled': item.actionsAllDisabled }]"
          @click.stop="handleCheckAll(item)">
          {{ item.actionsAllChecked ? $t(`m.common['取消全选']`) : $t(`m.common['选择全部']`) }}
        </span>
      </p>
      <div class="action-content" v-if="item.expanded">
        <div
          :class="['self-action-content', { 'set-border-bottom': isShowGroupAction(item) }]"
          v-if="item.actions && item.actions.length > 0">
          <bk-checkbox
            v-for="(act, actIndex) in item.actions"
            :key="actIndex"
            :true-value="true"
            :false-value="false"
            v-model="act.checked"
            :disabled="act.disabled || isDisabled"
            ext-cls="iam-action-cls"
            data-test-id="permTemplate_checkbox_action"
            @change="handleActionChecked(...arguments, act, item)">
            <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
              <template v-if="act.disabled">
                <span class="text" :class="{ 'text-through': act.tag === 'delete' && mode === 'detail' }">{{ act.name }}</span>
              </template>
              <template v-else>
                <span class="text" :class="{ 'text-through': act.tag === 'delete' && mode === 'detail' }">{{ act.name }}</span>
              </template>
              <div slot="content" class="iam-perm-apply-action-popover-content">
                <div>
                  <span class="name">{{ act.name }}</span>
                  <span :class="getComputedClass(act)">
                    ({{ act.checked ? act.disabled ? $t(`m.common['已获得']`) : $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})
                  </span>
                </div>
                <div class="description">{{ $t(`m.common['描述']`) + '：' + (act.description || '--') }}</div>
                <div class="relate-action" v-if="act.related_actions.length > 0">
                  {{ getRelatedActionTips(act.related_actions) }}
                </div>
              </div>
            </bk-popover>

            <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
              <template v-if="act.tag === 'delete'">
                <Icon type="error-fill" class="error-icon" />
              </template>
              <div slot="content" class="iam-perm-apply-action-popover-content">
                <div>
                  {{$t(`m.common['由于管理空间的授权范围没有包含此操作，']`)}}<br>
                  {{$t(`m.common[' 如需使用该模板进行新的授权必须先删除该操作。']`)}}
                </div>
              </div>
            </bk-popover>
            <template v-if="isCompare && act.hasOwnProperty('flag') && ['added', 'cancel'].includes(act.flag)">
              <bk-tag :theme="act.flag === 'added' ? 'success' : 'danger'">
                {{ act.flag === 'added' ? $t(`m.common['新增']`) : $t(`m.common['移除']`) }}
              </bk-tag>
            </template>
          </bk-checkbox>
          <bk-checkbox
            v-if="!isDisabled"
            :true-value="true"
            :false-value="false"
            v-model="item.allChecked"
            :disabled="item.actions.every(v => v.disabled) || isDisabled"
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
                  :disabled="act.disabled || isDisabled"
                  ext-cls="iam-action-cls"
                  data-test-id="permTemplate_checkbox_action"
                  @change="handleSubActionChecked(...arguments, act, subAct, item)">
                  <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                    <template v-if="act.disabled">
                      <span class="text" :class="{ 'text-through': act.tag === 'delete' && mode === 'detail' }">{{ act.name }}</span>
                    </template>
                    <template v-else>
                      <span class="text" :class="{ 'text-through': act.tag === 'delete' && mode === 'detail' }">{{ act.name }}</span>
                    </template>
                    <div slot="content" class="iam-perm-apply-action-popover-content">
                      <div>
                        <span class="name">{{ act.name }}</span>
                        <span :class="getComputedClass(act)">
                          ({{ act.checked ? act.disabled ? $t(`m.common['已获得']`) : $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})
                        </span>
                      </div>
                      <div class="description">{{ $t(`m.common['描述']`) + '：' + (act.description || '--') }}</div>
                      <div class="relate-action" v-if="act.related_actions.length > 0">
                        {{ getRelatedActionTips(act.related_actions) }}
                      </div>
                    </div>
                  </bk-popover>
                  <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                    <template v-if="act.tag === 'delete'">
                      <Icon type="error-fill" class="error-icon" />
                    </template>
                    <div slot="content" class="iam-perm-apply-action-popover-content">
                      <div>
                        {{$t(`m.common['由于管理空间的授权范围没有包含此操作，']`)}}<br>
                        {{$t(`m.common[' 如需使用该模板进行新的授权必须先删除该操作。']`)}}
                      </div>
                    </div>
                  </bk-popover>
                  <template v-if="isCompare && act.hasOwnProperty('flag') && ['added', 'cancel'].includes(act.flag)">
                    <bk-tag :theme="act.flag === 'added' ? 'success' : 'danger'">
                      {{ act.flag === 'added' ? $t(`m.common['新增']`) : $t(`m.common['移除']`) }}
                    </bk-tag>
                  </template>
                  <!-- <template v-if="act.related_actions.length > 0">
                                        <Icon v-bk-tooltips="getRelatedActionTips(act.related_actions)" type="info-new" />
                                    </template> -->
                </bk-checkbox>
              </section>
            </div>
            <bk-checkbox
              v-if="!isDisabled"
              :true-value="true"
              :false-value="false"
              v-model="subAct.allChecked"
              :disabled="subAct.actions.every(v => v.disabled) || isDisabled"
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
<script>
  export default {
    name: '',
    props: {
      actions: {
        type: Array,
        default: () => []
      },
      // mode取值: create detail edit
      mode: {
        type: String,
        default: 'create'
      },
      linearAction: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        isCompare: false,
        originalCustomTmplList: []
      };
    },
    computed: {
      isShowCount () {
        return ['detail', 'create', 'edit'].includes(this.mode);
      },
      isDisabled () {
        return ['detail'].includes(this.mode);
      },
      isShowGroupAction () {
        return (item) => {
          const isExistSubGroup = (item.sub_groups || []).some(v => v.sub_groups && v.sub_groups.length > 0);
          return item.sub_groups && item.sub_groups.length > 0 && !isExistSubGroup;
        };
      },
      curSelectActions () {
        const allActionIds = [];
        this.originalCustomTmplList.forEach(payload => {
          payload.deleteCount = 0;
          if (!payload.actionsAllDisabled) {
            payload.actions.forEach(item => {
              if (!item.disabled && item.checked) {
                allActionIds.push(item.id);
              }
              if (!item.disabled && item.checked && item.tag === 'delete') {
                payload.deleteCount++;
              }
            })
            ;(payload.sub_groups || []).forEach(subItem => {
              (subItem.actions || []).forEach(act => {
                if (!act.disabled && act.checked) {
                  allActionIds.push(act.id);
                }
                if (!act.disabled && act.checked && act.tag === 'delete') {
                  payload.deleteCount++;
                }
              });
            });
          }
        });
        return allActionIds;
      }
    },
    watch: {
      actions: {
        handler (value) {
          this.originalCustomTmplList = value;
        },
        deep: true,
        immediate: true
      },
      curSelectActions (value) {
        this.$emit('on-select', value);
      }
    },
    methods: {
      setWindowChangeDialog () {
        if (!this.isDisabled) {
          window.changeDialog = true;
        }
      },
      handleRelatedActions (payload, flag) {
        this.originalCustomTmplList.forEach((item, index) => {
          item.actions.forEach(act => {
            if (payload.related_actions.includes(act.id) && flag && !act.checked) {
              act.checked = true;
              act.flag = payload.flag;
              ++item.count;
            }
            if (act.related_actions.includes(payload.id) && !flag && act.checked) {
              act.checked = false;
              act.flag = payload.flag;
              --item.count;
            }
          })
          ;(item.sub_groups || []).forEach(sub => {
            sub.actions.forEach(act => {
              if (payload.related_actions.includes(act.id) && flag && !act.checked) {
                act.checked = true;
                act.flag = payload.flag;
                ++item.count;
              }
              if (act.related_actions.includes(payload.id) && !flag && act.checked) {
                act.checked = false;
                act.flag = payload.flag;
                --item.count;
              }
            });
            const isSubAllChecked = sub.actions.every(v => v.checked);
            const subActions = sub.actions.filter(e => !e.disabled);
            let isSubAllCheckedData = true;
            if (subActions.length) {
              isSubAllCheckedData = subActions.every(v => v.checked);
            }
            sub.allChecked = isSubAllChecked;
            sub.allCheckedData = isSubAllCheckedData;
          });
          const isAllChecked = item.actions.every(v => v.checked);
          const actions = item.actions.filter(e => !e.disabled);
          let isAllCheckedData = true;
          if (actions.length) {
            isAllCheckedData = actions.every(v => v.checked);
          }
          item.allChecked = isAllChecked;
          item.allCheckedData = isAllCheckedData;
          if (item.sub_groups && item.sub_groups.length > 0) {
            this.$nextTick(() => {
              item.actionsAllChecked = isAllCheckedData && item.sub_groups.every(v => v.allCheckedData);
            });
          } else {
            this.$nextTick(() => {
              item.actionsAllChecked = isAllCheckedData;
            });
          }
        });
      },
      handleExpanded (payload) {
        if (this.originalCustomTmplList.length < 2) {
          return;
        }
        this.setWindowChangeDialog();
        payload.expanded = !payload.expanded;
      },
      getRelatedActionTips (payload) {
        const relatedActions = this.linearAction.filter(item => payload.includes(item.id));
        return `${this.$t(`m.common['依赖操作']`)}: ${relatedActions.map(item => item.name).join('，')}`;
      },
      handleSubActionChecked (newVal, oldVal, val, actData, payload, item) {
        this.setWindowChangeDialog();
        const hasFlag = actData.hasOwnProperty('flag');
        if (!newVal) {
          payload.allChecked = false;
          item.actionsAllChecked = false;
          if (hasFlag) {
            if (actData.flag === 'selected') {
              actData.flag = 'cancel';
            }
            if (actData.flag === 'added') {
              this.$delete(actData, 'flag');
            }
          }
          this.handleRelatedActions(actData, false);
          item.count--;
          return;
        }
        if (hasFlag && actData.flag === 'cancel') {
          actData.flag = 'selected';
        }
        if (!hasFlag) {
          this.$set(actData, 'flag', 'added');
        }
        payload.allChecked = payload.actions.every(item => item.checked);
        item.actionsAllChecked = item.actions.every(act => act.checked) && item.sub_groups.every(v => {
          return v.actions.every(act => act.checked);
        });
        item.count++;
        this.handleRelatedActions(actData, true);
      },
      handleCheckAll (payload) {
        if (payload.actionsAllDisabled) {
          return;
        }
        this.setWindowChangeDialog();
        const tempActionIds = [];
        const allActionIds = [];
        const tempActions = [];
        payload.actionsAllChecked = !payload.actionsAllChecked;
        if (!payload.actions.every(v => v.disabled)) {
          payload.allChecked = payload.actionsAllChecked;
        }
        payload.actions.forEach(item => {
          if (!item.disabled) {
            item.checked = payload.actionsAllChecked;
            tempActionIds.push(item.id);
            tempActions.push(item);
            const hasFlag = item.hasOwnProperty('flag');
            if (!item.checked) {
              if (hasFlag) {
                if (item.flag === 'selected') {
                  item.flag = 'cancel';
                }
                if (item.flag === 'added') {
                  this.$delete(item, 'flag');
                }
              }
            } else {
              if (hasFlag && item.flag === 'cancel') {
                item.flag = 'selected';
              }
              if (!hasFlag) {
                this.$set(item, 'flag', 'added');
              }
            }
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
              const hasFlag = act.hasOwnProperty('flag');
              if (!act.checked) {
                if (hasFlag) {
                  if (act.flag === 'selected') {
                    act.flag = 'cancel';
                  }
                  if (act.flag === 'added') {
                    this.$delete(act, 'flag');
                  }
                }
              } else {
                if (hasFlag && act.flag === 'cancel') {
                  act.flag = 'selected';
                }
                if (!hasFlag) {
                  this.$set(act, 'flag', 'added');
                }
              }
            }
            allActionIds.push(act.id);
          });
        });
        tempActions.forEach(item => {
          this.handleRelatedActions(item, payload.actionsAllChecked);
        });
        payload.count = payload.actionsAllChecked ? payload.allCount : 0;
      },
      handleActionChecked (newVal, oldVal, val, actData, payload) {
        this.setWindowChangeDialog();
        const hasFlag = actData.hasOwnProperty('flag');
        if (!newVal) {
          payload.allChecked = false;
          payload.actionsAllChecked = false;
          if (hasFlag) {
            if (actData.flag === 'selected') {
              actData.flag = 'cancel';
            }
            if (actData.flag === 'added') {
              this.$delete(actData, 'flag');
            }
          }
          this.handleRelatedActions(actData, false);
          payload.count--;
          return;
        }
        if (hasFlag && actData.flag === 'cancel') {
          actData.flag = 'selected';
        }
        if (!hasFlag) {
          this.$set(actData, 'flag', 'added');
        }
        payload.allChecked = payload.actions.every(item => item.checked);
        if (payload.sub_groups && payload.sub_groups.length > 0) {
          payload.actionsAllChecked = payload.allChecked && payload.sub_groups.every(v => {
            return v.actions.every(act => act.checked);
          });
        } else {
          payload.actionsAllChecked = payload.allChecked;
        }
        payload.count++;
        this.handleRelatedActions(actData, true);
      },
      getComputedClass (payload) {
        return payload.checked ? payload.disabled ? 'has-obtained' : 'has-selected' : 'no-obtained';
      },
      handleSubAllChange (newVal, oldVal, val, payload, item) {
        this.setWindowChangeDialog();
        const tempActionIds = [];
        let count = 0;
        payload.actions.forEach(item => {
          if (!item.disabled) {
            if (!item.checked && newVal) {
              ++count;
            }
            item.checked = newVal;
            tempActionIds.push(item.id);
            this.handleRelatedActions(item, newVal);
            const hasFlag = item.hasOwnProperty('flag');
            if (!item.checked) {
              if (hasFlag) {
                if (item.flag === 'selected') {
                  item.flag = 'cancel';
                }
                if (item.flag === 'added') {
                  this.$delete(item, 'flag');
                }
              }
            } else {
              if (hasFlag && item.flag === 'cancel') {
                item.flag = 'selected';
              }
              if (!hasFlag) {
                this.$set(item, 'flag', 'added');
              }
            }
          }
        });
        if (!newVal) {
          item.actionsAllChecked = false;
          item.count = item.count - payload.actions.length;
          return;
        }
        item.actionsAllChecked = item.actions.every(act => act.checked) && item.sub_groups.every(v => {
          return v.actions.every(act => act.checked);
        });
        item.count = item.count + count;
      },
      handleAllChange (newVal, oldVal, val, payload) {
        this.setWindowChangeDialog();
        const tempActionIds = [];
        let count = 0;
        payload.actions.forEach(item => {
          if (!item.disabled) {
            if (!item.checked && newVal) {
              ++count;
            }
            item.checked = newVal;
            tempActionIds.push(item.id);
            this.handleRelatedActions(item, newVal);
            const hasFlag = item.hasOwnProperty('flag');
            if (!item.checked) {
              if (hasFlag) {
                if (item.flag === 'selected') {
                  item.flag = 'cancel';
                }
                if (item.flag === 'added') {
                  this.$delete(item, 'flag');
                }
              }
            } else {
              if (hasFlag && item.flag === 'cancel') {
                item.flag = 'selected';
              }
              if (!hasFlag) {
                this.$set(item, 'flag', 'added');
              }
            }
          }
        });
        if (!newVal) {
          payload.actionsAllChecked = false;
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
        payload.count = payload.count + count;
      }
    }
  };
</script>
<style lang="postcss">
.iam-perm-template-action-wrapper {
    .bk-checkbox-text {
        font-size: 12px;
        .text {
            display: inline-block;
            max-width: 99px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            vertical-align: middle;
            outline: none;
        }
    }
    .action-item {
        padding: 10px 0;
        &.set-border {
            border-bottom: 1px solid #dcdee5;
        }
        &.reset-padding-top {
            padding-top: 0;
        }
        p {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }
        .action-group-name {
            color: #313238;
            font-weight: bold;
            &.set-cursor {
                cursor: pointer;
            }
            i {
                position: relative;
                top: 2px;
                font-size: 24px;
            }
            .count {
                margin-left: 10px;
                font-weight: normal;
                color: #979ba5;
            }
            .delete-count{
                color: #ec4545;
            }
        }
        .check-all {
            position: relative;
            top: 4px;
            color: #3a84ff;
            cursor: pointer;
            &.is-disabled {
                color: #dcdee5;
                cursor: not-allowed;
            }
        }
        .action-content {
            margin: 14px 0 0 0;
            min-height: 50px;
            background: #f5f6fa;
            border-radius: 2px;
            .self-action-content {
                position: relative;
                padding: 20px;
                &.set-border-bottom {
                    border-bottom: 1px solid #fff;
                }
            }
            .sub-group-action-content {
                padding: 20px;
                .sub-action-item {
                    display: flex;
                    justify-content: space-between;
                    position: relative;
                    &.set-margin {
                        margin-top: 10px;
                    }
                    .sub-action-wrapper {
                        display: flex;
                        justify-content: flex-start;
                        width: 100%;
                        .name {
                            display: inline-block;
                            flex: 0 0 130px;
                            line-height: 36px;
                            font-size: 12px;
                            color: #313238;
                            font-weight: 700;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                        }
                    }
                }
            }
            .iam-action-cls {
                width: 175px;
                line-height: 36px;
                .error-icon {
                    font-size: 14px;
                    color: #ffb400;
                }
                .text-through{
                    text-decoration: line-through;
                    text-decoration-color: #ffb400;
                }
            }
            .iam-action-all-cls {
                position: absolute;
                top: 20px;
                right: 20px;
                line-height: 36px;
            }
            .iam-sub-action-all-cls {
                display: inline-block;
                position: absolute;
                right: 0;
                line-height: 36px;
            }
        }
    }
}
</style>

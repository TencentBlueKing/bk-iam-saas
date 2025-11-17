<template>
  <bk-sideslider
    :is-show="isShow"
    :quick-close="quickClose"
    transfer
    :width="960"
    ext-cls="iam-add-action-sideslider"
    :title="$t(`m.grading['添加系统和操作']`)"
    @update:isShow="handleCancel('leave')">
    <div slot="content"
      class="content-wrapper"
      v-bkloading="{ isLoading, opacity: 1 }">
      <template v-if="isShowContent">
        <div class="left-wrapper">
          <div class="search-wrapper">
            <bk-input
              clearable
              right-icon="bk-icon icon-search"
              class="search-wrapper-input"
              v-model="keyword"
              @input="handleInput"
              @enter="handleSearch"
              @right-icon-click="handleSearch"
            />
            <div class="icon-iamcenter-wrapper" @click.stop="handleRefreshList">
              <i class="iam-icon iamcenter-refresh" />
            </div>
          </div>
          <div :class="['system-wrapper', curSystemList.length > 20 ? 'system-item-fixed' : '']">
            <template>
              <template v-if="curSystemList.length > 0">
                <div v-bkloading="{ isLoading: systemListIsLoading, opacity: 1 }">
                  <div class="flex-between system-item"
                    v-for="item in curSystemList"
                    :key="item.id"
                    :class="item.id === curSystem ? 'active' : ''"
                    :title="item.name"
                    @click.stop="handleSysChange(item)">
                    <div :class="['single-hide','system-item-name',{ 'has-badge': systemData[item.id].count }]">
                      {{ item.name }}
                    </div>
                    <template v-if="systemData[item.id].count">
                      <bk-badge
                        :theme="getComputedTheme(item.id)"
                        ext-cls="action-count-badge-cls"
                        :val="systemData[item.id].count" />
                    </template>
                  </div>
                  <!-- <div
                                    v-if="isHierarchicalAdmin.type === 'rating_manager'"
                                    :class="['skip-link', curSystemList.length > 20 ? 'skip-link-fixed' : '']"
                                    :title="$t(`m.grading['修改管理空间授权范围']`)"
                                    @click="handleSkip">
                                    <i class="iam-icon iamcenter-edit-fill"></i>
                                    {{ $t(`m.grading['修改管理空间授权范围']`) }}
                                </div> -->
                </div>
              </template>
              <template v-else>
                <ExceptionEmpty
                  :type="emptyData.type"
                  :empty-text="emptyData.text"
                  :tip-text="emptyData.tip"
                  :tip-type="emptyData.tipType"
                  @on-clear="handleEmptyClear"
                />
              </template>
            </template>
          </div>
        </div>
        <div class="right-wrapper" v-bkloading="{ isLoading: isRightLoading, opacity: 1, color: '#f5f6fa' }">
          <template v-if="systemData[curSystem].list.length > 0 && !isRightLoading">
            <!-- eslint-disable max-len -->
            <render-action-tag
              style="margin: 0;"
              :system-id="curSystem"
              :data="commonActions"
              :tag-action-list="tagActionList"
              mode="detail"
              v-if="!isRightLoading && commonActions.length > 0"
              @on-change="handleActionTagChange" />
            <div
              :class="[
                'custom-tmpl-wrapper',
                { 'custom-tmpl-wrapper-none': !isShowGroupTitle(customTmpl) }
              ]"
              v-for="(customTmpl, index) in systemData[curSystem].list"
              :key="index"
            >
              <label class="bk-label" style="line-height: 20px;" v-if="isShowGroupTitle(customTmpl)">
                <span class="name">{{ customTmpl.name }}</span>
                <span class="select-all" data-test-id="grading_btn_selectAllAction" @click.stop="handleSelectAll(customTmpl, index)">
                  （{{ customTmpl.text }}）
                </span>
              </label>
              <div
                v-if="customTmpl.actions && customTmpl.actions.length > 0"
                :class="['choose-perm-tmpl', { 'set-style': index !== systemData[curSystem].list.length - 1 }]"
              >
                <span v-for="tmpl in customTmpl.actions" :key="tmpl.$id">
                  <bk-checkbox
                    :true-value="true"
                    :false-value="false"
                    v-model="tmpl.checked"
                    ext-cls="custom-action-checkbox-cls"
                    @change="handleActionChange(...arguments, customTmpl, tmpl.id, tmpl)">
                    <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                      <span class="text">{{ tmpl.name }}</span>
                      <div slot="content" class="iam-perm-apply-action-popover-content">
                        <div>
                          <span class="name">{{ tmpl.name }}</span>
                          <span :class="getComputedClass(tmpl)">({{ tmpl.checked ? $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})</span>
                        </div>
                        <div class="description">{{ $t(`m.common['描述']`) + '：' + (tmpl.description || '--') }}</div>
                        <div class="relate-action" v-if="tmpl.related_actions.length > 0">
                          {{ getRelatedActionTips(tmpl.related_actions) }}
                        </div>
                      </div>
                    </bk-popover>
                  </bk-checkbox>
                </span>
              </div>
              <section class="sub-group-wrapper" v-if="isShowGroupSubAction(customTmpl)">
                <div
                  v-for="subItem in customTmpl.sub_groups"
                  :key="subItem.name"
                  :class="[
                    'sub-item',
                    { 'sub-item-none': !subItem.actions.length }
                  ]"
                >
                  <template v-if="subItem.actions && subItem.actions.length > 0">
                    <label class="sub-item-name" :title="subItem.name">{{ subItem.name }}</label>
                    <div class="choose-perm-sub-tmpl">
                      <span v-for="subTmpl in subItem.actions" :key="subTmpl.$id">
                        <bk-checkbox
                          :true-value="true"
                          :false-value="false"
                          v-model="subTmpl.checked"
                          ext-cls="custom-action-checkbox-sub-cls"
                          @change="handleSubActionChange(...arguments, customTmpl, subTmpl, subTmpl.id)">
                          <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                            <span class="text">{{ subTmpl.name }}</span>
                            <div slot="content" class="iam-perm-apply-action-popover-content">
                              <div>
                                <span class="name">{{ subTmpl.name }}</span>
                                <span :class="getComputedClass(subTmpl)">({{ subTmpl.checked ? $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})</span>
                              </div>
                              <div class="description">{{ $t(`m.common['描述']`) + ':' + (subTmpl.description || '--') }}</div>
                              <div class="relate-action" v-if="subTmpl.related_actions.length > 0">
                                {{ getRelatedActionTips(subTmpl.related_actions) }}
                              </div>
                            </div>
                          </bk-popover>
                        </bk-checkbox>
                      </span>
                    </div>
                  </template>
                </div>
              </section>
            </div>
          </template>
          <template v-if="systemData[curSystem].list.length < 1 && !isRightLoading">
            <div class="empty-wrapper">
              <ExceptionEmpty
                :type="emptyData.type"
                :empty-text="emptyData.text"
                :tip-text="emptyData.tip"
                :tip-type="emptyData.tipType"
                @on-clear="handleEmptyClear"
              />
            </div>
          </template>
        </div>
      </template>
      <div v-else style="margin: 0 auto;">
        <ExceptionEmpty />
      </div>
    </div>
    <div slot="footer" style="padding-left: 30px;">
      <bk-button theme="primary" :disabled="isDisabled" @click="handleSubmit"
        data-test-id="grading_btn_addActionConfirm">
        {{ $t(`m.common['确定']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px;" @click="handleCancel('cancel')">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>
  </bk-sideslider>
</template>

<script>
  import _ from 'lodash';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { guid, formatCodeData } from '@/common/util';
  import RenderActionTag from '@/components/common-action';
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    components: {
      RenderActionTag
    },
    props: {
      isShow: {
        type: Boolean,
        default: false
      },
      defaultValue: {
        type: Array,
        default: () => []
      },
      defaultSystem: {
        type: String,
        default: ''
      },
      defaultData: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        keyword: '',
        systemList: [],
        curSystemList: [],
        initRequestQueue: ['system', 'action', 'commonActions'],
        isFilter: false,
        isRightLoading: false,
        curSystem: '',
        systemData: {},
        curSelectValue: [],
        commonActions: [],
        linearAction: [],
        quickClose: false,
        tagActionList: [],
        tagActionListBackUp: [],
        hasSelectedActions: [],
        systemListIsLoading: false,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isLoading () {
          return this.initRequestQueue.length > 0;
      },
      isShowContent () {
          return this.initRequestQueue.length < 1 && this.systemList.length > 0;
      },
      isDisabled () {
          let flag = false;
          if (Object.keys(this.systemData).length > 0) {
              for (const key in this.systemData) {
                  if (!flag) {
                      flag = (this.systemData[key].list || []).some(item => {
                          return (item.actions || []).some(act => act.checked)
                              || (item.sub_groups || []).some(sub => (sub.actions || []).some(v => v.checked));
                      });
                  }
              }
          } else {
              flag = false;
          }
          return this.initRequestQueue.length > 0 || !flag;
      },
      isHierarchicalAdmin () {
          // return this.$store.getters.roleList.find(item => item.id === this.$store.getters.navCurRoleId) || {};
          return this.user.role || {};
      },
      isShowGroupTitle () {
        return (item) => {
          const isExistActions = item.actions && item.actions.length > 0;
            const isExistSubGroup = (item.sub_groups || []).some(v =>
            (v.sub_groups && v.sub_groups.length > 0)
              || (v.actions && v.actions.length > 0)
              );
          return isExistSubGroup || isExistActions;
        };
      },
      isShowGroupSubAction () {
        return (item) => {
          const isExistSubGroup = (item.sub_groups || []).some(v =>
            (v.sub_groups && v.sub_groups.length > 0)
              || (v.actions && v.actions.length > 0)
              );
          return item.sub_groups && item.sub_groups.length > 0 && isExistSubGroup;
        };
      }
    },
    watch: {
      isShow: {
        handler (value) {
          if (value) {
            this.pageChangeAlertMemo = window.changeAlert;
            this.hasSelectedActions = _.cloneDeep(this.defaultValue);
            this.linearAction = [];
            window.changeAlert = 'iamSidesider';
            this.fetchSystems();
          } else {
            window.changeAlert = this.pageChangeAlertMemo;
          }
        },
        immediate: true
      },
      keyword (newVal, oldVal) {
        // 清除keyword时数据重置
        if (newVal === '' && oldVal !== '' && this.isFilter) {
          this.isFilter = false;
          this.curSystemList.splice(0, this.curSystemList.length, ...this.systemList);
        }
      },
      defaultValue (value) {
        // console.error('defaultValue', this.defaultValue)
        // console.error('defaultSystem', this.defaultSystem)
        // console.error('defaultData', this.defaultData)
        if (value.length > 0) {
          this.curSelectValue = [...value];
        }
      },
      isLoading: {
        handler (value) {
          if (!value) {
            this.quickClose = true;
          } else {
            this.quickClose = false;
          }
        },
        immediate: true
      }
    },
    created () {
      this.pageChangeAlertMemo = false;
    },
    methods: {
      handleActionTagChange (flag, selects) {
        window.changeDialog = true;
        if (selects.length < 1) {
          return;
        }
        const curSelects = selects.map(item => {
          return `${this.curSystem}&${item}`;
        });
        const setCurSelected = (value, payload) => {
          const isExistFlag = this.curSelectValue.includes(`${this.curSystem}&${value}`);
          if (payload) {
            if (!isExistFlag) {
              this.curSelectValue.push(`${this.curSystem}&${value}`);
            }
          } else {
            if (isExistFlag) {
              this.curSelectValue = this.curSelectValue.filter(item => item !== `${this.curSystem}&${value}`);
            }
          }
        };
        this.systemData[this.curSystem].list.forEach(payload => {
          payload.actions.forEach(item => {
            if (flag) {
              if (curSelects.includes(item.$id)) {
                if (!item.checked) {
                  item.checked = true;
                  ++this.systemData[this.curSystem].count;
                  this.handleRelatedActions(item, true, item.$id);
                  setCurSelected(item.id, true);
                }
              }
            } else {
              if (curSelects.includes(item.$id)) {
                if (item.checked) {
                  item.checked = false;
                  --this.systemData[this.curSystem].count;
                  this.handleRelatedActions(item, false, item.$id);
                  setCurSelected(item.id, false);
                }
              }
            }
          });
          payload.sub_groups.forEach(item => {
            (item.actions || []).forEach(subItem => {
              if (flag) {
                if (curSelects.includes(subItem.$id)) {
                  if (!subItem.checked) {
                    subItem.checked = true;
                    ++this.systemData[this.curSystem].count;
                    this.handleRelatedActions(subItem, true, subItem.$id);
                    setCurSelected(subItem.id, true);
                  }
                }
              } else {
                if (curSelects.includes(subItem.$id)) {
                  if (subItem.checked) {
                    subItem.checked = false;
                    --this.systemData[this.curSystem].count;
                    this.handleRelatedActions(subItem, false, subItem.$id);
                    setCurSelected(subItem.id, false);
                  }
                }
              }
            });
          });

          const checked = payload.actions.every(item => item.checked);
          let subChecked = true;
          if (payload.sub_groups.length) {
            subChecked = payload.sub_groups.every(item => {
              return item.actions.every(v => v.checked);
            });
          }
          const allChecked = checked && subChecked;
          payload.text = allChecked ? this.$t(`m.common['取消全选']`) : this.$t(`m.common['全选']`);
        });

        if (this.curSelectValue.length) {
          this.tagActionList = this.curSelectValue.map(e => {
            return e.split('&')[1];
          });
        } else {
          this.tagActionList = [];
        }
      },

      getRelatedActionTips (payload) {
        const relatedActions = this.linearAction.filter(item => payload.includes(item.id));
        return `${this.$t(`m.common['依赖操作']`)}: ${relatedActions.map(item => item.name).join('，')}`;
      },

      handleRelatedActions (payload, flag, $id) {
        const setCurSelected = (value, data) => {
          const isExistFlag = this.curSelectValue.includes(`${this.curSystem}&${value}`);
          if (data) {
            if (!isExistFlag) {
              this.curSelectValue.push(`${this.curSystem}&${value}`);
            }
          } else {
            if (isExistFlag) {
              this.curSelectValue = this.curSelectValue.filter(item => item !== `${this.curSystem}&${value}`);
            }
          }
        };
        this.systemData[this.curSystem].list.forEach((item, index) => {
          item.actions.forEach(act => {
            if (payload.related_actions.includes(act.id) && flag) {
              if (!act.checked) {
                act.checked = true;
                if (`${this.curSystem}&${act.id}` !== $id) {
                  ++this.systemData[this.curSystem].count;
                  setCurSelected(act.id, true);
                }
              }
            }
            if (act.related_actions.includes(payload.id) && !flag) {
              if (act.checked) {
                act.checked = false;
                if (`${this.curSystem}&${act.id}` !== $id) {
                  if (this.systemData[this.curSystem].count > 0) {
                    --this.systemData[this.curSystem].count;
                    setCurSelected(act.id, false);
                  }
                }
              }
            }
          });

          (item.sub_groups || []).forEach(sub => {
            sub.actions.forEach(act => {
              if (payload.related_actions.includes(act.id) && flag) {
                if (!act.checked) {
                  act.checked = true;
                  if (`${this.curSystem}&${act.id}` !== $id) {
                    ++this.systemData[this.curSystem].count;
                    setCurSelected(act.id, true);
                  }
                }
              }
              if (act.related_actions.includes(payload.id) && !flag) {
                if (act.checked) {
                  act.checked = false;
                  if (`${this.curSystem}&${act.id}` !== $id) {
                    if (this.systemData[this.curSystem].count > 0) {
                      --this.systemData[this.curSystem].count;
                      setCurSelected(act.id, false);
                    }
                  }
                }
              }
            });
          });

          const checked = item.actions.every(item => item.checked);
          let subChecked = true;
          if (item.sub_groups.length) {
            subChecked = item.sub_groups.every(item => {
              return item.actions.every(v => v.checked);
            });
          }
          const allChecked = checked && subChecked;
          item.text = allChecked ? this.$t(`m.common['取消全选']`) : this.$t(`m.common['全选']`);
        });
      },

      /**
       * 获取系统对应的常用操作
       *
       * @param {String} systemId 系统id
       */
      async fetchCommonActions (systemId) {
        try {
          const { code, data } = await this.$store.dispatch('permApply/getUserCommonAction', { systemId });
          this.commonActions.splice(0, this.commonActions.length, ...(data || []));
          this.emptyData = formatCodeData(code, this.emptyData, this.commonActions.length === 0);
          this.commonActions.forEach(item => {
            item.$id = guid();
          });
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          this.initRequestQueue.shift();
        }
      },

      /**
       * 获取系统列表
       */
      async fetchSystems () {
        this.systemListIsLoading = true;
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('system/getSystems', params);
          this.systemList = _.cloneDeep(data);
          this.curSystemList = _.cloneDeep(data);
          this.curSystem = this.defaultSystem;
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
          if (this.systemList.length) {
            if (!this.curSystem) {
              this.curSystem = this.systemList[0].id;
            }
            this.systemList.forEach(item => {
              this.$set(this.systemData, item.id, {});
              this.systemData[item.id].system_name = item.name;
              this.$set(this.systemData[item.id], 'count', 0);
              this.$set(this.systemData[item.id], 'list', []);
              const isExistSys = this.defaultData.find(sys => sys.system_id === item.id);
              if (isExistSys) {
                isExistSys.list.forEach(act => {
                  this.$set(act, 'checked', this.defaultValue.includes(act.$id));
                });
                this.systemData[item.id].list.push({
                  name: '',
                  actions: _.cloneDeep(isExistSys.list)
                });
              }
    
              if (this.defaultValue.length > 0) {
                const curAllActionIds = [];
                this.systemData[item.id].list.forEach(subItem => {
                  subItem.actions.forEach(act => {
                    curAllActionIds.push(act.$id);
                  });
                });
                const intersection = curAllActionIds.filter(v => this.defaultValue.includes(v));
                this.systemData[item.id].count = intersection.length;
              }
            });
          }
          await Promise.all([
            this.fetchCommonActions(this.curSystem, false),
            this.fetchActions(this.curSystem)
          ]);
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          this.initRequestQueue.shift();
          this.systemListIsLoading = false;
        }
      },

      getComputedClass (payload) {
        return payload.checked ? 'has-selected' : 'no-obtained';
      },

      /**
       * 获取系统对应的自定义操作
       *
       * @param {String} systemId 系统id
       * @param {Boolean} isLoading 是否loading
       */
      async fetchActions (systemId, isLoading = true) {
        this.isRightLoading = isLoading;
        const params = {
          system_id: systemId
        };
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const { code, data } = await this.$store.dispatch('permApply/getActions', params);
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
          this.handleDefaultData(systemId, data);
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          this.isRightLoading = false;
          this.initRequestQueue.length > 0 && this.initRequestQueue.shift();
        }
      },

      handleDefaultData (payload, data) {
        if (this.systemData[payload]) {
          this.tagActionListBackUp = [];
          this.$set(this.systemData[payload], 'count', 0);
          this.$set(this.systemData[payload], 'list', _.cloneDeep(data));
          this.systemData[payload].list.forEach((item) => {
            if (!item.actions) {
              item.actions = [];
            }
            if (!item.sub_groups) {
              item.sub_groups = [];
            }
            let allChecked = true;
            // item.actions = item.actions.filter(v => !v.hidden);
            item.actions.forEach(act => {
              act.$id = `${payload}&${act.id}`;
              act.related_resource_types.forEach(v => {
                v.type = v.id;
              });
              this.$set(act, 'checked', this.defaultValue.includes(act.$id) || this.curSelectValue.includes(act.$id));
              if (!act.checked) {
                allChecked = false;
              }
              if (act.checked) {
                this.tagActionListBackUp.push(act.id);
              }
              this.linearAction.push(act);
            });
            item.sub_groups.forEach(act => {
              // act.actions = act.actions.filter(v => !v.hidden);
              (act.actions || []).forEach(v => {
                v.$id = `${payload}&${v.id}`;
                v.related_resource_types.forEach(subItem => {
                  subItem.type = subItem.id;
                });
                this.$set(v, 'checked', this.defaultValue.includes(v.$id) || this.curSelectValue.includes(v.$id));
                if (!v.checked) {
                  allChecked = false;
                }
                if (v.checked) {
                  this.tagActionListBackUp.push(v.id);
                }
                this.linearAction.push(v);
              });
            });
            this.$set(item, 'text', allChecked ? this.$t(`m.common['取消全选']`) : this.$t(`m.common['全选']`));
          });
          const curSystem = this.systemList.find((item) => item.id === payload);
          if (curSystem) {
            const hasSelectedActions = this.linearAction.filter((v) => v.checked);
            this.systemData[payload] = Object.assign(this.systemData[payload], {
              system_name: curSystem.name,
              count: hasSelectedActions.length
            });
          }
        }
      },

      handleSelectAll (payload, index) {
        window.changeAlert = true;
        const hasSelectValue = payload.actions.filter(item => item.checked).map(item => item.$id);
        const actionIds = [];
        payload.actions.forEach(item => {
          actionIds.push(item.$id);
        });
        payload.sub_groups.forEach(item => {
          (item.actions || []).forEach(subItem => {
            actionIds.push(subItem.$id);
            if (subItem.checked) {
              hasSelectValue.push(subItem.$id);
            }
          });
        });

        const differenceSetIds = actionIds.filter(item => !hasSelectValue.includes(item));

        payload.text = this.$t(`m.common['取消全选']`);
        if (differenceSetIds.length > 0) {
          payload.actions.forEach(item => {
            this.$set(item, 'checked', true);
            this.handleRelatedActions(item, true, `${this.curSystem}&${item.id}`);
          });
          payload.sub_groups.forEach(item => {
            (item.actions || []).forEach(subItem => {
              this.$set(subItem, 'checked', true);
              this.handleRelatedActions(subItem, true, `${this.curSystem}&${subItem.id}`);
            });
          });
          this.curSelectValue.push(...differenceSetIds);
          this.setCurSelectedCount();
          return;
        }
        payload.text = this.$t(`m.common['全选']`);
        payload.actions.forEach(item => {
          this.$set(item, 'checked', false);
          this.handleRelatedActions(item, false, `${this.curSystem}&${item.id}`);
        });
        payload.sub_groups.forEach(item => {
          (item.actions || []).forEach(subItem => {
            this.$set(subItem, 'checked', false);
            this.handleRelatedActions(subItem, false, `${this.curSystem}&${subItem.id}`);
          });
        });
        this.curSelectValue = this.curSelectValue.filter(item => !actionIds.includes(item));

        this.setCurSelectedCount();
      },

      setCurSelectedCount () {
        let count = 0;
        this.systemData[this.curSystem].list.forEach((item, index) => {
          item.actions.forEach(act => {
            if (act.checked) {
              ++count;
            }
          })

          ;(item.sub_groups || []).forEach(sub => {
            sub.actions.forEach(act => {
              if (act.checked) {
                ++count;
              }
            });
          });
        });

        this.systemData[this.curSystem].count = count;
      },

      getComputedTheme (payload) {
        if (payload === this.curSystem) {
          return '#3a84ff';
        }
        return '#c3cdd7';
      },

      handleActionChange (curVal, oldVal, val, payload, value, item) {
        window.changeAlert = true;
        const checked = payload.actions.every(item => item.checked);
        let subChecked = true;
        if (payload.sub_groups.length) {
          subChecked = payload.sub_groups.every(item => {
            return item.actions.every(v => v.checked);
          });
        }
        const allChecked = checked && subChecked;
        payload.text = allChecked ? this.$t(`m.common['取消全选']`) : this.$t(`m.common['全选']`);

        const $id = `${this.curSystem}&${value}`;
        if (curVal) {
          ++this.systemData[this.curSystem].count;
          this.curSelectValue.push($id);
          this.handleRelatedActions(item, true, $id);
        } else {
          const index = this.curSelectValue.findIndex(item => item === $id);
          index > -1 && this.curSelectValue.splice(index, 1);
          if (this.systemData[this.curSystem].count > 0) {
            --this.systemData[this.curSystem].count;
          }
          this.handleRelatedActions(item, false, $id);
        }
      },

      handleSubActionChange (curVal, oldVal, val, parent, payload, value) {
        window.changeAlert = true;
        const checked = parent.actions.every(item => item.checked);
        let subChecked = true;
        if (parent.sub_groups.length) {
          subChecked = parent.sub_groups.every(item => {
            return item.actions.every(v => v.checked);
          });
        }
        const allChecked = checked && subChecked;
        parent.text = allChecked ? this.$t(`m.common['取消全选']`) : this.$t(`m.common['全选']`);

        const $id = `${this.curSystem}&${value}`;
        if (curVal) {
          ++this.systemData[this.curSystem].count;
          this.curSelectValue.push($id);
          this.handleRelatedActions(payload, true, $id);
        } else {
          const index = this.curSelectValue.findIndex(item => item === $id);
          index > -1 && this.curSelectValue.splice(index, 1);
          if (this.systemData[this.curSystem].count > 0) {
            --this.systemData[this.curSystem].count;
          }
          this.handleRelatedActions(payload, false, $id);
        }
      },

      handleSubmit () {
        const tempData = [];
        for (const key in this.systemData) {
          const curData = this.systemData[key];
          const { list } = curData;
          const isSelect = list.some(item => {
            return item.actions.some(act => act.checked)
              || item.sub_groups.some(sub => sub.actions.some(v => v.checked));
          });
          if (isSelect) {
            list.forEach(item => {
              (item.actions || []).forEach(subItem => {
                if (subItem.checked) {
                  tempData.push({
                    system_id: key,
                    system_name: curData.system_name,
                                        ...subItem,
                    $id: `${key}&${subItem.id}`
                  });
                }
              })
              ;(item.sub_groups || []).forEach(subItem => {
                (subItem.actions || []).forEach(act => {
                  if (act.checked) {
                    tempData.push({
                      system_id: key,
                      system_name: curData.system_name,
                                            ...act,
                      $id: `${key}&${act.id}`
                    });
                  }
                });
              });
            });
          }
        }
        this.$emit('update:isShow', false);
        this.$emit('on-submit', tempData);
        this.resetData();
      },

      async handleSysChange (payload) {
        window.changeAlert = true;
        if (this.curSystem === payload.id) {
          return;
        }
        this.curSystem = payload.id;
        this.linearAction = [];
        await Promise.all([
          this.fetchActions(this.curSystem),
          this.fetchCommonActions(this.curSystem)
        ]);
        this.tagActionList = [...this.tagActionListBackUp];
      },

      handleInput () {
        window.changeAlert = true;
      },

      handleSearch () {
        if (!this.keyword) {
          return;
        }
        this.emptyData = formatCodeData(0, { ...this.emptyData, ...{ tipType: 'search' } });
        window.changeAlert = true;
        this.isFilter = true;
        const filterList = this.systemList.filter(item => item.name.indexOf(this.keyword) > -1);
        this.curSystemList.splice(0, this.curSystemList.length, ...filterList);
      },

      resetData () {
        this.initRequestQueue = ['system', 'action', 'commonActions'];
        this.keyword = '';
        this.systemList = [];
        this.curSystemList = [];
        this.systemData = {};
        this.isFilter = false;
        this.curSystem = '';
        this.curSelectValue = [];
        this.linearAction = [];
      },

      fetchErrorMsg (payload) {
        console.error(payload);
        const { code } = payload;
        this.emptyData = formatCodeData(code, this.emptyData);
        this.messageAdvancedError(payload);
      },

      handleCancel (payload) {
        const operateMap = {
          leave: () => {
            let cancelHandler = Promise.resolve();
            if (window.changeAlert) {
              cancelHandler = leaveConfirm();
            }
            cancelHandler.then(() => {
              this.$emit('update:isShow', false);
              this.resetData();
            }, _ => _);
          },
          cancel: () => {
            this.$emit('update:isShow', false);
            this.resetData();
          }
        };
        operateMap[payload]();
      },

      handleSkip () {
        this.$router.push({
          name: 'gradingAdminEdit',
          params: {
            id: this.$store.getters.navCurRoleId
          }
        });
      },

      handleEmptyClear () {
        this.keyword = '';
        this.emptyData.tipType = '';
        this.handleRefreshList();
      },

      handleEmptyRefresh () {
        this.resetData();
        this.fetchSystems();
      },

      handleRefreshList () {
        this.keyword = '';
        this.linearAction = [];
        this.fetchSystems();
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import "@/css/mixins/iam-add-action-slider.css";
</style>

<template>
  <div class="iam-system-access-optimize-wrapper">
    <div class="inner">
      <bk-steps class="system-access-step" ref="systemAccessStep" direction="vertical"
        :steps="controllableSteps.steps"
        :controllable="controllableSteps.controllable"
        :cur-step.sync="controllableSteps.curStep"
        :before-change="beforeStepChanged"
      >
      </bk-steps>
      <smart-action class="content-wrapper">
        <render-horizontal-block :label="$t(`m.access['操作分组']`)">
          <template>
            <div id="container-pop">
              <pop-content
                :title="$t(`m.access['什么是操作分组？']`)"
                :desc="$t(`m.access['操作分组可以让用户在申请权限时更方便的找到想要的操作。']`)"
                :image="operationGroupImage"
              ></pop-content>
            </div>
            <Icon class="icon-info-regis" type="info-new" v-bk-tooltips="htmlConfig" />
          </template>
          <div v-bkloading="{ isLoading: groupActionLoading, opacity: 0.8 }">
            <div class="action-no-group-list-wrapper">
              <div class="action-item set-border reset-padding-top">
                <p class="title-wrapper">
                  <section class="action-group-name">
                    <span class="name"> {{$t(`m.permTemplate['未分组操作']`)}}</span>
                  </section>
                </p>
                <div class="action-content no-bg" v-if="noGroupActionList.length">
                  <div class="sub-group-action-content">
                    <section class="sub-action-item">
                      <section>
                        <div class="text" v-for="(item, index) in noGroupActionList"
                          :key="index">{{ item.name }}
                        </div>
                      </section>
                    </section>
                  </div>
                </div>
                <div class="action-content no-bg no-data" v-else>
                  {{$t(`m.access['暂无未分组操作']`)}}
                </div>
              </div>
            </div>
            <section class="new-add-group" v-if="!groupList.length">
              <bk-button theme="primary" text @click="showAddGroupSameLevel(0)">
                <Icon type="add-small" />
                {{ $t(`m.access['新增操作分组']`) }}
              </bk-button>
            </section>

            <div class="action-group-list-wrapper">
              <div
                v-for="(group, index) in groupList"
                :key="index"
                class="action-item set-border">
                <p class="title-wrapper" @click.stop="handleExpanded(group)">
                  <section class="action-group-name">
                    <Icon :type="group.expanded ? 'down-angle' : 'right-angle'" />
                    <span class="name">{{ group.name }}</span>
                  </section>
                </p>
                <div class="btn-wrapper">
                  <bk-button text size="small" theme="primary"
                    @click="showAddGroupSameLevel(index)">
                    {{ $t(`m.access['添加同级分组']`) }}
                  </bk-button>
                  <bk-button text size="small"
                    @click="showAddGroupSubLevel(group, index)">
                    {{ $t(`m.access['添加子分组']`) }}
                  </bk-button>
                  <bk-button text size="small"
                    @click="showEditGroup(group, index)">
                    {{ $t(`m.common['编辑']`) }}
                  </bk-button>
                  <bk-button text size="small"
                    @click="delGroup(group, index)">
                    {{ $t(`m.common['删除']`) }}
                  </bk-button>
                </div>
                <!-- eslint-disable max-len -->
                <div class="action-content" v-if="group.expanded">
                  <div class="self-action-content set-border-bottom"
                    v-if="group.actions && group.actions.length">
                    <div class="iam-action-cls" v-for="(act, actIndex) in group.actions" :key="actIndex">
                      <span class="bk-checkbox-text">
                        <span class="text">{{ act.name || act.id }}</span>
                      </span>
                    </div>
                  </div>
                  <div class="sub-group-action-content">
                    <section
                      v-for="(subGroup, subGroupIndex) in group.sub_groups"
                      :key="subGroupIndex"
                      class="sub-action-item">
                      <div class="sub-action-wrapper">
                        <span class="name" :title="subGroup.name">{{ subGroup.name }}</span>
                        <section>
                          <div class="text" v-for="(subGroupAct, subGroupActIndex) in subGroup.actions" :key="subGroupActIndex">
                            {{ subGroupAct.name || subGroupAct.id }}
                          </div>
                        </section>
                        <div class="btn-wrapper" style="top: 11px;">
                          <bk-button text size="small" @click="showEditSubGroup(group, index, subGroup, subGroupIndex)">{{ $t(`m.common['编辑']`) }}</bk-button>
                          <bk-button text size="small" @click="delSubGroup(group, index, subGroup, subGroupIndex)">{{ $t(`m.common['删除']`) }}</bk-button>
                        </div>
                      </div>
                    </section>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </render-horizontal-block>

        <render-horizontal-block :label="$t(`m.access['常用操作']`)">
          <template>
            <div id="container-pop">
              <pop-content
                :title="$t(`m.access['什么是常用操作？']`)"
                :desc="$t(`m.access['常用操作可以让用户在申请权限时可以一次性选择某一类角色需要的操作。']`)"
                :image="operationCommonImage"
              ></pop-content>
            </div>
            <Icon class="icon-info-regis" type="info-new" v-bk-tooltips="htmlConfig" />
          </template>
          <div v-bkloading="{ isLoading: commonActionLoading, opacity: 0.8 }">
            <div class="common-action-list-wrapper">
              <div
                v-for="(common, index) in commonList"
                :key="index"
                class="action-item set-border" :class="index === 0 ? 'reset-padding-top' : ''">
                <p class="title-wrapper">
                  <section class="action-group-name">
                    <span class="name">{{ common.name }}</span>
                  </section>
                </p>
                <div class="btn-wrapper" :class="index === 0 ? 'reset-top' : ''">
                  <bk-button text size="small" @click="showEditCommon(common, index)">{{ $t(`m.common['编辑']`) }}</bk-button>
                  <bk-button text size="small" @click="delCommon(common, index)">{{ $t(`m.common['删除']`) }}</bk-button>
                </div>
                <div class="action-content no-bg">
                  <div class="self-action-content set-border-bottom" v-if="common.actions && common.actions.length">
                    <div>
                      <div class="iam-action-cls">
                        <span v-for="(act, actIndex) in allActionList" :key="actIndex">
                          <span class="bk-checkbox-text" v-for="(actions, actionsIndex) in common.actions" :key="actionsIndex" v-show="actions.id === act.id">
                            <span class="text">{{ act.name || act.id }}</span>
                          </span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <section class="new-add-common">
              <bk-button theme="primary" text @click="showAddCommon">
                <Icon type="add-small" />
                {{ $t(`m.access['新增常用分组']`) }}
              </bk-button>
            </section>
          </div>
        </render-horizontal-block>

        <div slot="action">
          <bk-button theme="primary" type="button" @click="handleSubmit('systemAccessComplete')">
            {{ $t(`m.common['下一步']`) }}
          </bk-button>
          <bk-button style="margin-left: 10px;" @click="handlePrev">{{ $t(`m.common['上一步']`) }}</bk-button>
        </div>
      </smart-action>

      <add-group-dialog
        :show.sync="isShowAddGroupDialog"
        :modeling-id="modelingId"
        :group-list="groupList"
        :no-group-action-list="noGroupActionList"
        :add-group-index="addGroupIndex"
        @on-after-leave="addGroupAfterLeave"
        @on-success="addGroupSuccess"
        @on-hide="addGroupHide">
      </add-group-dialog>

      <add-sub-group-dialog
        :show.sync="isShowAddSubGroupDialog"
        :modeling-id="modelingId"
        :group-list="groupList"
        :no-group-action-list="noGroupActionList"
        :prepare-add-group-parent="prepareAddGroupParent"
        :prepare-add-group-parent-index="prepareAddGroupParentIndex"
        @on-after-leave="addSubGroupAfterLeave"
        @on-success="addSubGroupSuccess"
        @on-hide="addSubGroupHide">
      </add-sub-group-dialog>

      <edit-group-dialog
        :show.sync="isShowEditGroupDialog"
        :modeling-id="modelingId"
        :group-list="groupList"
        :no-group-action-list="noGroupActionList"
        :cur-edit-group="curEditGroup"
        :cur-edit-group-index="curEditGroupIndex"
        @on-after-leave="editGroupAfterLeave"
        @on-success="editGroupSuccess"
        @on-hide="editGroupHide">
      </edit-group-dialog>

      <edit-sub-group-dialog
        :show.sync="isShowEditSubGroupDialog"
        :modeling-id="modelingId"
        :group-list="groupList"
        :no-group-action-list="noGroupActionList"
        :cur-edit-parent-group="curEditParentGroup"
        :cur-edit-parent-group-index="curEditParentGroupIndex"
        :cur-edit-sub-group="curEditSubGroup"
        :cur-edit-sub-group-index="curEditSubGroupIndex"
        @on-after-leave="editSubGroupAfterLeave"
        @on-success="editSubGroupSuccess"
        @on-hide="editSubGroupHide">
      </edit-sub-group-dialog>

      <add-common-dialog
        :show.sync="isShowAddCommonDialog"
        :modeling-id="modelingId"
        :common-list="commonList"
        :all-action-list="allActionList"
        @on-success="addCommonSuccess"
        @on-hide="addCommonHide">
      </add-common-dialog>

      <edit-common-dialog
        :show.sync="isShowEditCommonDialog"
        :modeling-id="modelingId"
        :common-list="commonList"
        :all-action-list="allActionList"
        :cur-edit-common="curEditCommon"
        :cur-edit-common-index="curEditCommonIndex"
        @on-after-leave="editCommonAfterLeave"
        @on-success="editCommonSuccess"
        @on-hide="editCommonHide">
      </edit-common-dialog>
    </div>
  </div>
</template>
<script>
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import AddGroupDialog from './add-group-dialog.vue';
  import AddSubGroupDialog from './add-sub-group-dialog.vue';
  import EditGroupDialog from './edit-group-dialog.vue';
  import EditSubGroupDialog from './edit-sub-group-dialog.vue';
  import AddCommonDialog from './add-common-dialog.vue';
  import EditCommonDialog from './edit-common-dialog.vue';
  import beforeStepChangedMixin from '../common/before-stepchange';
  import PopContent from '../common/pop-content';
  import operationGroupImage from '@/images/operation-group.png';
  import operationCommonImage from '@/images/operation-common.png';

  export default {
    name: '',
    components: {
      AddGroupDialog,
      AddSubGroupDialog,
      EditGroupDialog,
      EditSubGroupDialog,
      AddCommonDialog,
      EditCommonDialog,
      PopContent
    },
    mixins: [beforeStepChangedMixin],
    data () {
      return {
        modelingId: '',

        controllableSteps: {
          controllable: true,
          steps: [
            { title: this.$t(`m.access['注册系统']`), icon: 1 },
            { title: this.$t(`m.access['注册操作']`), icon: 2 },
            { title: this.$t(`m.access['体验优化']`), icon: 3 },
            { title: this.$t(`m.access['完成']`), icon: 4 }
          ],
          curStep: 3
        },
        allActionIdNameMap: {},
        allActionList: [],
        groupList: [],
        noGroupActionList: [],

        commonList: [],

        isShowAddGroupDialog: false,
        // 将要添加的同级分组的索引，添加同级分组时才有效
        addGroupIndex: -1,

        isShowAddSubGroupDialog: false,
        // 将要添加的子分组的父级分组的索引，添加子分组时才有效
        prepareAddGroupParentIndex: -1,
        // 将要添加的子分组的父级分组，添加子分组时才有效
        prepareAddGroupParent: null,

        groupActionLoading: false,

        isShowEditGroupDialog: false,
        // 当前更新的 group
        curEditGroup: null,
        // 当前更新的 group 的索引
        curEditGroupIndex: -1,

        isShowEditSubGroupDialog: false,
        // 当前更新的子 group 的父级 group
        curEditParentGroup: null,
        // 当前更新的子 group 的父级 group 的索引
        curEditParentGroupIndex: -1,
        // 当前更新的子 group
        curEditSubGroup: null,
        // 当前更新的子 group 的索引
        curEditSubGroupIndex: -1,

        commonActionLoading: false,
        isShowAddCommonDialog: false,
        isShowEditCommonDialog: false,
        curEditCommon: null,
        curEditCommonIndex: -1,
        operationGroupImage,
        operationCommonImage,
        htmlConfig: {
          allowHtml: true,
          width: 520,
          trigger: 'click',
          theme: 'light',
          content: '#container-pop',
          placement: 'right-start'
        }
      };
    },
    mounted () {
      const stepNode = this.$refs.systemAccessStep.$el;
      if (stepNode) {
        const children = Array.from(stepNode.querySelectorAll('.bk-step') || []);
        children.forEach(child => {
          child.classList.remove('current');
        });
        children[2].classList.add('current');
      }
    },
    methods: {
      // stepChanged (index) {
      //     if (index === 2) {
      //         this.handlePrev()
      //     } else if (index === 4) {
      //         this.handleSubmit()
      //     }
      // },
      /**
       * fetchPageData
       */
      async fetchPageData () {
        const modelingId = this.$route.params.id;
        if (modelingId === null || modelingId === undefined || modelingId === '') {
          return;
        }

        this.modelingId = modelingId;

        await Promise.all([
          this.fetchAllActionList(),
          this.fetchGroupList(),
          this.fetchCommonList()
        ]);

        this.refreshNoGroupAction();
      },

      /**
       * refreshNoGroupAction
       */
      refreshNoGroupAction () {
        const groupActionIds = [];
        this.groupList.forEach(group => {
          if (group.sub_groups) {
            group.sub_groups.forEach(subGroup => {
              subGroup.actions.forEach(subGroupAction => {
                subGroupAction.name = this.allActionIdNameMap[subGroupAction.id].name;
                subGroupAction.name_en = this.allActionIdNameMap[subGroupAction.id].name_en;
                groupActionIds.push(subGroupAction.id);
              });
            });
          }
          group.actions.forEach(groupAction => {
            groupAction.name = this.allActionIdNameMap[groupAction.id].name;
            groupAction.name_en = this.allActionIdNameMap[groupAction.id].name_en;
            groupActionIds.push(groupAction.id);
          });
        });

        const noGroupActionList = this.allActionList.filter(item => groupActionIds.indexOf(item.id) < 0);
        this.noGroupActionList.splice(0, this.noGroupActionList.length, ...noGroupActionList);
      },

      /**
       * fetchAllActionList
       */
      async fetchAllActionList () {
        try {
          const resModeling = await this.$store.dispatch('access/getModeling', {
            id: this.modelingId,
            data: {
              type: 'action'
            }
          });
          const allActionList = [];
          allActionList.splice(0, 0, ...(resModeling.data || []));

          const allActionIdNameMap = {};
          allActionList.forEach(item => {
            allActionIdNameMap[item.id] = item;
          });
          this.allActionIdNameMap = Object.assign({}, allActionIdNameMap);

          this.allActionList.splice(0, this.allActionList.length, ...allActionList);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      /**
       * fetchGroupList
       */
      async fetchGroupList () {
        try {
          const resModeling = await this.$store.dispatch('access/getModeling', {
            id: this.modelingId,
            data: {
              type: 'action_groups'
            }
          });
          const groupList = [];
          groupList.splice(0, 0, ...(resModeling.data || []));
          groupList.forEach((item, index) => {
            item.expanded = index === 0;
          });

          this.groupList.splice(0, this.groupList.length, ...groupList);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      /**
       * fetchCommonList
       */
      async fetchCommonList () {
        try {
          const resModeling = await this.$store.dispatch('access/getModeling', {
            id: this.modelingId,
            data: {
              type: 'common_actions'
            }
          });
          const commonList = [];
          commonList.splice(0, 0, ...(resModeling.data || []));

          this.commonList.splice(0, this.commonList.length, ...commonList);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      /**
       * handleExpanded
       */
      handleExpanded (item) {
        item.expanded = !item.expanded;
      },

      /**
       * showAddGroupSameLevel
       */
      showAddGroupSameLevel (index) {
        this.isShowAddGroupDialog = true;
        this.addGroupIndex = index;
      },

      /**
       * addGroupAfterLeave
       */
      addGroupAfterLeave () {
        this.addGroupIndex = -1;
      },

      /**
       * addGroupSuccess
       */
      async addGroupSuccess () {
        this.isShowAddGroupDialog = false;
        this.groupActionLoading = true;
        try {
          const r = await Promise.all([
            this.fetchAllActionList(),
            this.$store.dispatch('access/getModeling', {
              id: this.modelingId,
              data: {
                type: 'action_groups'
              }
            })
          ]);

          const groupList = [];
          groupList.splice(0, 0, ...this.groupList);

          const res = r[1] || {};
          const newGroupList = res.data || [];
          newGroupList.forEach((group, index) => {
            if (!groupList.filter(g => g.name === group.name).length) {
              group.expanded = false;
              groupList.splice(index, 0, group);
            }
          });
          this.groupList.splice(0, this.groupList.length, ...groupList);

          this.refreshNoGroupAction();
        } catch (e) {
          console.error(e);
        } finally {
          this.groupActionLoading = false;
        }
      },

      /**
       * addGroupHide
       */
      addGroupHide () {
        this.isShowAddGroupDialog = false;
      },

      /**
       * showAddGroupSubLevel
       */
      showAddGroupSubLevel (item, index) {
        this.isShowAddSubGroupDialog = true;
        this.prepareAddGroupParentIndex = index;
        this.prepareAddGroupParent = Object.assign({}, item);
      },

      /**
       * addSubGroupAfterLeave
       */
      addSubGroupAfterLeave () {
        this.prepareAddGroupParentIndex = -1;
        this.prepareAddGroupParent = null;
      },

      /**
       * 添加子分组 成功后的回调函数
       *
       * @param {number} prepareAddGroupParentIndex 将要添加的子分组的父级分组的索引
       */
      async addSubGroupSuccess (prepareAddGroupParentIndex) {
        this.isShowAddSubGroupDialog = false;
        this.groupActionLoading = true;
        try {
          const r = await Promise.all([
            this.fetchAllActionList(),
            this.$store.dispatch('access/getModeling', {
              id: this.modelingId,
              data: {
                type: 'action_groups'
              }
            })
          ]);

          const groupList = [];
          groupList.splice(0, 0, ...this.groupList);

          const res = r[1] || {};
          const newGroupList = res.data || [];
          newGroupList.forEach((group, index) => {
            if (index === prepareAddGroupParentIndex) {
              group.expanded = groupList[index].expanded;
              this.$set(groupList, index, group);
            }
          });
          this.groupList.splice(0, this.groupList.length, ...groupList);

          this.refreshNoGroupAction();
        } catch (e) {
          console.error(e);
        } finally {
          this.groupActionLoading = false;
        }
      },

      /**
       * addSubGroupHide
       */
      addSubGroupHide () {
        this.isShowAddSubGroupDialog = false;
      },

      /**
       * showEditGroup
       */
      showEditGroup (item, index) {
        this.isShowEditGroupDialog = true;
        this.curEditGroup = item;
        this.curEditGroupIndex = index;
      },

      /**
       * editGroupAfterLeave
       */
      editGroupAfterLeave () {
        this.curEditGroup = null;
        this.curEditGroupIndex = -1;
      },

      /**
       * 编辑组 成功后的回调函数
       *
       * @param {number} curEditGroupIndex 编辑的组的索引
       */
      async editGroupSuccess (curEditGroupIndex) {
        this.isShowEditGroupDialog = false;
        this.groupActionLoading = true;
        try {
          const r = await Promise.all([
            this.fetchAllActionList(),
            this.$store.dispatch('access/getModeling', {
              id: this.modelingId,
              data: {
                type: 'action_groups'
              }
            })
          ]);

          const groupList = [];
          groupList.splice(0, 0, ...this.groupList);

          const res = r[1] || {};
          const newGroupList = res.data || [];
          newGroupList.forEach((group, index) => {
            if (index === curEditGroupIndex) {
              group.expanded = groupList[index].expanded;
              this.$set(groupList, index, group);
            }
          });

          this.groupList.splice(0, this.groupList.length, ...groupList);

          this.refreshNoGroupAction();
        } catch (e) {
          console.error(e);
        } finally {
          this.groupActionLoading = false;
        }
      },

      /**
       * editGroupHide
       */
      editGroupHide () {
        this.isShowEditGroupDialog = false;
      },

      /**
       * showEditSubGroup
       */
      showEditSubGroup (group, index, subGroup, subGroupIndex) {
        this.isShowEditSubGroupDialog = true;
        this.curEditParentGroup = group;
        this.curEditParentGroupIndex = index;
        this.curEditSubGroup = subGroup;
        this.curEditSubGroupIndex = subGroupIndex;
      },

      /**
       * editSubGroupAfterLeave
       */
      editSubGroupAfterLeave () {
        this.curEditParentGroup = null;
        this.curEditParentGroupIndex = -1;
        this.curEditSubGroup = null;
        this.curEditSubGroupIndex = -1;
      },

      /**
       * 编辑子分组 成功后的回调函数
       *
       * @param {number} curEditParentGroupIndex 将要添加的子分组的父级分组的索引
       */
      async editSubGroupSuccess (curEditParentGroupIndex) {
        this.isShowEditSubGroupDialog = false;
        this.groupActionLoading = true;
        try {
          const r = await Promise.all([
            this.fetchAllActionList(),
            this.$store.dispatch('access/getModeling', {
              id: this.modelingId,
              data: {
                type: 'action_groups'
              }
            })
          ]);

          const groupList = [];
          groupList.splice(0, 0, ...this.groupList);

          const res = r[1] || {};
          const newGroupList = res.data || [];
          newGroupList.forEach((group, index) => {
            if (index === curEditParentGroupIndex) {
              group.expanded = groupList[index].expanded;
              this.$set(groupList, index, group);
            }
          });
          this.groupList.splice(0, this.groupList.length, ...groupList);

          this.refreshNoGroupAction();
        } catch (e) {
          console.error(e);
        } finally {
          this.groupActionLoading = false;
        }
      },

      /**
       * editSubGroupHide
       */
      editSubGroupHide () {
        this.isShowEditSubGroupDialog = false;
      },

      /**
       * delGroup
       */
      delGroup (item, index) {
        const directive = {
          name: 'bkTooltips',
          content: item.name,
          placement: 'right'
        };
        const me = this;
        me.$bkInfo({
          title: this.$t(`m.access['确认删除操作分组？']`),
          confirmLoading: true,
          subHeader: (
                        <div class="del-group-warn-info">
                            <p>
                                <span title={ item.name } v-bk-tooltips={ directive }>{ item.name }</span>
                            </p>
                        </div>
                    ),
          confirmFn: async () => {
            try {
              const groupList = [];
              groupList.splice(0, 0, ...this.groupList);
              groupList.splice(index, 1);

              this.groupActionLoading = true;

              await this.$store.dispatch('access/updateModeling', {
                id: this.modelingId,
                data: {
                  type: 'action_groups',
                  data: groupList
                }
              });

              this.groupList.splice(0, this.groupList.length, ...groupList);

              await Promise.all([
                this.fetchAllActionList(),
                this.fetchGroupList()
              ]);
              this.refreshNoGroupAction();
              this.groupActionLoading = false;

              me.messageSuccess(me.$t(`m.access['删除操作分组成功']`), 1000);
              return true;
            } catch (e) {
              console.error(e);
              me.messageAdvancedError(e);
              return false;
            }
          }
        });
      },

      /**
       * delSubGroup
       */
      delSubGroup (group, index, subGroup, subGroupIndex) {
        const directive = {
          name: 'bkTooltips',
          content: subGroup.name,
          placement: 'right'
        };
        const me = this;
        me.$bkInfo({
          title: this.$t(`m.access['确认删除子分组？']`),
          confirmLoading: true,
          subHeader: (
                        <div class="del-group-warn-info">
                            <p>
                                <span title={ subGroup.name } v-bk-tooltips={ directive }>{ subGroup.name }</span>
                            </p>
                        </div>
                    ),
          confirmFn: async () => {
            try {
              const groupList = [];
              groupList.splice(0, 0, ...this.groupList);

              const subGroups = [];
              subGroups.splice(0, 0, ...(group.sub_groups || []));
              subGroups.splice(subGroupIndex, 1);

              group.sub_groups.splice(0, group.sub_groups.length, ...subGroups);

              this.$set(groupList, index, group);

              this.groupActionLoading = true;

              await this.$store.dispatch('access/updateModeling', {
                id: this.modelingId,
                data: {
                  type: 'action_groups',
                  data: groupList
                }
              });

              this.groupList.splice(0, this.groupList.length, ...groupList);

              await Promise.all([
                this.fetchAllActionList(),
                this.fetchGroupList()
              ]);
              this.refreshNoGroupAction();
              this.groupActionLoading = false;

              me.messageSuccess(me.$t(`m.access['删除操作子分组成功']`), 1000);
              return true;
            } catch (e) {
              console.error(e);
              me.messageAdvancedError(e);
              return false;
            }
          }
        });
      },

      /**
       * showAddCommon
       */
      showAddCommon () {
        this.isShowAddCommonDialog = true;
      },

      /**
       * addCommonSuccess
       */
      async addCommonSuccess () {
        this.isShowAddCommonDialog = false;
        this.commonActionLoading = true;
        try {
          await Promise.all([
            this.fetchAllActionList(),
            this.fetchCommonList()
          ]);
        } catch (e) {
          console.error(e);
        } finally {
          this.commonActionLoading = false;
        }
      },

      /**
       * addCommonHide
       */
      addCommonHide () {
        this.isShowAddCommonDialog = false;
      },

      /**
       * showEditCommon
       */
      showEditCommon (item, index) {
        this.isShowEditCommonDialog = true;
        this.curEditCommon = item;
        this.curEditCommonIndex = index;
      },

      /**
       * editCommonAfterLeave
       */
      editCommonAfterLeave () {
        this.curEditCommon = null;
        this.curEditCommonIndex = -1;
      },

      /**
       * editCommonSuccess
       */
      async editCommonSuccess () {
        this.isShowEditCommonDialog = false;
        this.commonActionLoading = true;
        try {
          await Promise.all([
            this.fetchAllActionList(),
            this.fetchCommonList()
          ]);
        } catch (e) {
          console.error(e);
        } finally {
          this.commonActionLoading = false;
        }
      },

      /**
       * editCommonHide
       */
      editCommonHide () {
        this.isShowEditCommonDialog = false;
      },

      /**
       * delCommon
       */
      delCommon (item, index) {
        const directive = {
          name: 'bkTooltips',
          content: item.name,
          placement: 'right'
        };
        const me = this;
        me.$bkInfo({
          title: this.$t(`m.access['确认删除常用操作？']`),
          confirmLoading: true,
          subHeader: (
                        <div class="del-group-warn-info">
                            <p>
                                <span title={ item.name } v-bk-tooltips={ directive }>{ item.name }</span>
                            </p>
                        </div>
                    ),
          confirmFn: async () => {
            try {
              const commonList = [];
              commonList.splice(0, 0, ...this.commonList);
              commonList.splice(index, 1);

              this.commonActionLoading = true;

              await this.$store.dispatch('access/updateModeling', {
                id: this.modelingId,
                data: {
                  type: 'common_actions',
                  data: commonList
                }
              });

              await Promise.all([
                this.fetchAllActionList(),
                this.fetchCommonList()
              ]);
              this.refreshNoGroupAction();
              this.commonActionLoading = false;

              me.messageSuccess(me.$t(`m.access['删除常用操作成功']`), 1000);
              return true;
            } catch (e) {
              console.error(e);
              me.messageAdvancedError(e);
              return false;
            }
          }
        });
      },
      // stepChanged (index) {
      //     alert(`当前步骤index：${index}`)
      //     let routeName = ''
      //     if (index === 1) {
      //         routeName = 'systemAccessAccess'
      //     } else if (index === 2) {
      //         routeName = 'systemAccessRegistry'
      //     } else if (index === 3) {
      //         routeName = 'systemAccessOptimize'
      //     } else if (index === 4) {
      //         routeName = 'systemAccessComplete'
      //     }
      //     this.$router.push({
      //         name: routeName,
      //         params: this.$route.params
      //     })
      // },
      handleSubmit (routerName) {
        this.$router.push({
          name: routerName,
          params: {
            id: this.modelingId
          }
        });
      },

      /**
       * handlePrev
       */
      handlePrev () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          this.$router.push({
            name: 'systemAccessRegistry',
            params: this.$route.params
          });
        }, _ => _);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    @import './index.css';
</style>

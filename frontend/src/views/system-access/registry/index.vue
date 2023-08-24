<template>
  <!-- eslint-disable max-len -->
  <div class="iam-system-access-registry-wrapper">
    <div class="inner">
      <bk-steps class="system-access-step" ref="systemAccessStep" direction="vertical"
        :steps="controllableSteps.steps"
        :controllable="controllableSteps.controllable"
        :cur-step.sync="controllableSteps.curStep"
        :before-change="beforeStepChanged"
        @step-changed="stepChanged">
      </bk-steps>
      <smart-action class="content-wrapper">
        <template v-if="actionList.length">
          <div class="registry-action-item" v-for="(item, index) in actionList" :key="index">
            <div class="header" @click="handleExpanded(item)"
              :style="{ position: item.isExpand ? 'absolute' : 'relative' }">
              <Icon bk class="expanded-icon" :type="item.isExpand ? 'down-shape' : 'right-shape'" />
              <label class="title">{{ item.title || $t(`m.access['注册操作']`) }}</label>
            </div>
            <template v-if="!item.title">
              <div id="container-pop">
                <pop-content
                  :title="$t(`m.access['什么是注册操作？']`)"
                  :desc="$t(`m.access['操作是接入系统要控制的某个场景功能，如 服务器重启、脚本执行、菜单查看等，一 个操作是最小的权限控制单元，操作应该是可枚举相对静态的，一个接入系统的操作 数量有可能随着系统功能模块的增加而增加，但一般不会随着时间的推移无限增长。']`)"
                  :image="operationImage"
                ></pop-content>
              </div>
              <Icon class="icon-info-regis" type="info-new" v-bk-tooltips="htmlConfig" />
            </template>
            <div class="content" v-if="item.isExpand">
              <div class="slot-content">
                <div style="min-height: 60px;" v-bkloading="{ isLoading: item.loading, opacity: 1 }">
                  <section :ref="`basicInfoContentRef${index}`">
                    <basic-info :ref="`basicInfoRef${index}`" :info-data="item"
                      @on-change="handleBasicInfoChange(...arguments, item, index)" />
                  </section>
                  <bk-button theme="primary" text :disabled="!item.isEdit"
                    :style="{
                      marginTop: '23px',
                      marginBottom: item.isExpandAdvanced ? '6px' : '26px'
                    }"
                    @click="item.isExpandAdvanced = !item.isExpandAdvanced">
                    {{ $t(`m.access['高级配置']`) }}
                    <Icon :type="item.isExpandAdvanced ? 'up-angle' : 'down-angle'"
                      class="expand-advanced-settings" />
                  </bk-button>
                  <template v-if="item.isExpandAdvanced">
                    <div class="label-info">
                      {{$t(`m.access['依赖资源']`)}}
                      <template>
                        <div id="container-pop">
                          <pop-content
                            :title="$t(`m.access['什么是资源类型？']`)"
                            :desc="$t(`m.access['资源类型是指操作所关联的对象，如服务器重启关联的对象是服务器、脚本编辑关联的 对象是脚本，服务器、脚本都是一种资源类型，一个操作可以不关联任何资源类型，也 可以关联一种或多种资源类型。']`)"
                            :image="resourceImage"
                          ></pop-content>
                        </div>
                        <Icon type="info-new" v-bk-tooltips="htmlConfig" />
                      </template>
                    </div>
                    <bk-table :data="item.related_resource_types" border
                      :cell-class-name="getCellClass">
                      <bk-table-column :resizable="false" min-width="250"
                        :label="$t(`m.access['资源类型']`)">
                        <template slot-scope="{ row }">
                          <iam-cascade
                            class="system-access-cascade"
                            :disabled="!item.isEdit"
                            v-model="row.resourceTypeCascadeValue"
                            :list="systemListResourceType"
                            :is-remote="true"
                            :remote-method="fetchResourceTypeListBySystem"
                            clearable
                            :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                            :placeholder="$t(`m.access['请选择资源类型']`)"
                            :empty-text="$t(`m.access['无匹配数据']`)"
                            @change="handleResourceTypeChange(row, ...arguments)">
                            <div slot="extension" class="system-access-cascade-extension"
                              style="cursor: pointer;" @click="showAddResourceType">
                              <i class="bk-icon icon-plus-circle"></i>
                              {{ $t(`m.access['新增资源类型']`) }}
                            </div>
                          </iam-cascade>
                        </template>
                      </bk-table-column>
                      <bk-table-column :resizable="false" min-width="450"
                        :label="$t(`m.access['资源实例选择方式']`)" :render-header="renderHeader">
                        <template slot-scope="{ row }">
                          <div class="related-instance-selections-wrapper">
                            <bk-checkbox :disabled="!item.isEdit"
                              :checked="row.selection_mode === 'instance' || row.selection_mode === 'all'"
                              style="margin-right: 20px; margin-top: 7px;"
                              @change="instanceSelectionCheckboxHandler('instance', row, ...arguments)">
                              {{$t(`m.access['通过拓扑选择']`)}}
                            </bk-checkbox>
                            <div class="related-instance-selections-cascade-wrapper">
                              <div style="position: relative;"
                                v-for="(isItem, isItemIndex) in row.related_instance_selections"
                                :key="isItemIndex">
                                <iam-cascade
                                  class="related-instance-selections-cascade"
                                  :disabled="!item.isEdit || (row.selection_mode !== 'instance' && row.selection_mode !== 'all')"
                                  v-model="isItem.instanceSelectionsCascadeValue"
                                  :list="systemListInstanceSelections"
                                  :is-remote="true"
                                  :remote-method="fetchInstanceSelectionsListBySystem"
                                  clearable
                                  :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                                  :placeholder="$t(`m.access['请选择实例视图']`)"
                                  :empty-text="$t(`m.access['无匹配数据']`)"
                                  @change="handleInstanceSelectionsChange(row, isItem, ...arguments)">
                                  <div slot="extension" class="system-access-cascade-extension"
                                    style="cursor: pointer;" @click="showAddInstanceSelection">
                                    <i class="bk-icon icon-plus-circle"></i>{{ $t(`m.access['新增实例视图']`) }}
                                  </div>
                                </iam-cascade>
                                <Icon type="add-hollow" class="add-icon" :class="!item.isEdit ? 'disabled' : ''" @click="addRelatedInstanceSelections(item, row)" />
                                <Icon type="reduce-hollow" class="reduce-icon" v-if="row.related_instance_selections.length > 1" :class="!item.isEdit ? 'disabled' : ''" @click="delRelatedInstanceSelections(item, row, isItemIndex)" />
                              </div>
                              <Icon type="close-fill" class="remove-icon" v-if="item.related_resource_types.length > 1" :class="!item.isEdit ? 'disabled' : ''" @click="delRelatedRelatedResource(item, isItemIndex, $event)" />
                            </div>
                          </div>
                          <div>
                            <bk-checkbox :disabled="!item.isEdit"
                              :checked="row.selection_mode === 'attribute' || row.selection_mode === 'all'"
                              @change="instanceSelectionCheckboxHandler('attribute', row, ...arguments)">
                              {{$t(`m.access['通过属性选择']`)}}
                            </bk-checkbox>
                          </div>
                        </template>
                      </bk-table-column>
                    </bk-table>

                    <section class="add-related-resource-wrapper">
                      <bk-button theme="primary" text :disabled="!item.isEdit" @click="addRelatedResource(item)">
                        <Icon type="add-small" />
                        {{ $t(`m.access['新增依赖资源']`) }}
                      </bk-button>
                    </section>

                    <div class="label-info">{{$t(`m.access['依赖操作']`)}}</div>
                    <bk-select style="margin-top: 10px;margin-bottom: 30px;"
                      :disabled="!item.isEdit"
                      searchable
                      multiple
                      display-tag
                      v-model="item.related_actions">
                      <bk-option v-for="option in relatedActionList"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                      </bk-option>
                    </bk-select>
                  </template>
                </div>
              </div>
            </div>
            <div v-if="item.isExpand" class="btn-wrapper">
              <template v-if="!item.isEdit">
                <bk-button size="small" @click="item.isEdit = true">
                  {{ $t(`m.common['编辑']`) }}
                </bk-button>
                <bk-button size="small" theme="danger" outline :disabled="item.loading"
                  @click.stop.prevent="delAction(item, index)">{{ $t(`m.common['删除']`) }}</bk-button>
              </template>
              <template v-else>
                <bk-button size="small" :disabled="item.loading" theme="primary"
                  @click.stop.prevent="saveAction(item, index)">{{ $t(`m.common['保存']`) }}</bk-button>
                <bk-button size="small" :disabled="item.loading"
                  @click.stop.prevent="cancelEdit(index)">{{ $t(`m.common['取消']`) }}</bk-button>
              </template>
            </div>
          </div>
        </template>

        <render-action :title="$t(`m.access['新增操作']`)" style="margin-bottom: 20px;" @on-click="addAction"></render-action>

        <div slot="action">
          <bk-button theme="primary" type="button" :loading="submitLoading"
            @click="handleSubmit('systemAccessOptimize')">
            {{ $t(`m.common['下一步']`) }}
          </bk-button>
          <bk-button style="margin-left: 10px;" @click="handlePrev">{{ $t(`m.common['上一步']`) }}</bk-button>
        </div>
      </smart-action>
    </div>
    <resource-type-sideslider
      :is-show.sync="isShowAddResourceTypeSideslider"
      @on-refresh-system-list="fetchSystemList"
      @on-cancel="hideAddResourceType" />

    <instance-selection-sideslider
      :is-show.sync="isShowAddInstanceSelectionSideslider"
      @on-refresh-system-list="fetchSystemList"
      @on-cancel="hideAddResourceType" />
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';

  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import iamCascade from '@/components/cascade';
  import RenderAction from '../common/render-action';
  import BasicInfo from './basic-info';
  import PopContent from '../common/pop-content';

  import ResourceTypeSideslider from './resource-type-sideslider';
  import InstanceSelectionSideslider from './instance-selection-sideslider';

  import beforeStepChangedMixin from '../common/before-stepchange';

  import resourceImage from '@/images/resource-type.png';
  import operationImage from '@/images/operation.png';

  const getDefaultActionData = () => ({
    id: '',
    type: '',
    name: '',
    name_en: '',
    description: '',
    description_en: '',
    related_resource_types: [
      {
        resourceTypeCascadeValue: [],
        id: '',
        system_id: '',
        selection_mode: '',
        related_instance_selections: [
          {
            instanceSelectionsCascadeValue: [],
            id: '',
            system_id: ''
          }
        ]
      }
    ],
    related_actions: [],
    isEdit: true,
    isExpand: true,
    isExpandAdvanced: false,
    loading: false,
    // 添加了还未保存的
    isNewAdd: true,
    title: ''
  });

  export default {
    name: '',
    components: {
      BasicInfo,
      RenderAction,
      iamCascade,
      ResourceTypeSideslider,
      InstanceSelectionSideslider,
      PopContent
    },
    mixins: [beforeStepChangedMixin],
    data () {
      return {
        submitLoading: false,

        controllableSteps: {
          controllable: true,
          steps: [
            { title: this.$t(`m.access['注册系统']`), icon: 1 },
            { title: this.$t(`m.access['注册操作']`), icon: 2 },
            { title: this.$t(`m.access['体验优化']`), icon: 3 },
            { title: this.$t(`m.access['完成']`), icon: 4 }
          ],
          curStep: 2
        },
        isExpandAdvanced: false,
        // modelingSystemData: null,
        actionList: [],
        actionListBackup: [],
        isShowAddResourceTypeSideslider: false,
        isShowAddInstanceSelectionSideslider: false,
        systemListResourceType: [],
        systemListInstanceSelections: [],
        relatedActionList: [],
        htmlConfig: {
          allowHtml: true,
          width: 520,
          trigger: 'click',
          theme: 'light',
          content: '#container-pop',
          placement: 'right-start'
        },
        resourceImage,
        operationImage
      };
    },
    computed: {
            ...mapGetters(['user']),
            modelingId () {
                return this.$route.params.id;
            }
    },
    watch: {
      actionList (v) {
        const relatedActionList = v.filter(item => !item.isNewAdd).map(item => {
          return {
            id: item.id, name: item.name
          };
        });

        this.relatedActionList.splice(0, this.relatedActionList.length, ...relatedActionList);
      }
    },
    mounted () {
      const stepNode = this.$refs.systemAccessStep.$el;
      if (stepNode) {
        const children = Array.from(stepNode.querySelectorAll('.bk-step') || []);
        children.forEach(child => {
          child.classList.remove('current');
        });
        children[1].classList.add('current');
      }
    },
    methods: {
      // this.$emit('change', newValue, oldValue, this.localTrueValue)
      instanceSelectionCheckboxHandler (idx, row, value, oldValue, localTrueValue) {
        // 当前点击的是 通过属性选择 多选框
        if (idx === 'attribute') {
          // 选中
          if (value) {
            // 通过拓扑选择 多选框已选中
            if (row.selection_mode === 'instance') {
              row.selection_mode = 'all';
            } else if (row.selection_mode === '') {
              row.selection_mode = 'attribute';
            } else {
              row.selection_mode = '';
            }
          } else {
            // 通过拓扑选择 多选框已选中
            if (row.selection_mode === 'all') {
              row.selection_mode = 'instance';
            } else {
              row.selection_mode = '';
            }
          }
        }
        // 当前点击的是 通过拓扑选择 多选框
        if (idx === 'instance') {
          // 选中
          if (value) {
            // 通过属性选择 多选框已选中
            if (row.selection_mode === 'attribute') {
              row.selection_mode = 'all';
            } else if (row.selection_mode === '') {
              row.selection_mode = 'instance';
            } else {
              row.selection_mode = '';
            }
          } else {
            // 通过拓扑选择 多选框已选中
            if (row.selection_mode === 'all') {
              row.selection_mode = 'attribute';
            } else {
              row.selection_mode = '';
            }
          }
        }
      },
      async fetchPageData () {
        await Promise.all([
          this.fetchSystemList('all'),
          // this.fetchModeling()
          this.fetchActionList()
        ]);
      },

      async fetchSystemList (type) {
        try {
          const res = await this.$store.dispatch('access/getSystemList', {
            id: this.modelingId
          });
          const systemListResourceType = [];
          const systemListInstanceSelections = [];
          const list = res.data || [];
          list.forEach(item => {
            const id = item[0];
            const sysResourceType = this.systemListResourceType.find(s => s.id === id);
            const sysInstanceSelections = this.systemListInstanceSelections.find(s => s.id === id);
            const obj = {
              id: item[0],
              name: item[1],
              // TODO: cascade/caspanel.vue 的 handleItemFn 使用。目的是不允许选中第一层节点中没有子层级的节点，暂时先这么实现
              parent: true
            };
            if (type === 'all' || type === 'resourceType') {
              if (sysResourceType && sysResourceType.children) {
                obj.children = sysResourceType.children;
              }
              systemListResourceType.push(obj);
            }
            if (type === 'all' || type === 'instanceSelection') {
              if (sysInstanceSelections && sysInstanceSelections.children) {
                obj.children = sysInstanceSelections.children;
              }
              systemListInstanceSelections.push(obj);
            }
          });
          if (type === 'all' || type === 'resourceType') {
            this.systemListResourceType.splice(
              0,
              this.systemListResourceType.length,
              ...systemListResourceType
            );
          }
          if (type === 'all' || type === 'instanceSelection') {
            this.systemListInstanceSelections = JSON.parse(JSON.stringify(systemListInstanceSelections));
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
        }
      },

      async fetchActionList () {
        try {
          const resModeling = await this.$store.dispatch('access/getModeling', {
            id: this.modelingId,
            data: {
              type: 'action'
            }
          });
          const actionList = [];
          actionList.splice(0, 0, ...(resModeling.data || []));

          const preloadResourceTypeListBySys = [];
          const preloadResourceTypeListBySysParams = [];

          const preloadInstanceSelectionsBySys = [];
          const preloadInstanceSelectionsBySysParams = [];

          if (!actionList.length) {
            actionList.push(getDefaultActionData());
          } else {
            actionList.forEach(item => {
              item.title = item.name;
              item.isEdit = false;
              item.isExpand = false;
              item.loading = false;
              item.isNewAdd = false;
              if (!item.related_resource_types || !item.related_resource_types.length) {
                item.isExpandAdvanced = false;
                item.related_resource_types = [
                  {
                    resourceTypeCascadeValue: [],
                    id: '',
                    system_id: '',
                    selection_mode: '',
                    related_instance_selections: [
                      {
                        instanceSelectionsCascadeValue: [],
                        id: '',
                        system_id: ''
                      }
                    ]
                  }
                ];
              } else {
                item.isExpandAdvanced = true;
                item.related_resource_types.forEach(c => {
                  if (!c.related_instance_selections) {
                    c.related_instance_selections = [
                      {
                        instanceSelectionsCascadeValue: [],
                        id: '',
                        system_id: ''
                      }
                    ];
                  } else {
                    c.related_instance_selections.forEach(is => {
                      is.instanceSelectionsCascadeValue = [is.system_id, is.id];
                      preloadInstanceSelectionsBySysParams.push(is.system_id);
                      preloadInstanceSelectionsBySys.push(this.$store.dispatch('access/getInstanceSelectionsListBySystem', {
                        id: this.modelingId,
                        data: {
                          system_id: is.system_id
                        }
                      }));
                    });
                  }

                  c.resourceTypeCascadeValue = [c.system_id, c.id];

                  // preloadResourceTypeListBySysParams 和 preloadResourceTypeListBySys 的顺序是一致的
                  preloadResourceTypeListBySysParams.push(c.system_id);
                  preloadResourceTypeListBySys.push(this.$store.dispatch('access/getResourceTypeListBySystem', {
                    id: this.modelingId,
                    data: {
                      system_id: c.system_id
                    }
                  }));
                });
              }
            });
            if (preloadResourceTypeListBySys.length) {
              const resArr = await Promise.all(preloadResourceTypeListBySys);
              resArr.forEach((res, index) => {
                const curSysData = this.systemListResourceType.find(
                  sys => sys.id === preloadResourceTypeListBySysParams[index]
                );
                if (curSysData) {
                  curSysData.children = [];
                  (res.data || []).forEach(d => {
                    curSysData.children.push({
                                            ...d,
                                            isLoading: false
                    });
                  });
                }
              });
            }
            if (preloadInstanceSelectionsBySys.length) {
              const resArr = await Promise.all(preloadInstanceSelectionsBySys);
              resArr.forEach((res, index) => {
                const curSysData = this.systemListInstanceSelections.find(
                  sys => sys.id === preloadInstanceSelectionsBySysParams[index]
                );
                const curSysDataIndex = this.systemListInstanceSelections.findIndex(
                  sys => sys.id === preloadInstanceSelectionsBySysParams[index]
                );
                if (curSysData) {
                  curSysData.children = [];
                  (res.data || []).forEach(d => {
                    curSysData.children.push({
                                            ...d,
                                            isLoading: false
                    });
                  });
                  this.$set(this.systemListInstanceSelections, curSysDataIndex, curSysData);
                }
              });
            }
          }
          this.actionList.splice(0, this.actionList.length, ...actionList);
          this.actionListBackup = JSON.parse(JSON.stringify(actionList));
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

      // async fetchModeling () {
      //     try {
      //         const res = await this.$store.dispatch('access/getModeling', { id: this.modelingId })
      //         const systemData = (res.data || {}).system
      //         this.modelingSystemData = Object.assign({}, systemData || {})
      //     } catch (e) {
      //         console.error(e)
      //         this.bkMessageInstance = this.$bkMessage({
      //             limit: 1,
      //             theme: 'error',
      //             message: e.message || e.data.msg || e.statusText
      //         })
      //     }
      // },

      renderHeader (h, data) {
        return <span class="related-instance-selections-header-cell">{ data.column.label }</span>;
      },

      handleResourceTypeChange (row, newValue, oldValue, selectList) {
        row.system_id = row.resourceTypeCascadeValue[0];
        // 只有一层的情况
        row.id = row.resourceTypeCascadeValue[1] || row.resourceTypeCascadeValue[0];
      },

      handleInstanceSelectionsChange (resourceTypeRow, instanceSelectionRow, newValue, oldValue, selectList) {
        instanceSelectionRow.system_id = instanceSelectionRow.instanceSelectionsCascadeValue[0];
        // 只有一层的情况
        instanceSelectionRow.id = instanceSelectionRow.instanceSelectionsCascadeValue[1]
          || instanceSelectionRow.instanceSelectionsCascadeValue[0];
      },

      /**
       * 显示添加资源类型侧边栏
       */
      showAddResourceType () {
        this.isShowAddResourceTypeSideslider = true;
      },

      /**
       * 隐藏添加资源类型侧边栏
       */
      hideAddResourceType () {
        this.isShowAddResourceTypeSideslider = false;
      },

      /**
       * 显示添加实例视图侧边栏
       */
      showAddInstanceSelection () {
        this.isShowAddInstanceSelectionSideslider = true;
      },

      /**
       * 隐藏添加实例视图侧边栏
       */
      hideAddInstanceSelection () {
        this.isShowAddInstanceSelectionSideslider = false;
      },

      /**
       * 新增操作
       */
      addAction () {
        const actionList = [];
        actionList.splice(0, 0, ...this.actionList);
        actionList.push(getDefaultActionData());
        this.actionList.splice(0, this.actionList.length, ...actionList);
        this.actionListBackup = JSON.parse(JSON.stringify(actionList));
      },

      /**
       * getCellClass
       */
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1) {
          return 'registry-action-table-cell-cls';
        }
        return '';
      },

      /**
       * delRelatedInstanceSelections
       */
      delRelatedInstanceSelections (curAction, row, index) {
        if (!curAction.isEdit) {
          return;
        }

        const relatedInstanceSelections = [];
        relatedInstanceSelections.splice(0, 0, ...row.related_instance_selections);
        relatedInstanceSelections.splice(index, 1);

        row.related_instance_selections = JSON.parse(JSON.stringify(relatedInstanceSelections));
      },

      /**
       * addRelatedInstanceSelections
       */
      addRelatedInstanceSelections (curAction, row) {
        if (!curAction.isEdit) {
          return;
        }
        row.related_instance_selections.push({ instanceSelectionsCascadeValue: [], id: '', system_id: '' });
      },

      /**
       * fetchResourceTypeListBySystem
       */
      async fetchResourceTypeListBySystem (sys, resolve) {
        if (sys.isLoading === false) {
          resolve(sys);
          return;
        }
        this.$set(sys, 'isLoading', true);
        try {
          const res = await this.$store.dispatch('access/getResourceTypeListBySystem', {
            id: this.modelingId,
            data: {
              system_id: sys.id
            }
          });
          const list = [];
          res.data.forEach(item => {
            list.push({
                            ...item,
                            isLoading: false
            });
          });
          sys.children = list;
          resolve(sys);

          const systemListResourceType = [];
          systemListResourceType.splice(0, 0, ...this.systemListResourceType);
          const curSys = systemListResourceType.find(item => item.id === sys.id);
          if (curSys) {
            curSys.children = list;
            this.systemListResourceType.splice(
              0,
              this.systemListResourceType.length,
              ...systemListResourceType
            );
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
        }
      },

      /**
       * fetchInstanceSelectionsListBySystem
       */
      async fetchInstanceSelectionsListBySystem (sys, resolve) {
        if (sys.isLoading === false) {
          resolve(sys);
          return;
        }
        this.$set(sys, 'isLoading', true);
        try {
          const res = await this.$store.dispatch('access/getInstanceSelectionsListBySystem', {
            id: this.modelingId,
            data: {
              system_id: sys.id
            }
          });
          const list = [];
          res.data.forEach(item => {
            list.push({
                            ...item,
                            isLoading: false
            });
          });
          sys.children = list;
          resolve(sys);

          const systemListInstanceSelections = [];
          systemListInstanceSelections.splice(0, 0, ...this.systemListInstanceSelections);
          const curSys = systemListInstanceSelections.find(item => item.id === sys.id);
          if (curSys) {
            curSys.children = list;
            this.systemListInstanceSelections.splice(
              0,
              this.systemListInstanceSelections.length,
              ...systemListInstanceSelections
            );
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
        }
      },

      /**
       * handleExpanded
       */
      handleExpanded (item) {
        item.isExpand = !item.isExpand;
      },

      /**
       * handleBasicInfoChange
       */
      handleBasicInfoChange (value, item, index) {
        window.changeDialog = true;
        item.id = value.id;
        item.name = value.name;
        item.name_en = value.name_en;
        item.type = value.type;
        item.description = value.description;
        item.description_en = value.description_en;
      },

      /**
       * addRelatedResource
       */
      addRelatedResource (item) {
        const relatedResourceTypes = [];
        relatedResourceTypes.splice(0, 0, ...item.related_resource_types);
        relatedResourceTypes.push({
          resourceTypeCascadeValue: [],
          id: '',
          system_id: '',
          selection_mode: '',
          related_instance_selections: [
            {
              instanceSelectionsCascadeValue: [],
              id: '',
              system_id: ''
            }
          ],
          instanceSelectionsCascadeValue: []
        });
        item.related_resource_types.splice(0, item.related_resource_types.length, ...relatedResourceTypes);
      },

      /**
       * delRelatedRelatedResource
       */
      delRelatedRelatedResource (item, isItemIndex, event) {
        if (!item.isEdit) {
          return;
        }
        isItemIndex = event.currentTarget.parentElement.parentElement.parentElement.parentElement.parentElement.getAttribute('data-table-row').split('-')[1];
        const relatedResourceTypes = [];
        relatedResourceTypes.splice(0, 0, ...item.related_resource_types);
        relatedResourceTypes.splice(isItemIndex, 1);
        item.related_resource_types = JSON.parse(JSON.stringify(relatedResourceTypes));
      },

      /**
       * saveAction
       */
      async saveAction (item, index) {
        const formComp = this.$refs[`basicInfoRef${index}`];
        if (formComp && formComp[0]) {
          try {
            await formComp[0].handleValidator();
          } catch (e) {
            this.scrollToLocation(this.$refs[`basicInfoContentRef${index}`][0]);
            return;
          }
                    
          // 依赖实例时才需要校验
          if (item.related_resource_types.filter(t => t.selection_mode && !t.id).length) {
            this.messageError(this.$t(`m.access['资源实例选择方式至少选择一个']`), 1000);
            return;
          }

          const instanceSelectionModeList = ['all', 'instance'];

          // 通过拓扑选择，但是没有选择实例视图的判断
          // 选择实例视图组件在清空时，数组还是有数据的，所以用 system_id 来判断
          const invalidLength = item.related_resource_types.filter(t =>
            (instanceSelectionModeList.indexOf(t.selection_mode) > -1)
            && (t.related_instance_selections.filter(is => !is.system_id).length)
          ).length;

          if (invalidLength) {
            this.messageError(this.$t(`m.access['通过拓扑选择时必须要选择实例视图']`), 1000);
            return;
          }

          const relatedResourceTypes = [];
          item.related_resource_types.forEach(t => {
            if (t.system_id && t.id) {
              const obj = {
                system_id: t.system_id,
                id: t.id,
                selection_mode: t.selection_mode
              };
              if (instanceSelectionModeList.indexOf(t.selection_mode) > -1) {
                if (t.related_instance_selections && t.related_instance_selections.length) {
                  obj.related_instance_selections = [];
                  t.related_instance_selections.forEach(is => {
                    obj.related_instance_selections.push({
                      system_id: is.system_id,
                      id: is.id
                    });
                  });
                }
              } else {
                t.related_instance_selections = [{
                  instanceSelectionsCascadeValue: [],
                  id: '',
                  system_id: ''
                }];
              }
              relatedResourceTypes.push(obj);
            }
          });

          try {
            item.loading = true;
            await this.$store.dispatch('access/updateModeling', {
              id: this.modelingId,
              data: {
                type: 'action',
                data: {
                  id: item.id,
                  type: item.type,
                  name: item.name,
                  name_en: item.name_en,
                  description: item.description,
                  description_en: item.description_en,
                  related_resource_types: relatedResourceTypes,
                  related_actions: item.related_actions || []
                }
              }
            });
            item.title = item.name;
            item.isEdit = false;
            item.isNewAdd = false;
            this.messageSuccess(this.$t(`m.access['保存操作成功']`), 1000);
          } catch (e) {
            console.error(e);
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText
            });
          } finally {
            item.loading = false;
          }
        }
      },

      /**
       * cancelEdit
       */
      cancelEdit (index) {
        const formComp = this.$refs[`basicInfoRef${index}`];
        if (formComp && formComp[0]) {
          formComp[0].resetError();
        }
        const curItem = this.actionList[index];
        // 如果是未保存过的，那么取消的时候直接删除
        if (curItem.isNewAdd) {
          const actionList = [];
          actionList.splice(0, 0, ...this.actionList);
          actionList.splice(index, 1);
          this.actionList.splice(0, this.actionList.length, ...actionList);

          this.actionListBackup = JSON.parse(JSON.stringify(actionList));
        } else {
          const originalExpanded = curItem.isExpand;
          const originalExpandedAdvanced = curItem.isExpandAdvanced;
          const originalItem = Object.assign({}, this.actionListBackup[index]);
          originalItem.isEdit = false;
          originalItem.isExpand = originalExpanded;
          originalItem.isExpandAdvanced = originalExpandedAdvanced;
          this.$set(this.actionList, index, originalItem);
        }
      },

      /**
       * delAction
       */
      async delAction (item, index) {
        const directive = {
          name: 'bkTooltips',
          content: item.name,
          placement: 'right'
        };
        const me = this;
        me.$bkInfo({
          title: this.$t(`m.access['确认删除下列操作？']`),
          confirmLoading: true,
          subHeader: (
                        <div class="add-resource-type-warn-info">
                            <p>
                                <span title={ item.name } v-bk-tooltips={ directive }>{ item.name }</span>
                            </p>
                        </div>
                    ),
          confirmFn: async () => {
            try {
              item.loading = true;
              await me.$store.dispatch('access/deleteModeling', {
                id: me.modelingId,
                data: {
                  id: item.id,
                  type: 'action'
                }
              });

              const actionList = [];
              actionList.splice(0, 0, ...me.actionList);
              actionList.splice(index, 1);
              me.actionList.splice(0, me.actionList.length, ...actionList);

              me.messageSuccess(me.$t(`m.access['删除操作成功']`), 1000);
              return true;
            } catch (e) {
              console.error(e);
              me.bkMessageInstance = me.$bkMessage({
                limit: 1,
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
              return false;
            } finally {
              item.loading = false;
              this.$router.push({
                name: 'systemAccessRegistry',
                params: {
                  id: this.modelingId
                }
              });
              this.$nextTick(() => {
                me.actionListBackup = JSON.parse(JSON.stringify(me.actionList));
              });
            }
          }
        });
      },

      /**
       * handleSubmit
       */
      async handleSubmit (routerName) {
        if (!this.actionList.length) {
          this.messageError(this.$t(`m.access['至少要注册一个操作']`), 1000);
          return;
        }

        const invalidItemList = this.actionList.filter(item => item.isEdit);
        if (invalidItemList.length) {
          this.$bkInfo({
            title: this.$t(`m.access['请先保存所有操作']`),
            subHeader: (
                            <div class="add-resource-type-warn-info">
                                {
                                    invalidItemList.map(invalidItem => {
                                        const directive = {
                                            name: 'bkTooltips',
                                            content: invalidItem.name,
                                            placement: 'right'
                                        };
                                        return (
                                            <p>
                                                <span title={ invalidItem.name } v-bk-tooltips={ directive }>
                                                    { invalidItem.name }
                                                </span>
                                            </p>
                                        );
                                    })
                                }
                            </div>
                        )
          });
          return;
        }

        this.$router.push({
          // name: 'systemAccessComplete',
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
            name: 'systemAccessAccess',
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

<template>
  <div class="group-perm-table-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
    <bk-table
      v-if="!isLoading"
      :data="tableList"
      :ext-cls="!isEdit ? 'is-detail-view' : ''"
      :col-border="true"
      :cell-style="{ background: '#ffffff' }"
      :cell-class-name="getCellClass"
    >
      <bk-table-column :label="$t(`m.common['所属系统']`)" :min-width="100">
        <template slot-scope="{ row }">
          <span>{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.actionsTemplate['添加来源']`)" :min-width="130" prop="source_type">
        <template slot-scope="{ row }">
          <div
            v-for="(temp, tempIndex) of row.templates"
            :key="tempIndex"
            :class="[
              'child-table-content',
              'add-source-content',
              { 'set-border': isSetBorder(temp, tempIndex, row) },
              { 'is-search-no-border': isSearchNoBorder(temp, tempIndex, row) }
            ]"
          >
            <!-- 只有资源类型数量为偶数时且添加来源索引前的数据没有多个资源类型的情况才需要设置偏移量居中 -->
            <div
              v-for="(action, actionIndex) in temp.tableData"
              :key="action.id"
              :class="[
                'add-source-content-item',
                { 'multiple-temp-item': row.templates.length > 1 },
                {
                  'set-translate': temp.tableData.length > 1
                    && formatResourceTypeTotal(temp) % 2 === 0
                    && (((formatSourceDistance(temp) === actionIndex && !formatHasMultipleResourceType(temp)
                      || temp.tableData.length % 2 === 0)))
                },
                {
                  'set-zero-count-translate': formatResourceTypeCount(action) > 1 && formatSourceDistance(temp) === 0
                }
              ]"
              :style="{
                'min-height': formatSourceHeight(action),
                'line-height': formatSourceHeight(action)
              }"
            >
              <div class="source-name" v-show="formatSourceDistance(temp) === actionIndex">
                <Icon type="action-temp" class="action-icon" />
                <span
                  class="single-hide name"
                  v-bk-tooltips="{
                    content: temp.name,
                    placements: ['right-start']
                  }"
                  :ref="`source_${temp.id}_${temp.name}`"
                >
                  {{ temp.name }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)" :min-width="160" prop="action_name">
        <template slot-scope="{ row }">
          <div
            v-for="(temp, tempIndex) of row.templates"
            :key="tempIndex"
            class="child-table-content"
          >
            <div
              v-for="action in temp.tableData"
              :key="action.id"
              :class="[
                'actions-name',
                { 'set-border': isSetBorder(temp, tempIndex, row) },
                { 'is-search-no-border': isSearchNoBorder(temp, tempIndex, row) }
              ]"
            >
              <div class="instance-select-content">
                <template v-if="action.resource_groups && action.resource_groups.length > 0">
                  <div v-for="group in action.resource_groups" :key="group.id">
                    <div
                      v-for="(related, relatedIndex) in group.related_resource_types"
                      :key="related.type"
                      :class="[
                        'related-resource-item',
                        { 'actions-multiple-resource-type': group.related_resource_types.length > 1 },
                        { 'is-show-action': isShowColumnActions(group, relatedIndex) }
                      ]"
                    >
                      <span
                        class="single-hide name"
                        v-bk-tooltips="{
                          content: action.name,
                          placements: ['right-start']
                        }"
                        :ref="`actionName_${action.id}`"
                      >
                        {{ action.name }}
                      </span>
                    </div>
                  </div>
                </template>
                <div v-else class="related-resource-item">
                  <span
                    class="single-hide name"
                    v-bk-tooltips="{
                      content: action.name,
                      placements: ['right-start']
                    }"
                    :ref="`actionName_${action.id}`"
                  >
                    {{ action.name }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.permApply['资源类型']`)" :min-width="130" prop="resource_type">
        <template slot-scope="{ row }">
          <div
            v-for="(temp, tempIndex) in row.templates"
            :key="tempIndex"
            class="child-table-content"
          >
            <div
              v-for="action of temp.tableData"
              :key="action.id"
              :class="[
                'resource-type-name',
                { 'set-border': isSetBorder(temp, tempIndex, row) },
                { 'is-search-no-border': isSearchNoBorder(temp, tempIndex, row) }
              ]"
            >
              <div class="instance-select-content">
                <template v-if="action.resource_groups && action.resource_groups.length > 0">
                  <div v-for="group in action.resource_groups" :key="group.id">
                    <div
                      v-for="(related, relatedIndex) in group.related_resource_types"
                      :key="related.type"
                      :class="[
                        'related-resource-item',
                        {
                          'multiple-related-resource-item': group.related_resource_types.length > 1
                            && relatedIndex !== group.related_resource_types.length - 1
                        }
                      ]"
                    >
                      <div
                        :class="[
                          {
                            'multiple-resource-type': group.related_resource_types.length > 1
                              && relatedIndex !== group.related_resource_types.length - 1
                          }
                        ]"
                      >
                        <span
                          class="single-hide resource-type-label"
                          v-bk-tooltips="{
                            content: related.name,
                            placements: ['right-start']
                          }"
                          :ref="`resourceType_${action.id}_${related.type}`"
                        >
                          {{ related.name }}
                        </span>
                      </div>
                    </div>
                  </div>
                </template>
                <div v-else class="no-column-data">{{ $t(`m.common['无资源类型']`) }}</div>
              </div>
            </div>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['资源实例']`)" :min-width="260" prop="resource_instance" fixed="right">
        <template slot-scope="{ row }">
          <div
            v-for="(temp, tempIndex) in row.templates"
            :key="tempIndex"
            class="child-table-content"
          >
            <div
              v-for="action in temp.tableData"
              :key="action.id"
              :class="[
                'flex-between',
                'resource-instance-name',
                { 'set-border': isSetBorder(temp, tempIndex, row) },
                { 'is-search-no-border': isSearchNoBorder(temp, tempIndex, row) }
              ]"
            >
              <div class="instance-select-content">
                <template v-if="action.resource_groups && action.resource_groups.length > 0">
                  <div v-for="(group, groupIndex) in action.resource_groups" :key="group.id">
                    <div
                      v-for="(related, relatedIndex) in group.related_resource_types"
                      :key="related.type"
                      :class="[
                        'related-resource-item',
                        {
                          'multiple-related-resource-item': group.related_resource_types.length > 1
                            && relatedIndex !== group.related_resource_types.length - 1
                        }
                      ]"
                    >
                      <div
                        :class="[
                          'flex-between',
                          {
                            'multiple-resource-type': group.related_resource_types.length > 1
                              && relatedIndex !== group.related_resource_types.length - 1
                          }
                        ]"
                      >
                        <div class="instance-label">
                          <span>{{ $t(`m.common['已选择']`) }}</span>
                          <span class="instance-count">{{ formatInstanceCount(related, group) || 0 }}</span>
                          <span>{{ $t(`m.actionsTemplate['个任务实例']`) }}</span>
                        </div>
                        <div class="instance-operate-icon">
                          <Icon
                            v-if="isShowView(action)"
                            v-bk-tooltips="{ content: $t(`m.common['详情']`) }"
                            type="detail"
                            class="view-icon"
                            @click.stop="handleViewResource(action, groupIndex, relatedIndex)"
                          />
                          <Icon
                            v-bk-tooltips="{ content: $t(`m.common['复制']`) }"
                            type="copy"
                            class="copy-icon"
                            @click.stop="handleCopyInstance(related, action)"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
                <div v-else class="no-column-data">{{ $t(`m.common['无需关联实例']`) }}</div>
              </div>
            </div>
          </div>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty />
      </template>
    </bk-table>

    <preview-resource-dialog
      :show="isShowPreviewDialog"
      :title="previewDialogTitle"
      :params="previewResourceParams"
      @on-after-leave="handlePreviewDialogClose"
    />
  
  </div>
</template>
  
<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep, uniqWith, isEqual } from 'lodash';
  import { bus } from '@/common/bus';
  import PreviewResourceDialog from '@/views/group/components/preview-resource-dialog';
  export default {
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    inject: {
      getPermTableWidth: { value: 'getPermTableWidth', default: null }
    },
    components: {
      PreviewResourceDialog
    },
    props: {
      isLoading: {
        type: Boolean
      },
      list: {
        type: Array,
        default: () => []
      },
      originalList: {
        type: Array,
        default: () => []
      },
      remoteAction: {
        type: Array,
        default: () => []
      },
      systemId: {
        type: String,
        default: ''
      },
      templateId: {
        type: [String, Number],
        default: ''
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
      isGroup: {
        type: Boolean,
        default: false
      },
      externalDelete: {
        type: Boolean,
        default: false
      },
      linearActionList: {
        type: Array,
        default: () => []
      },
      isSearch: {
        type: Boolean
      }
    },
    data () {
      return {
        disabled: false,
        isShowPreviewDialog: false,
        curIndex: -1,
        curResIndex: -1,
        curGroupIndex: -1,
        selectedIndex: 0,
        // 当前复制的数据形态: normal: 普通; aggregate: 聚合后
        curId: '',
        curCopyKey: '',
        curCopyMode: 'normal',
        curCopyDataId: '',
        previewDialogTitle: '',
        previewResourceParams: {},
        curCopyParams: {},
        tableList: [],
        previewData: [],
        curCopyData: ['none'],
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters(['user']),
      isSuperManager () {
        return this.user.role.type === 'super_manager';
      },
      sliderWidth () {
        return 960;
      },
      condition () {
        if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
            return [];
        }
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResIndex];
        if (!curData) {
            return [];
        }
        return cloneDeep(curData.condition);
      },
      originalCondition () {
        if (this.curIndex === -1
            || this.curResIndex === -1
            || this.curGroupIndex === -1
            || this.originalList.length < 1) {
            return [];
        }
        const curId = this.tableList[this.curIndex].id;
        const curType = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResIndex].type;
        if (!this.originalList.some(item => item.id === curId)) {
            return [];
        }
        const curResTypeData = this.originalList.find(item => item.id === curId);
        if (!curResTypeData.resource_groups[this.curGroupIndex]
            .related_resource_types.some(item => item.type === curType)) {
            return [];
        }
        const curData = (curResTypeData.resource_groups[this.curGroupIndex]
            .related_resource_types || []).find(item => item.type === curType);
        if (!curData) {
            return [];
        }
        return cloneDeep(curData.condition);
      },
      curDisabled () {
        if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
            return false;
        }
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResIndex];
        return curData.isDefaultLimit;
      },
      curFlag () {
        if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
            return 'add';
        }
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResIndex];
        return curData.flag;
      },
      curSelectionMode () {
        if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
            return 'all';
        }
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResIndex];
        return curData.selectionMode;
      },
      curSelectionCondition () {
        if (this.curIndex === -1 || this.isSuperManager) {
            return [];
        }
        const curSelectionCondition = this.tableList[this.curIndex].conditionIds;
        return curSelectionCondition;
      },
      isShowPreview () {
        if (this.curIndex === -1) {
            return false;
        }
        return this.tableList[this.curIndex].policy_id !== '';
      },
      isShowView () {
        return (payload) => {
          return !payload.isEmpty;
        };
      },
      isCreateMode () {
        return this.mode === 'create';
      },
      isShowColumnActions () {
        return (payload, index) => {
          return payload.related_resource_types
          && (Math.floor(payload.related_resource_types.length / 2)) === index
          && payload.related_resource_types.length > 1;
        };
      },
      isShowDeleteAction () {
        return ['detail'].includes(this.mode) && this.isCustom && this.type !== 'view' && !this.externalDelete;
      },
      isNoBorder () {
        return (payload) => {
          const curIndex = payload.findLastIndex((v) => v.tableData.length > 0 && v.tableData.length < 2);
          return curIndex > -1;
        };
      },
      isSetBorder () {
        return (temp, tempIndex, row) => {
          return !(tempIndex === row.templates.length - 1
          && this.isNoBorder(row.templates)) && temp.tableData.length > 0;
        };
      },
      isSearchNoBorder () {
        return (temp, tempIndex, row) => {
          return this.isSearch && row.custom_policy_count > 0 && row.template_count > 0
            && (row.templates.findLastIndex((v) => v.tableData.length > 0) === tempIndex);
        };
      },
      // 获取每列添加来源的资源类型总数
      formatResourceTypeTotal () {
        return (payload) => {
          let count = 0;
          if (payload.tableData && payload.tableData.length) {
            const resourceGroups = payload.tableData.map((v) => v.resource_groups).flat(Infinity);
            if (resourceGroups.length > 0) {
              count = resourceGroups.reduce((prev, curr) => {
                if (curr.related_resource_types) {
                  return prev + curr.related_resource_types.length;
                }
              }, 0);
              return count;
            }
            return Math.floor(payload.tableData.length / 2);
          }
        };
      },
      // 判断添加来源索引前是否存在多个资源类型
      formatHasMultipleResourceType () {
        return (payload) => {
          if (payload.tableData && payload.tableData.length) {
            const resourceGroups = payload.tableData.map((v) => v.resource_groups).flat(Infinity);
            if (resourceGroups.length > 0) {
              const curIndex = Math.floor(this.formatResourceTypeTotal(payload) / 2);
              // 判断当前位置的索引前面是否有多个资源类型的操作
              const hasMultipleResourceType = resourceGroups.filter((v, i) =>
                v.related_resource_types.length > 1 && i < curIndex);
              return hasMultipleResourceType.length > 0;
            }
            return false;
          }
        };
      },
      // 计算添加来源的位置
      formatSourceDistance () {
        return (payload) => {
          if (payload.tableData && payload.tableData.length) {
            const resourceGroups = payload.tableData.map((v) => v.resource_groups).flat(Infinity);
            if (resourceGroups.length > 0) {
              const curIndex = Math.floor(this.formatResourceTypeTotal(payload) / 2);
              const hasMultipleResourceType = resourceGroups.filter((v, i) =>
                v.related_resource_types.length > 1 && i < curIndex);
              return hasMultipleResourceType.length > 0 && curIndex - hasMultipleResourceType.length > -1
                ? curIndex - hasMultipleResourceType.length
                : curIndex;
            }
            return this.formatResourceTypeTotal(payload);
          }
        };
      },
      formatResourceTypeCount () {
        return (payload) => {
          let count = 0;
          if (payload.resource_groups && payload.resource_groups.length > 0) {
            const hasResourceType = payload.resource_groups.some((v) =>
              v.related_resource_types && v.related_resource_types.length > 0);
            if (hasResourceType) {
              count = payload.resource_groups[0].related_resource_types.length;
            }
            return count;
          }
          return count;
        };
      },
      // 处理一个操作下有多个资源类型的场景，所以高度需要动态计算，默认44px
      formatSourceHeight () {
        return (payload) => {
         return this.formatResourceTypeCount(payload) > 1 ? `${this.formatResourceTypeCount(payload) * 44}px` : `44px`;
        };
      },
      // 处理无限制和聚合后多个tab数据结构不兼容情况
      formatDisplayValue () {
        return (payload) => {
          const { isNoLimited, empty, value, aggregateResourceType, selectedIndex } = payload;
          if (value && aggregateResourceType[selectedIndex]) {
            let displayValue = aggregateResourceType[selectedIndex].displayValue;
            if (isNoLimited || empty) {
              displayValue = value;
            }
            return displayValue;
          }
        };
      },
      formatInstanceCount () {
        return (payload, related) => {
          let curPaths = [];
          // 暂时注释掉获取所有资源类型下实例总和的业务逻辑
          // if (related.related_resource_types && related.related_resource_types.length > 1) {
          //   const list = related.related_resource_types.map((v) => {
          //     if (v.condition.length) {
          //       const { instance, instances } = v.condition[0];
          //       const list = instance || instances;
          //       curPaths = list.reduce((prev, next) => {
          //         prev.push(
          //           ...next.path.map(v => {
          //             const paths = { ...v, ...next };
          //             delete paths.instance;
          //             delete paths.path;
          //             return paths[0];
          //           })
          //         );
          //         return prev;
          //       }, []);
          //       return curPaths.length;
          //     }
          //   });
          //   const count = list.reduce((prev, next) => prev + next, 0);
          //   return count;
          // } else {
          //   if (payload.condition.length) {
          //     const { instance, instances } = payload.condition[0];
          //     const list = instance || instances;
          //     curPaths = list.reduce((prev, next) => {
          //       prev.push(
          //         ...next.path.map(v => {
          //           const paths = { ...v, ...next };
          //           delete paths.instance;
          //           delete paths.path;
          //           return paths[0];
          //         })
          //       );
          //       return prev;
          //     }, []);
          //     return curPaths.length;
          //   }
          // }
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
        };
      }
    },
    watch: {
      list: {
        handler (value) {
          this.tableList = uniqWith(value, isEqual);
        },
        immediate: true
      },
      systemId: {
        handler (value) {
          if (value) {
            this.curCopyMode = 'normal';
            this.curCopyData = ['none'];
            this.curIndex = -1;
            this.curResIndex = -1;
            this.curGroupIndex = -1;
          }
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
      formatFormItemWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
      },

      handleViewResource (payload, relatedIndex, typesIndex) {
        this.curId = payload.id;
        const params = [];
        const sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, {
          value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}`
        });
        const resourceGroup = payload.resource_groups[relatedIndex];
        if (resourceGroup.related_resource_types.length > 0) {
          resourceGroup.related_resource_types.forEach((item) => {
            const { name, type, condition } = item;
            params.push({
              name: type || '',
              label: this.$t(`m.info['tab操作实例']`, { value: name }),
              tabType: 'resource',
              tabActive: resourceGroup.related_resource_types[typesIndex].type || '',
              data: condition
            });
          });
        }
        this.previewData = cloneDeep(params);
        bus.$emit('on-drawer-side', { isShow: true, width: 640, title: sideSliderTitle, previewData: this.previewData });
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        const columnMap = {
          source_type: () => {
            return 'group-perm-table-source';
          },
          action_name: () => {
            return 'group-perm-table-action';
          },
          resource_type: () => {
            return 'group-perm-table-resource-type';
          },
          resource_instance: () => {
            return 'group-perm-table-resource-instance';
          }
        };
        if (columnMap[column.property]) {
          return columnMap[column.property]();
        }
        return '';
      },

      handleLimitChange () {
        window.changeDialog = true;
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex];
        curData.isChange = true;
      },

      handleResourcePreview () {
        window.changeDialog = true;
        // eslint-disable-next-line max-len
        const { system_id, type, name } = this.tableList[this.curIndex].resource_groups[this.curGroupIndex].related_resource_types[this.curResIndex];
        const condition = [];
        const conditionData = this.$refs.renderResourceRef.handleGetPreviewValue();
        conditionData.forEach(item => {
          const { id, attribute, instance } = item;
          condition.push({
            id,
            attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
            instances: instance ? instance.filter(item => item.path.length > 0) : []
          });
        });
        this.previewResourceParams = {
          id: this.templateId,
          action_id: this.tableList[this.curIndex].id,
          related_resource_type: {
            system_id,
            type,
            name,
            condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
          },
          reverse: true,
          groupId: this.groupId,
          policy_id: this.tableList[this.curIndex].policy_id,
          isTemplate: this.tableList[this.curIndex].isTemplate,
          resource_group_id: this.tableList[this.curIndex].resource_groups[this.curGroupIndex].id,
          isNotLimit: conditionData.length === 0
        };
        this.previewDialogTitle = this.$t(`m.info['操作侧边栏操作的资源实例差异对比']`, { value: `${this.$t(`m.common['【']`)}${this.tableList[this.curIndex].name}${this.$t(`m.common['】']`)}` });
        this.isShowPreviewDialog = true;
      },

      handlerOnView (payload, item, itemIndex) {
        const { system_id, type, name } = item;
        const condition = [];
        item.condition.forEach(item => {
          const { id, attribute, instance } = item;
          condition.push({
            id,
            attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
            instances: instance ? instance.filter(item => item.path.length > 0) : []
          });
        });
        this.previewResourceParams = {
          id: this.templateId,
          action_id: payload.id,
          related_resource_type: {
            system_id,
            type,
            name,
            condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
          },
          reverse: true,
          groupId: this.groupId,
          policy_id: payload.policy_id,
          resource_group_id: payload.resource_groups[this.curGroupIndex].id,
          isTemplate: payload.isTemplate
        };
        this.previewDialogTitle = this.$t(`m.info['操作侧边栏操作的资源实例差异对比']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        if (!this.previewResourceParams.id) {
          this.messageWarn(this.$t(`m.info['无资源ID，无法预览']`), 3000);
          return;
        }
        this.isShowPreviewDialog = true;
      },

      handleCopyInstance (sub, payload) {
        this.curCopyMode = 'normal';
        this.curCopyKey = `${sub.system_id}${sub.type}`;
        this.curCopyData = cloneDeep(sub.condition);
        this.curCopyParams = this.getBatchCopyParams(payload, sub);
        bus.$emit('on-group-perm-instance-copy', this.curCopyParams);
        this.messageSuccess(this.$t(`m.info['实例复制']`), 3000);
      },

      getBatchCopyParams (payload, content) {
        const actions = [];
        actions.unshift({
          system_id: payload.detail.system.id,
          id: payload.id
        });
        return {
          resource_type: {
            system_id: content.system_id,
            type: content.type,
            condition: content.condition.map(item => {
              return {
                id: item.id,
                instances: item.instance || [],
                attributes: item.attribute || []
              };
            })
          },
          actions
        };
      },
    
      handlePreviewDialogClose () {
        this.previewDialogTitle = '';
        this.previewResourceParams = {};
        this.isShowPreviewDialog = false;
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '../css/group-perm-table.css';
</style>

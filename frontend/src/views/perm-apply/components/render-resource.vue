<template>
  <div class="iam-slider-resource-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
    <div class="no-limit-wrapper" v-if="!isLoading">
      <div class="no-limit" :title="$t(`m.resource['无限制总文案']`)">
        <span>
          <Icon type="info-new" />
          <span class="text">{{ $t(`m.resource['无限制文案']`) }}</span>
          <bk-checkbox
            :ext-cls="'no-limit-checkbox'"
            v-model="notLimitValue"
            :disabled="disabled"
            @change="handleLimitChange"
          >
            {{ $t(`m.common['无限制']`) }}
          </bk-checkbox>
        </span>
      </div>
    </div>

    <template v-if="!isHide && !isLoading">
      <div v-for="(condition, index) in conditionData"
        :key="index"
        :class="conditionData.length === 1 ? 'is-one-resource-instance' : ''">
        <render-order-number v-if="conditionData.length > 1" :number="`${index + 1 }`" />
        <div class="resource-instance-wrapper" :class="conditionData.length > 1 ? 'set-padding' : ''">
          <!-- 实例 -->
          <render-resource-instance
            v-if="condition.hasOwnProperty('instance') || ['instance:paste'].includes(condition.selectionMode)"
            :expanded.sync="condition.instanceExpanded"
            :is-group="handleComputedIsGroup(condition)"
            :sub-title="condition.instanceTitle"
            :disabled="notLimitValue"
            mode="edit"
            :can-delete="condition.instanceCanDelete"
            :selection-mode="selectionMode"
            :need-order="conditionData.length > 1"
            @on-add="handleAdd(condition, index, 'instance')"
            @on-expand="handleExpanded(...arguments, condition)"
            @on-delete="handleDelete(condition, index, 'instance')"
            @on-mouseover="handleMouseenter(condition)"
            @on-mouseleave="handleMouseleave(condition)">
            <div class="iam-instance-wrapper">
              <div class="left-layout" :style="leftLayoutStyle">
                <choose-ip
                  :ref="`${index}TreeRef`"
                  :tree-value="condition.instance"
                  :selection-mode="selectionMode"
                  :select-list="selectList"
                  :select-value="selectValue"
                  :system-params="params"
                  :has-attribute="condition.hasOwnProperty('attribute')"
                  :has-status-bar="conditionData.length > 1 && index !== conditionData.length - 1"
                  :has-add-instance="!isHide && !isLoading && selectionMode !== 'instance'"
                  :is-show-edit-action="!handleComputedIsGroup(condition) && ['all'].includes(selectionMode)"
                  @on-tree-select="handlePathSelect(...arguments, index)" />
                <div class="drag-dotted-line" v-if="isDrag" :style="dottedLineStyle"></div>
                <div class="drag-line"
                  :style="dragStyle">
                  <img
                    class="drag-bar"
                    src="@/images/drag-icon.svg"
                    alt=""
                    :draggable="false"
                    @mousedown="handleDragMouseenter($event)">
                </div>
              </div>
              <div class="right-layout">
                <div class="flex-between right-layout-header">
                  <div class="right-layout-title">{{ $t(`m.common['结果预览']`) }}</div>
                  <div
                    :class="[
                      'clear-all'
                    ]"
                    @click.stop=""
                  >
                    <bk-dropdown-menu
                      ref="dropdownInstance"
                      :position-fixed="true"
                      align="left"
                      :disabled="formatClearDisabled(condition.instance)"
                    >
                      <template slot="dropdown-trigger">
                        <Icon bk type="more" />
                      </template>
                      <ul
                        slot="dropdown-content"
                        class="bk-dropdown-list"
                      >
                        <li>
                          <a @click.stop="handleConditionClearAll(condition.instance, index)">
                            {{ $t(`m.common['清除所有']`) }}
                          </a>
                        </li>
                      </ul>
                    </bk-dropdown-menu>
                  </div>
                </div>
                <div
                  v-if="condition.instance && condition.instance.length > 0"
                  :style="{ maxHeight: 'calc(100vh - 600px)' }"
                >
                  <instance-view
                    :select-list="selectList"
                    :select-value="selectValue"
                    :data="condition.instance"
                    @on-delete="handleInstanceDelete(...arguments, index)"
                    @on-clear="handleInstanceClearAll(...arguments, index)" />
                </div>
                <template v-else>
                  <div class="empty-wrapper">
                    <ExceptionEmpty
                      style="background: #fafbfd"
                    />
                  </div>
                </template>
              </div>
            </div>
          </render-resource-instance>
          <!-- 属性 -->
          <render-resource-instance
            v-if="condition.hasOwnProperty('attribute')"
            type="property"
            mode="edit"
            :can-delete="condition.attributeCanDelete"
            :selection-mode="selectionMode"
            :need-order="conditionData.length > 1"
            :sub-title="condition.attributeTitle"
            :disabled="notLimitValue"
            :expanded.sync="condition.attributeExpanded"
            :is-group="handleComputedIsGroup(condition)"
            :hovering="condition.isHovering"
            @on-add="handleAdd(condition, index, 'attribute')"
            @on-delete="handleDelete(condition, index, 'attribute')">
            <attribute
              :value="condition.attribute"
              :list="attributes"
              :params="attributeParams"
              ref="attributeRef"
              @on-change="handleAttrValueChange(...arguments, condition)" />
          </render-resource-instance>
        </div>
        <or-status-bar v-if="conditionData.length > 1 && index !== conditionData.length - 1" />
      </div>
    </template>
    <bk-button
      text
      size="small"
      v-if="!isHide && !isLoading && selectionMode !== 'instance'"
      :disabled="notLimitValue"
      style="margin: 5px 0 0 25px; padding-left: 0;"
      icon="plus-circle-shape"
      @click="handleAddInstance">
      {{ $t(`m.resource['添加一组实例']`) }}
    </bk-button>
    <!-- <p class="resource-error-tips" v-if="isEmptyResource">{{ $t(`m.resource['请至少选择一组实例']`) }}</p> -->
  </div>
</template>
<script>
    /* eslint-disable max-len */

  import _ from 'lodash';
  import renderResourceInstance from '@/components/render-resource';
  import renderOrderNumber from '@/components/render-resource/order-number';
  import OrStatusBar from '@/components/render-status/bar';
  import ChooseIp from '@/components/choose-ip';
  import InstanceView from '@/components/choose-ip/view';
  import Attribute from './attribute';
  import Instance from '@/model/instance';
  import Condition from '@/model/condition';

  const ATTRIBUTE_ITEM = {
    id: '',
    name: '',
    values: [
      {
        id: '',
        name: ''
      }
    ]
  };

  export default {
    name: '',
    // 这里用箭头函数会改变this
    provide: function () {
      return {
        getDragDynamicWidth: () => this.dragWidth
      };
    },
    inject: {
      getResourceSliderWidth: { value: 'getResourceSliderWidth', default: null }
    },
    components: {
      renderResourceInstance,
      renderOrderNumber,
      OrStatusBar,
      Attribute,
      ChooseIp,
      InstanceView
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      originalData: {
        type: Array,
        default: () => []
      },
      // 查询参数
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      flag: {
        type: String,
        default: ''
      },
      disabled: {
        type: Boolean,
        default: false
      },
      selectionMode: {
        type: String,
        default: 'all'
      }
    },
    data () {
      return {
        notLimitValue: false,
        hasSelectData: [],
        conditionData: [],
        selectList: [],
        selectValue: '',
        requestQueue: [],
        attributes: [],
        isHide: false,
        // isEmptyResource: false,
        dragWidth: this.getResourceSliderWidth ? this.getResourceSliderWidth() * 0.67 : 600,
        dragRealityWidth: this.getResourceSliderWidth ? this.getResourceSliderWidth() * 0.67 : 600,
        isDrag: false,
        hasSelectedCondition: []
      };
    },
    computed: {
      isLoading () {
        return this.requestQueue.length > 0;
      },
      attributeParams () {
        if (Object.keys(this.params).length > 0) {
          const { resource_type_system, resource_type_id } = this.params;
          return {
            system_id: resource_type_system,
            type: resource_type_id
          };
        }
        return {};
      },
      dragStyle () {
        return {
          'left': `${this.dragWidth}px`
        };
      },
      dottedLineStyle () {
        return {
          'left': `${this.dragRealityWidth}px`
        };
      },
      leftLayoutStyle () {
        const sliderWidth = this.getResourceSliderWidth ? this.getResourceSliderWidth() * 0.67 : 600;
        if (this.dragWidth >= sliderWidth) {
          return {
            'min-width': `${this.dragWidth}px`
          };
        }
        return {};
      },
      formatClearDisabled () {
        return (payload) => {
          let curPaths = [];
          if (payload.length) {
            curPaths = payload.reduce((prev, next) => {
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
            return curPaths.every(v => v.disabled);
          }
          return true;
        };
      },
      dynamicsSliderWidth () {
        return this.getResourceSliderWidth ? this.getResourceSliderWidth() * 0.67 : 600;
      }
    },
    watch: {
      params: {
        handler (value) {
          if (Object.keys(value).length > 0) {
            this.$emit('on-init', false);
            if (this.selectionMode === 'all') {
              this.requestQueue = ['instanceSelection', 'resourceAttr'];
              this.fetchInstanceSelection(value);
              this.fetchResourceAttrs();
            } else if (['instance', 'instance:paste'].includes(this.selectionMode)) {
              this.requestQueue = ['instanceSelection'];
              this.fetchInstanceSelection(value);
            } else {
              this.requestQueue = ['resourceAttr'];
              this.fetchResourceAttrs();
            }
          }
        },
        immediate: true
      },
      requestQueue (value) {
        if (value.length < 1) {
          this.$emit('on-init', true);
        }
      },
      data: {
        handler (val) {
          const len = val.length;
          // 此时是无权限状态
          if (len === 1 && val[0] === 'none') {
            this.conditionData = [new Condition({ selection_mode: this.selectionMode }, 'init', 'add')];
            this.conditionData[0].instanceExpanded = true;
            const selectionMode = this.conditionData[0].selectionMode;
            if (selectionMode !== 'all') {
              this.conditionData[0].instanceCanDelete = false;
            }
            // 备份已选数据，与最新数据做对比判断要不要展示离开确认框
            this.hasSelectedCondition = _.cloneDeep(val);
            return;
          }
          if (len > 0) {
            this.conditionData = val;
            const firstConditionData = this.conditionData[0];
            if (firstConditionData.instance && firstConditionData.instance.length > 0) {
              firstConditionData.instanceExpanded = true;
            }
            if (firstConditionData.attribute && firstConditionData.attribute.length > 0) {
              firstConditionData.attributeExpanded = true;
            }
            if (len === 1) {
              const selectionMode = this.conditionData[0].selectionMode;
              if (selectionMode !== 'all') {
                this.conditionData[0].instanceCanDelete = false;
              }
            }
            this.notLimitValue = false;
            this.isHide = false;
            // 备份已选数据，与最新数据做对比判断要不要展示离开确认框
            this.hasSelectedCondition = _.cloneDeep(this.conditionData);
          } else {
            this.notLimitValue = true;
            this.isHide = true;
            this.conditionData = [];
            // 备份已选数据，与最新数据做对比判断要不要展示离开确认框
            this.hasSelectedCondition = _.cloneDeep(this.conditionData);
          }
          console.log(this.conditionData, '当前实例数据');
        },
        deep: true,
        immediate: true
      },
      notLimitValue (value) {
        if (value) {
          this.conditionData.forEach(item => {
            item.isInstanceEmpty = false;
            item.isAttributeEmpty = false;
          });
        }
      }
    },
    methods: {
      handleDragMouseenter (e) {
        if (this.isDrag) {
          return;
        }
        this.isDrag = true;
        document.addEventListener('mousemove', this.handleDragMousemove);
        document.addEventListener('mouseup', this.handleDragMouseup);
      },

      handleDragMouseup (e) {
        // this.dragWidth = this.dragRealityWidth
        this.isDrag = false;
        document.removeEventListener('mousemove', this.handleDragMousemove);
        document.removeEventListener('mouseup', this.handleDragMouseup);
      },

      handleDragMousemove (e) {
        if (!this.isDrag) {
          return;
        }
        // 可拖拽范围
        const MIN_OFFSET_WIDTH = this.dynamicsSliderWidth;
        const minWidth = MIN_OFFSET_WIDTH;
        const maxWidth = MIN_OFFSET_WIDTH + 120;
        const sliderWidth = this.getResourceSliderWidth ? this.getResourceSliderWidth() : 960;
        const offsetX = e.clientX - (document.body.clientWidth - sliderWidth);
        if (offsetX < minWidth || offsetX >= maxWidth) {
          return;
        }
        this.dragRealityWidth = offsetX;
        this.dragWidth = offsetX;
      },

      async fetchInstanceSelection (params = {}) {
        try {
          const res = await this.$store.dispatch('permApply/getInstanceSelection', params);
          this.selectList = [...res.data];
          if (this.selectList.length > 0) {
            this.selectValue = res.data[0].id || '';
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      async fetchResourceAttrs () {
        try {
          const res = await this.$store.dispatch('permApply/getResourceAttrs', this.attributeParams);
          this.attributes = [...res.data.results];
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      handleLimitChange (newVal, oldVal) {
        window.changeAlert = true;
        if (!newVal) {
          this.isHide = false;
          const isInitializeData = this.originalData.length === 1 && this.originalData[0] === 'none';
          if (!isInitializeData && this.originalData.length > 0) {
            this.conditionData = _.cloneDeep(this.originalData);
            const firstConditionData = this.conditionData[0];
            if (firstConditionData.instance && firstConditionData.instance.length > 0) {
              firstConditionData.instanceExpanded = true;
            }
            if (firstConditionData.attribute && firstConditionData.attribute.length > 0) {
              firstConditionData.attributeExpanded = true;
            }
            return;
          }
          if (this.conditionData.length < 1) {
            this.conditionData.push(new Condition({ selection_mode: this.selectionMode }, 'init', 'add'));
            this.conditionData[0].instanceExpanded = true;
          }
        }

        if (this.flag === '') {
          this.$emit('on-limit-change');
        }
      },

      handleExpanded (payload, item) {
        // window.changeAlert = true;
        item.isHovering = !payload;
      },

      handleDelete (payload, index, key) {
        window.changeAlert = true;
        const currentData = _.cloneDeep(payload);
        if (key === 'instance') {
          delete currentData.instance;
        } else {
          delete currentData.attribute;
        }
        if (!currentData.instance && !currentData.attribute) {
          this.conditionData.splice(index, 1);
        } else {
          this.conditionData.splice(index, 1, currentData);
        }
      },

      handleAdd (condition, index, type) {
        window.changeAlert = true;
        const currentData = _.cloneDeep(condition);
        if (type === 'instance') {
          currentData.isAttributeEmpty = false;
          currentData.attribute = _.cloneDeep([ATTRIBUTE_ITEM]);
        } else {
          currentData.isInstanceEmpty = false;
          currentData.instance = [];
        }
        this.conditionData.splice(index, 1, currentData);
      },

      handleMouseenter (payload) {
        if (!payload.instanceExpanded) {
          payload.isHovering = true;
        }
      },

      handleMouseleave (payload) {
        payload.isHovering = false;
      },

      handleAddInstance () {
        // this.isEmptyResource = false
        window.changeAlert = true;
        this.conditionData.push(new Condition({ selection_mode: this.selectionMode }, 'init', 'add'));
        const lastConditionData = this.conditionData[this.conditionData.length - 1];
        if (lastConditionData.instance) {
          lastConditionData.instanceExpanded = true;
        } else {
          lastConditionData.attributeExpanded = true;
        }
      },

      handleComputedIsGroup (payload) {
        if (payload.hasOwnProperty('instance') && payload.hasOwnProperty('attribute')) {
          return true;
        }
        return false;
      },

      handleAttrValueChange (payload, condition) {
        window.changeAlert = true;
        condition.isAttributeEmpty = false;
        condition.attribute = payload;
      },

      handleGetPreviewValue () {
        if (this.notLimitValue) {
          return [];
        }
        const tempConditionData = _.cloneDeep(this.conditionData);
        tempConditionData.forEach(item => {
          if (!item.instance) {
            item.instance = [];
          }
          if (!item.attribute) {
            item.attribute = [];
          }
          if (item.instance.length > 0) {
            item.instance = item.instance.filter(ins => ins.path.length > 0);
          }
          if (item.attribute.length > 0) {
            item.attribute = item.attribute.filter(attr => attr.values.length > 0);
          }
        });
        return tempConditionData.map(({ id, instance, attribute }) => ({ id, instance, attribute }));
      },

      handleGetValue () {
        if (this.notLimitValue) {
          return {
            isEmpty: false,
            data: []
          };
        }
        if (this.conditionData.length < 1) {
          // this.isEmptyResource = true
          return {
            isEmpty: false,
            data: ['none']
          };
        }
        const tempConditionData = _.cloneDeep(this.conditionData);
        if (!tempConditionData.some(item => {
          return (item.instance && (item.instance.length > 0 && item.instance.some(instanceItem => instanceItem.path.length > 0)))
            || (item.attribute && (item.attribute.length > 0 && item.attribute.some(attr => attr.values.some(val => val.id !== ''))));
        })) {
          return {
            isEmpty: false,
            data: ['none']
          };
        }
        tempConditionData.forEach(item => {
          if (item.instance && item.instance.length > 0) {
            item.instance = item.instance.filter(ins => ins.path.length > 0);
          }
          if (item.attribute && item.attribute.length > 0) {
            item.attribute = item.attribute.filter(attr => attr.values.length > 0);
          }
        });
        return {
          isEmpty: false,
          data: tempConditionData
        };
      },

      handleConditionClearAll (payload, index) {
        payload.forEach((item, i) => {
          this.handleInstanceClearAll(item, i, index);
        });
        this.$nextTick(() => {
          this.$refs.dropdownInstance && this.$refs.dropdownInstance[0].hide();
        });
      },

      handleInstanceClearAll (payload, payloadIndex, index) {
        window.changeAlert = true;
        const { displayPath } = payload;
        displayPath.forEach((item, itemIndex) => {
          const curIds = item.parentChain.map(v => `${v.id}&${v.type}`);
          const curInstance = this.conditionData[index].instance;
          let id = item.id;
          let type = item.type;
          if (item.id === '*') {
            const data = curInstance[payloadIndex].path[itemIndex];
            const idIndex = data.findIndex(item => item.id === '*');
            id = data[idIndex - 1].id;
            type = data[idIndex - 1].type;
          }
          curIds.push(`${id}&${type}`);
          this.$refs[`${index}TreeRef`][0] && this.$refs[`${index}TreeRef`][0].handeCancelChecked(curIds.join('#'));
        });

        const curInstanceItem = this.conditionData[index].instance[payloadIndex];
        const indexList = [];
        curInstanceItem.path.forEach((v, index) => {
          if (v.some(_ => _.disabled)) {
            indexList.push(index);
          }
        });
        curInstanceItem.paths = curInstanceItem.paths.filter((v, index) => indexList.includes(index));
        curInstanceItem.path = curInstanceItem.path.filter(v => v.some(_ => _.disabled));

        if (curInstanceItem.path.length < 1) {
          this.conditionData[index].instance.splice(payloadIndex, 1);
        }
      },

      handleInstanceDelete (payload, payloadIndex, childIndex, index) {
        window.changeAlert = true;
        const curIds = payload.parentChain.map(v => `${v.id}&${v.type}`);
        const isCarryNextNoLimit = payload.id === '*';

        const curInstance = this.conditionData[index].instance;
        const curPath = curInstance[payloadIndex].path;
        const curPaths = curInstance[payloadIndex].paths;
        let id = payload.id;
        let type = payload.type;
        if (isCarryNextNoLimit) {
          const data = curPath[childIndex];
          const idIndex = data.findIndex(item => item.id === '*');
          id = data[idIndex - 1].id;
          type = data[idIndex - 1].type;
        }
        curPath.splice(childIndex, 1);
        curPaths.splice(childIndex, 1);
        if (curInstance.every(item => item.path.length < 1)) {
          const len = curInstance.length;
          curInstance.splice(0, len, ...[]);
        }

        curIds.push(`${id}&${type}`);

        if (isCarryNextNoLimit) {
          const existedNoCarryNoLimitData = curPath.find(item => {
            return curIds.join('#') === item.map(v => `${v.id}&${v.type}`).join('#');
          });
          if (existedNoCarryNoLimitData) {
            const isDisabled = existedNoCarryNoLimitData.some(v => v.disabled);
            if (isDisabled) {
              this.$refs[`${index}TreeRef`][0] && this.$refs[`${index}TreeRef`][0].handeSetChecked(curIds.join('#'));
            }
          } else {
            this.$refs[`${index}TreeRef`][0] && this.$refs[`${index}TreeRef`][0].handeCancelChecked(curIds.join('#'));
          }
        } else {
          const existedNoLimitData = curPath.find(item => {
            const tempArr = item.filter(_ => _.id !== '*');
            return curIds.join('#') === tempArr.map(v => `${v.id}&${v.type}`).join('#') && item[item.length - 1].id === '*';
          });
          if (existedNoLimitData) {
            const isDisabled = existedNoLimitData.some(v => v.disabled);
            if (isDisabled) {
              this.$refs[`${index}TreeRef`][0] && this.$refs[`${index}TreeRef`][0].handeSetChecked(curIds.join('#'));
            }
          } else {
            this.$refs[`${index}TreeRef`][0] && this.$refs[`${index}TreeRef`][0].handeCancelChecked(curIds.join('#'));
          }
        }
      },

      handleChain (payload, currentInstance, index, curAsync) {
        const typeChain = _.cloneDeep(payload).filter(item => item.id !== '*');
        // const curInstance = _.cloneDeep(currentInstance)
        // console.warn('typeChain: ')
        // console.warn(typeChain)
        // 当前类型链路：
        const curChain = typeChain.map(item => item.type);
        // console.warn('当前类型链路curChain: ')
        // console.warn(curChain)
        // 当前父级id链路
        const curIdChain = typeChain.map(item => item.id);
        // console.warn('当前父级id链路curIdChain: ')
        // console.warn(curIdChain)
        // 匹配的所有包含父级id的链路
        const allChain = [];
        // console.warn(currentInstance)
        currentInstance.forEach((item, itemIndex) => {
          const obj = {};
          obj.instanceIndex = itemIndex;
          item.path.forEach((pathItem, pathIndex) => {
            const isExistAny = pathItem.some(v => v.id === '*');
            if (!isExistAny) {
              if (pathItem.length === 1 && curAsync) {
                // const tempPathItem = _.cloneDeep(pathItem)
                // tempPathItem.unshift(...typeChain)
                const tempPathItem = _.cloneDeep(item.paths[pathIndex]);
                if (tempPathItem.map(sub => sub.id).filter(v => curIdChain.includes(v)).length > 0) {
                  obj.childChain = tempPathItem.map(chain => chain.type);
                  obj.childChainId = tempPathItem.map(chain => `${chain.id}&${chain.name}`);
                  obj.id = tempPathItem[tempPathItem.length - 1].id;
                  obj.pathIndex = pathIndex;
                  allChain.push(_.cloneDeep(obj));
                }
              }
              if (pathItem.length > 1) {
                if (pathItem.map(sub => sub.id).filter(v => curIdChain.includes(v)).length > 0) {
                  obj.childChain = pathItem.map(chain => chain.type);
                  obj.childChainId = pathItem.map(chain => `${chain.id}&${chain.name}`);
                  obj.id = pathItem[pathItem.length - 1].id;
                  obj.pathIndex = pathIndex;
                  allChain.push(_.cloneDeep(obj));
                }
              }
            } else {
              const templatePathItem = pathItem.filter(v => v.id !== '*');
              if (templatePathItem.length > 1) {
                if (templatePathItem.map(sub => sub.id).filter(v => curIdChain.includes(v)).length > 0) {
                  obj.childChain = templatePathItem.map(chain => chain.type);
                  obj.childChainId = templatePathItem.map(chain => `${chain.id}&${chain.name}`);
                  obj.id = templatePathItem[templatePathItem.length - 1].id;
                  obj.pathIndex = pathIndex;
                  allChain.push(_.cloneDeep(obj));
                }
              }
            }
          });
        });

        // 匹配的所有子级链路：
        const tempChain = allChain.filter(item => item.childChain.length > curChain.length);
        // console.warn('匹配的所有子级链路tempChain: ')
        // console.warn(tempChain)
        if (tempChain.length < 1) {
          return;
        }
        tempChain.forEach(item => {
          if (item.childChainId.join('').includes(curIdChain.join(''))) {
            const curPath = currentInstance[item.instanceIndex].path;
            // console.warn('curPath：')
            // console.warn(curPath)
            // const curPathIndex = curPath.findIndex(sub => item.id === sub[sub.length - 1].id)
            const curPathIndex = curPath.findIndex(sub => {
              if (sub.some(v => v.id === '*')) {
                return item.id === sub[sub.length - 2].id;
              }
              return item.id === sub[sub.length - 1].id;
            });
            const getFlag = () => {
              if (curIdChain.length === 1) {
                const arr = item.childChainId.slice(item.childChainId.length - 1);
                if (arr[0] === curIdChain[0]) {
                  return true;
                }
                return false;
              }
              return false;
            };
            // 禁用的不做移除
            if (curPathIndex > -1) {
              if (!curPath[curPathIndex].every(v => v.disabled) && !getFlag()) {
                curPath.splice(curPathIndex, 1);
              }
            }
          }
          // if (item.childChain.join('').includes(curChain.join(''))) {
          //   const curPath = currentInstance[item.instanceIndex].path;
          //   const curPathIndex = curPath.findIndex(sub => item.id === sub[sub.length - 1].id);
          //   curPath.splice(curPathIndex, 1);
          // }
        });
      },

      handlePathSelect (value, node, payload, resourceLen, index) {
        // console.log(value, node, payload, index, this.conditionData);
        window.changeAlert = true;
        const { type, path, paths } = payload[0];
        const tempPath = path[0];
        const curInstance = this.conditionData[index].instance;
        this.conditionData[index].isInstanceEmpty = false;
        if (value) {
          // console.warn('curInstance: ')
          // console.warn(curInstance)
          if (curInstance.length < 1) {
            curInstance.push(new Instance(payload[0]));
          } else {
            const selectInstanceItemIndex = curInstance.findIndex(item => item.type === type);
            // console.warn('selectInstanceItem: ')
            // console.warn(selectInstanceItem)
            // console.warn('path: ')
            // console.warn(path)
            if (selectInstanceItemIndex > -1) {
              const selectInstanceItem = _.cloneDeep(curInstance[selectInstanceItemIndex]);
              selectInstanceItem.path.push(...path);
              selectInstanceItem.paths.push(...paths);
              curInstance.splice(selectInstanceItemIndex, 1, selectInstanceItem);
            } else {
              curInstance.push(new Instance(payload[0]));
            }
            this.handleChain(tempPath, curInstance, index, node.async);
          }
        } else {
          let isDisabled = false;
          let curChildrenIds = [];
          const deleteIndex = -1;
          let deleteInstanceItem = curInstance.find(item => item.type === type);
          if (!deleteInstanceItem) {
            const hasSelectData = [];
            curInstance.forEach(item => {
              item.path.forEach(pathItem => {
                hasSelectData.push({
                  ids: pathItem.map(v => `${v.id}&${v.type}`),
                  idChain: pathItem.map(v => `${v.id}&${v.type}`).join('#'),
                  childTypes: pathItem.map(v => v.type),
                  disabled: pathItem.some(subItem => subItem.disabled)
                });
              });
            });
            this.hasSelectData = _.cloneDeep(hasSelectData);
            const hasData = this.hasSelectData.find((item) => item.childTypes.includes(type));
            if (hasData) {
              deleteInstanceItem = curInstance.find(item => hasData.childTypes.includes(item.type) && hasData.childTypes.includes(type));
            }
          }
          if (resourceLen) {
            for (let i = 0; i < resourceLen; i++) {
              // const noCarryNoLimitPath = payload[1]
          
              // const arr = path[0]
              // const tempPath = arr.filter(item => item.id !== '*')
          
              // const deleteIndex = deleteInstanceItem.path.findIndex(item => item.map(v => v.id).join('') === tempPath.map(v => v.id).join(''))
              const deleteIndex = deleteInstanceItem.path.findIndex(item => item.map(v => `${v.id}&${v.type}`).join('') === tempPath.map(v => `${v.id}&${v.type}`).join(''));
          
              // const curChildrenIds = node.children.map(item => item.id)
              curChildrenIds = node.children.map(item => `${item.id}&${item.type}`);
          
              // deleteInstanceItem.path.splice(deleteIndex, 1)
              if (deleteIndex > -1) {
                isDisabled = deleteInstanceItem.path[deleteIndex].some(_ => _.disabled);
                if (!isDisabled) {
                  deleteInstanceItem.path.splice(deleteIndex, 1);
                }
              }
            }
          } else {
            const deleteIndex = deleteInstanceItem.path.findIndex(item => item.map(v => `${v.id}&${v.type}`).join('') === tempPath.map(v => `${v.id}&${v.type}`).join(''));
            const deleteItem = deleteInstanceItem.path.filter(item => item.map(v => `${v.id}&${v.type}`).join('') === tempPath.map(v => `${v.id}&${v.type}`).join(''));
            curChildrenIds = node.children.map(item => `${item.id}&${item.type}`);
            if (deleteIndex > -1) {
              isDisabled = deleteInstanceItem.path[deleteIndex].some(_ => _.disabled);
              if (!isDisabled) {
                deleteInstanceItem.path.splice(deleteIndex, 1);
                // 处理半选之后再全选会造成有重叠的数据
                if (deleteItem.length > 1) {
                  deleteInstanceItem.path = deleteInstanceItem.path.filter((item) => !deleteItem.includes(item));
                }
              }
            }
          }

          if (payload[1]) {
            const noCarryNoLimitPath = payload[1].path[0];
            const deleteIndexTemp = deleteInstanceItem.path.findIndex(item => {
              return item.map(v => `${v.id}&${v.type}`).join('') === noCarryNoLimitPath.map(v => `${v.id}&${v.type}`).join('');
            });
            if (deleteIndexTemp > -1 && !deleteInstanceItem.path[deleteIndexTemp].some(_ => _.disabled)) {
              deleteInstanceItem.path.splice(deleteIndexTemp, 1);
              if (isDisabled) {
                const curIds = deleteInstanceItem.path[deleteIndex].filter(v => v.id !== '*').map(_ => `${_.id}&${_.type}`);
                this.$nextTick(() => {
                  this.$refs[`${index}TreeRef`][0] && this.$refs[`${index}TreeRef`][0].handeSetChecked(curIds.join('#'));
                });
              }
            }

            const otherTempPaths = payload[1].paths[0];
            const otherDeleteIndexTemp = deleteInstanceItem.paths.findIndex(item => item.map(v => `${v.id}&${v.type}`).join('') === otherTempPaths.map(v => `${v.id}&${v.type}`).join(''));
            deleteInstanceItem.paths.splice(otherDeleteIndexTemp, 1);
          }

          for (let i = 0; i < curInstance.length; i++) {
            const instanceItem = curInstance[i];
            if (instanceItem.path.length === 1 && instanceItem.path[0].length === 1) {
              // if (curChildrenIds.includes(instanceItem.path[0][0].id)) {
              //     curInstance.splice(i, 1)
              // }
              if (curChildrenIds.includes(`${instanceItem.path[0][0].id}&${instanceItem.path[0][0].type}`)) {
                curInstance.splice(i, 1);
                break;
              }
            }
            if (instanceItem.path < 1) {
              curInstance.splice(i, 1);
              break;
            }
          }

          const tempPaths = paths[0];
          const deleteIndexTemp = deleteInstanceItem.paths.findIndex(item => item.map(v => `${v.id}&${v.type}`).join('') === tempPaths.map(v => `${v.id}&${v.type}`).join(''));
          deleteInstanceItem.paths.splice(deleteIndexTemp, 1);
        }
      }
    }
  };
</script>

<style lang="postcss" scoped>
  @import '@/css/mixins/resource-instance-slider.css';
</style>

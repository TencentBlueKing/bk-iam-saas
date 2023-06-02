<template>
  <div class="iam-condition-detail-wrapper"
    :class="conditionData.length > 1 ? 'reset-top' : ''">
    <template v-if="conditionData.length > 0">
      <div v-for="(condition, conIndex) in conditionData" :key="condition">
        <render-order-number v-if="conditionData.length > 1" :number="`${conIndex + 1 }`" />
        <div class="group-checked-wrapper"
          v-if="conditionData.length > 1 && canEdit && condition.hasOwnProperty('instance')">
          <bk-checkbox
            :true-value="true"
            :false-value="false"
            v-model="condition.isGroupChecked"
            @change="handleGroupChange(...arguments, conIndex)">
            <!-- :indeterminate="condition.isGroupIndeterminate" -->
          </bk-checkbox>
        </div>
        <div class="resource-instance-wrapper">
          <render-resource-instance
            key="instance"
            v-if="condition.hasOwnProperty('instance')"
            :expanded.sync="condition.instanceExpanded"
            :is-group="computedIsGroup(condition)"
            :need-order="conditionData.length > 1"
            :sub-title="computedInstanceTitle(condition)"
            @on-expand="handleExpanded(...arguments, condition, conIndex)"
            @on-mouseover="handleMouseenter(condition)"
            @on-mouseleave="handleMouseleave(condition)">
            <instance-item
              v-for="(instanceItem, instanceIndex) in condition.instance"
              :key="instanceIndex"
              :ref="`instanceRef&${conIndex}`"
              :can-edit="canEdit"
              :title="`${instanceItem.name}(${instanceItem.path.length})`"
              :has-gap="instanceIndex > 0"
              :data="instanceItem.path"
              @on-selelct-all="handleSelectAll(...arguments, conIndex, instanceIndex)"
              @on-change="handleInstanceChange(...arguments, conIndex, instanceIndex)" />
          </render-resource-instance>
          <render-resource-instance
            key="property"
            v-if="condition.hasOwnProperty('attribute')"
            type="property"
            :sub-title="computedAttributeTitle(condition)"
            :expanded.sync="condition.attributeExpanded"
            :is-group="computedIsGroup(condition)"
            :need-order="conditionData.length > 1"
            :hovering="condition.isHovering"
            @on-expand="handleExpanded(...arguments, condition, conIndex)">
            <div style="padding-top: 10px;">
              <property-item :data="condition.attribute" />
            </div>
          </render-resource-instance>
        </div>
        <or-status-bar v-if="conditionData.length > 1 && conIndex !== conditionData.length - 1" />
      </div>
    </template>
    <div class="no-limit-wrapper" v-else>
      <div class="resource-empty-wrapper">{{ $t(`m.resource['资源实例无限制']`) }}</div>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import renderResourceInstance from './instance-edit.vue';
  import renderOrderNumber from './order-number.vue';
  import InstanceItem from './instance-item-edit.vue';
  import propertyItem from './property-item.vue';
  import OrStatusBar from '../render-status/bar.vue';

  export default {
    name: '',
    components: {
      renderResourceInstance,
      renderOrderNumber,
      InstanceItem,
      propertyItem,
      OrStatusBar
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      canEdit: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        conditionData: []
      };
    },
    watch: {
      data: {
        handler (value) {
          const list = _.cloneDeep(value);
          if (list.length > 0) {
            if (list[0] && list[0].hasOwnProperty('instance')) {
              list[0].instanceExpanded = true;
            }
            if (list[0] && list[0].hasOwnProperty('attribute')) {
              list[0].attributeExpanded = true;
            }
          }
          list.forEach(item => {
            let count = 0
            ;(item.instance || []).forEach(ins => {
              count = count + ins.path.length;
            });
            item.count = count;
            item.selectCount = 0;
            this.$set(item, 'isGroupChecked', false);
            // this.$set(item, 'isGroupIndeterminate', false)
          });
          this.conditionData = list;
        },
        immediate: true
      },
      canEdit (value) {
        if (!value) {
          this.conditionData.forEach((item, index) => {
            item.selectCount = 0;
            this.$set(item, 'isGroupChecked', false);
            const curInstanceRefs = this.$refs[`instanceRef&${index}`];
            curInstanceRefs.forEach($ref => {
              $ref && $ref.handleSetChecked(false);
            });
          });

          this.$emit('on-change');
        }
      }
    },
    methods: {
      handleGetValue () {
        const tempData = {
          ids: [],
          condition: [],
          iaAllDelete: false
        };
        this.conditionData.forEach((item, index) => {
          if (item.isGroupChecked) {
            tempData.ids.push(item.id);
          } else {
            const curInstanceRefs = this.$refs[`instanceRef&${index}`];
            const path = []
            ;(curInstanceRefs || []).forEach($ref => {
              const curData = $ref.handleGetValue().map(subItem => subItem.list);
              curData.forEach(pathItem => {
                const tempPath = pathItem.map(
                  ({ id, name, type, type_name, system_id }) => (
                    { id, name, type, type_name, system_id }
                  )
                );
                path.push(tempPath);
              });
            });

            const instances = []
            ;(item.instance || []).forEach(ins => {
              const { name, type } = ins;
              const curPath = path.filter(pathItem => {
                const reallyPath = pathItem.filter(v => v.id !== '*');
                return reallyPath[reallyPath.length - 1].type === type;
              });
              if (curPath.length > 0) {
                instances.push({
                  type,
                  name,
                  path: curPath
                });
              }
            });

            if (instances.length > 0) {
              tempData.condition.push({
                id: item.id,
                instances
              });
            }
          }
        });
        if (tempData.ids.length === this.conditionData.length) {
          tempData.iaAllDelete = true;
        }
        return tempData;
      },

      handleGroupChange (newVal, oldVal, val, payload) {
        const curInstanceRefs = this.$refs[`instanceRef&${payload}`];
        curInstanceRefs.forEach($ref => {
          $ref && $ref.handleSetChecked(newVal);
        });

        this.$emit('on-change');
      },

      handleSelectAll (checked, len, conIndex, instanceIndex) {
        const curCondition = this.conditionData[conIndex];

        if (checked) {
          curCondition.selectCount = curCondition.selectCount + len;
        } else {
          if (curCondition.selectCount > 0) {
            curCondition.selectCount = curCondition.selectCount - len;
          }
        }

        const flag = curCondition.selectCount === curCondition.count;
        this.conditionData[conIndex].isGroupChecked = flag;

        this.$emit('on-change');
      },

      handleInstanceChange (payload, conIndex, instanceIndex) {
        const curCondition = this.conditionData[conIndex];
        if (payload) {
          ++curCondition.selectCount;
        } else {
          if (curCondition.selectCount > 0) {
            --curCondition.selectCount;
          }
        }

        const flag = curCondition.selectCount === curCondition.count;
        this.conditionData[conIndex].isGroupChecked = flag;

        this.$emit('on-change');
        // if (flag) {
        //     this.conditionData[conIndex].isGroupChecked = true
        //     this.conditionData[conIndex].isGroupIndeterminate = false
        // } else {
        //     this.conditionData[conIndex].isGroupChecked = false
        //     if (payload.length > 0) {
        //         this.conditionData[conIndex].isGroupIndeterminate = true
        //     } else {
        //         this.conditionData[conIndex].isGroupIndeterminate = false
        //     }
        // }
      },

      computedIsGroup (payload) {
        if (payload.hasOwnProperty('instance') && payload.hasOwnProperty('attribute')) {
          return true;
        }
        return false;
      },

      computedInstanceTitle (payload) {
        if (payload.instance && payload.instance.length > 0) {
          const strList = [];
          payload.instance.forEach(item => {
            if (item.displayPath.length > 0) {
              const str = ` ${item.displayPath.length} ${this.$t(`m.common['个']`)}${item.name}${this.curLanguageIsCn ? '' : '(s)'}`;
              strList.push(str);
            }
          });
          return this.curLanguageIsCn ? `已选择 ${strList.join('、')}` : `${strList.join('、')} ${this.$t(`m.common['已选择']`)}`;
        }
        return this.$t(`m.resource['未选择任何拓扑实例']`);
      },

      computedAttributeTitle (payload) {
        if (payload.attribute && payload.attribute.length > 0) {
          let len = 0;
          payload.attribute.forEach(item => {
            if (item.id && item.values.some(val => val.id)) {
              ++len;
            }
          });
          if (len > 0) {
            return this.curLanguageIsCn ? `已设置 ${len} ${this.$t(`m.resource['个属性条件']`)}` : `${len} ${this.$t(`m.resource['个属性条件']`)} has been set`;
          }
          return this.$t(`m.resource['未设置任何属性条件']`);
        }
        return this.$t(`m.resource['未设置任何属性条件']`);
      },

      handleExpanded (payload, item, index) {
        item.isHovering = !payload;
        if (payload.instance && payload.instance.length > 0) {
          this.$nextTick(() => {
            const curInstanceRef = this.$refs[`instanceRef&${index}`][0];
            curInstanceRef && curInstanceRef.handleSetChecked(item.isGroupChecked);
          });
        }
      },

      handleMouseenter (payload) {
        if (!payload.instanceExpanded) {
          payload.isHovering = true;
        }
      },

      handleMouseleave (payload) {
        payload.isHovering = false;
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-condition-detail-wrapper {
        position: relative;
        &.reset-top {
            position: relative;
            top: -20px;
        }
        .group-checked-wrapper {
            position: absolute;
            right: 8px;
        }
        .resource-instance-wrapper {
            /* padding: 0 20px; */
            padding: 0 30px;
        }
        .no-limit-wrapper {
            /* padding: 0 20px; */
            padding: 0 30px;
        }
        .resource-empty-wrapper {
            line-height: 40px;
            background: #fff;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            font-size: 12px;
            text-align: center;
        }
    }
</style>

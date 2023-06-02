<template>
  <div class="iam-condition-detail-wrapper"
    :class="conditionData.length > 1 ? 'reset-top' : ''">
    <template v-if="conditionData.length > 0">
      <div v-for="(condition, conIndex) in conditionData" :key="conIndex">
        <render-order-number v-if="conditionData.length > 1" :number="`${conIndex + 1 }`" />
        <div class="resource-instance-wrapper">
          <render-resource-instance
            v-if="condition.hasOwnProperty('instance')"
            :expanded.sync="condition.instanceExpanded"
            :is-group="computedIsGroup(condition)"
            :need-order="conditionData.length > 1"
            :sub-title="computedInstanceTitle(condition)"
            @on-expand="handleExpanded(...arguments, condition)"
            @on-mouseover="handleMouseenter(condition)"
            @on-mouseleave="handleMouseleave(condition)">
            <instance-item
              v-for="(instanceItem, instanceIndex) in condition.instance"
              :key="instanceIndex"
              :title="`${instanceItem.name}(${instanceItem.path.length})`"
              :has-gap="instanceIndex > 0"
              :data="instanceItem.displayPath" />
          </render-resource-instance>
          <render-resource-instance
            v-if="condition.hasOwnProperty('attribute')"
            type="property"
            :sub-title="computedAttributeTitle(condition)"
            :expanded.sync="condition.attributeExpanded"
            :is-group="computedIsGroup(condition)"
            :need-order="conditionData.length > 1"
            :hovering="condition.isHovering">
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
  import renderResourceInstance from './index.vue';
  import renderOrderNumber from './order-number.vue';
  import InstanceItem from './instance-item.vue';
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
          if (value.length > 0) {
            if (value[0] && value[0].hasOwnProperty('instance')) {
              value[0].instanceExpanded = true;
            }
            if (value[0] && value[0].hasOwnProperty('attribute')) {
              value[0].attributeExpanded = true;
            }
          }
          this.conditionData = value;
        },
        immediate: true
      }
    },
    methods: {
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
          return this.curLanguageIsCn ? `已选择 ${strList.join('、')}` : `${strList.join('、')} selected`;
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

      handleExpanded (payload, item) {
        item.isHovering = !payload;
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
        &.reset-top {
            position: relative;
            top: -20px;
        }
        .resource-instance-wrapper {
            padding: 0 20px;
        }
        .no-limit-wrapper {
            padding: 0 20px;
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

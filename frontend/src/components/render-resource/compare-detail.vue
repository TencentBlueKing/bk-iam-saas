<template>
  <div class="iam-resource-compare-wrapper">
    <template v-if="curCondition.length > 0">
      <s class="all-delete-item" v-if="isAllAdd">{{ $t(`m.common['无限制']`) }}</s>
      <!-- <div class="all-add-item" v-if="isAllDelete"> -->
      <div class="all-add-item" v-if="isNotLimit">
        <span class="add-tag"></span>
        {{ $t(`m.common['无限制']`) }}
      </div>
      <div v-for="(condition, conIndex) in curCondition" :key="conIndex">
        <render-order-number v-if="curCondition.length > 1" :number="`${conIndex + 1 }`" />
        <div class="resource-instance-wrapper">
          <render-resource-instance
            v-if="condition.hasOwnProperty('instance')"
            :expanded.sync="condition.instanceExpanded"
            :is-group="computedIsGroup(condition)"
            :need-order="curCondition.length > 1"
            :is-new="condition.isInstanceNew"
            :title="condition.instanceTitle"
            :sub-title="condition.instanceSubTitle"
            @on-expand="handleExpanded(...arguments, condition)"
            @on-mouseover="handleMouseenter(condition)"
            @on-mouseleave="handleMouseleave(condition)">
            <compare-item
              v-for="(instanceItem, instanceIndex) in condition.instance"
              :key="instanceIndex"
              :title="instanceItem.title"
              :has-gap="instanceIndex > 0"
              :data="instanceItem.displayPath" />
          </render-resource-instance>
          <render-resource-instance
            v-if="condition.hasOwnProperty('attribute')"
            type="property"
            :title="condition.attributeTitle"
            :is-new="condition.isAttributeNew"
            :sub-title="condition.attributeSubTitle"
            :expanded.sync="condition.attributeExpanded"
            :is-group="computedIsGroup(condition)"
            :need-order="curCondition.length > 1"
            :hovering="condition.isHovering">
            <compare-item
              v-for="(attrItem, attrIndex) in condition.attribute"
              :key="attrIndex"
              :title="attrItem.title"
              :has-gap="attrIndex > 0"
              :data="attrItem.values" />
          </render-resource-instance>
        </div>
        <or-status-bar v-if="curCondition.length > 1 && conIndex !== curCondition.length - 1" />
      </div>
    </template>
    <div class="no-limit-wrapper" v-else>
      <div class="resource-empty-wrapper">{{ $t(`m.resource['资源实例无限制']`) }}</div>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import renderResourceInstance from '@/components/render-resource';
  import renderOrderNumber from './order-number';
  import CompareItem from '@/components/render-resource/compare-item';
  import OrStatusBar from '@/components/render-status/bar';

  export default {
    name: '',
    components: {
      renderResourceInstance,
      renderOrderNumber,
      CompareItem,
      OrStatusBar
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      isNotLimit: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        curCondition: []
      };
    },
    computed: {
      isAllDelete () {
        return this.curCondition.every(item => item.status === 'delete');
      },
      isAllAdd () {
        return this.curCondition.every(item => item.status === 'add');
      }
    },
    watch: {
      data: {
        handler (value) {
          this.curCondition = _.cloneDeep(value);
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
    .iam-resource-compare-wrapper {
        position: relative;
        .all-delete-item {
            display: inline-block;
            padding-left: 24px;
            margin-bottom: 5px;
            font-size: 14px;
            color: #c4c6cc;
        }
        .all-add-item {
            display: inline-block;
            padding-left: 24px;
            margin-bottom: 5px;
            font-size: 14px;
            .add-tag {
                display: inline-block;
                position: relative;
                top: 8px;
                width: 5px;
                height: 5px;
                border-radius: 50%;
                border: 1px solid #10c178;
                background: #85dcb8;
                vertical-align: top;
            }
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

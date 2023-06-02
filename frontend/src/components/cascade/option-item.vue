<template>
  <li class="bk-option"
    :class="{
      'is-selected': selectedItem.id === item.id,
      'is-multiple': multiple,
      'is-disabled': item.disabled
    }">
    <div class="bk-option-content">
      <slot>
        <div class="bk-option-content-default" :title="item.name">
          <div class="bk-cascade-check" v-if="multiple">
            <bk-checkbox
              :value="item.isSelected"
              :disabled="item.disabled"
              :indeterminate="item.isIndeterminate"
              @change="handleCheckItem">
            </bk-checkbox>
          </div>
          <span class="bk-option-name" :class="{ 'bk-margin-left': multiple }">
            {{item.name}}
            <slot name="prepend" :node="item"></slot>
          </span>
        </div>
      </slot>
    </div>
    <template v-if="isRemote">
      <i class="bk-icon left-icon icon-loading bk-button-icon-loading bk-cascade-right" v-if="item.isLoading">
        <span class="loading"></span>
      </i>
      <!-- eslint-disable max-len -->
      <i class="bk-cascade-right bk-icon icon-angle-right" v-if="(item.children && item.children.length) || (item.isLoading === undefined && !item.disabled)"></i>
    </template>
    <template v-else>
      <i class="bk-cascade-right bk-icon icon-angle-right"
        v-if="item.children && item.children.length"></i>
    </template>
  </li>
</template>
<script>
  export default {
    name: 'iamCascadeOptionItem',
    props: {
      item: {
        type: Object,
        default: () => ({})
      },
      selectedItem: {
        type: Object,
        default: () => ({})
      },
      multiple: {
        type: Boolean,
        default: false
      },
      isRemote: {
        type: Boolean,
        default: false
      }
    },
    methods: {
      handleCheckItem () {
        this.$emit('handleCheckItem', this.item);
      }
    }
  };
</script>

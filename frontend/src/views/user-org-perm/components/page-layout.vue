<template>
  <div class="page-layout">
    <div :class="[
      'left-layout',
      { 'external-left-height': externalLeftLayoutHeight },
      { 'no-expand': !isExpand }
    ]">
      <slot />
    </div>
    <slot name="expand-icon" />
    <div :class="['right-layout', { 'external-right-height': externalRightLayoutHeight }]">
      <slot name="right" />
    </div>
  </div>
</template>

<script>
  export default {
    name: '',
    props: {
      externalLeftLayoutHeight: {
        type: Boolean,
        default: false
      },
      externalRightLayoutHeight: {
        type: Boolean,
        default: false
      },
      isExpand: {
        type: Boolean,
        default: true
      }
    }
  };
</script>

<style lang="postcss" scoped>
.page-layout {
  display: flex;
  padding: 0;
  .left-layout {
    flex: 0 0 240px;
    height: calc(100vh - 61px);
    background-color: #ffffff;
    overflow: hidden;
    &.no-expand {
      display: none;
    }
  }
  .right-layout {
    padding: 16px 16px 0 0;
    flex: 1 0 auto;
    width: calc(100% - 240px);
    height: calc(100vh - 210px);
    background-color: #f5f6fa;
    overflow-y: auto;
    &::-webkit-scrollbar {
      width: 4px;
      background-color: lighten(transparent, 80%);
    }
    &::-webkit-scrollbar-thumb {
      height: 5px;
      border-radius: 2px;
      background-color: #e6e9ea;
    }
  }

  .external-right-height {
    padding: 30px 30px 0;
    height: calc(100vh - 5px);
  }
}
</style>

<template>
  <div class="detail-item" :class="`design-layout-${layout}`">
    <div class="detail-label">
      <span>{{ label }}</span>
    </div>
    <div class="detail-content">
      <slot />
    </div>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      label: {
        type: String,
        default: ''
      },
      layout: {
        type: String,
        default: '' // horizontal, vertical
      }
    }
  };
</script>
<style lang='postcss' scoped>
    .detail-item {
        display: flex;
        align-items: flex-start;
        justify-content: flex-end;
        font-size: 14px;
        color: #313238;
        line-height: 34px;
        &.design-layout-horizontal {
            flex-direction: row !important;
        }
        &.design-layout-vertical {
            flex-direction: column !important;
            .detail-content{
                width: 100%;
            }
        }
    }
    .detail-label {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex: 0 0 auto;
        text-align: left;
        color: #63656e;
        word-break: keep-all;
        white-space: pre;
    }
    .detail-content {
        flex: 1;
        color: #63656e;
    }
</style>

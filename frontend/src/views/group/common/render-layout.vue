<template functional>
  <div class="iam-render-common-layout">
    <div class="left">
      <slot />
    </div>
    <div class="right">
      <slot name="right" />
    </div>
  </div>
</template>
<style lang="postcss" scoped>
    .iam-render-common-layout {
        display: flex;
        justify-content: flex-start;
        width: 100%;
        .left {
            flex: 0 0 50%;
        }
        .right {
            margin-left: 10px;
        }
    }
</style>

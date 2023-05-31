<template functional>
  <div class="iam-search-wrapper">
    <div class="left">
      <slot />
    </div>
    <div class="right">
      <slot name="right" />
    </div>
  </div>
</template>
<style lang="postcss">
    .iam-search-wrapper {
        position: relative;
        display: flex;
        justify-content: space-between;
        /* .left {
            display: flex;
            align-items: center;
        } */
    }
</style>

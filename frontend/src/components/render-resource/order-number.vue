<template functional>
  <div class="iam-resource-order-number-wrapper">
    <span class="number">{{ props.number || 0 }}</span>
  </div>
</template>
<style lang="postcss">
    .iam-resource-order-number-wrapper {
        line-height: 1px;
        border-bottom: 1px solid #dcdee5;
        margin-bottom: 18px;
        .number {
            display: inline-block;
            position: relative;
            top: 17px;
            width: 16px;
            height: 16px;
            font-size: 12px;
            text-align: center;
            line-height: 16px;
            color: #fff;
            background: #4f5d7b;
        }
    }
</style>

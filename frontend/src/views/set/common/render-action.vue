<template functional>
  <div class="iam-set-action-wrapper" @click="props.handleClick">
    <Icon type="add-small" />
    {{ props.title }}
  </div>
</template>
<style lang="postcss">
    .iam-set-action-wrapper {
        margin-top: -1px;
        width: 100%;
        line-height: 32px;
        border: 1px dashed #dcdee5;
        background: #fafbfd;
        font-size: 12px;
        text-align: center;
        cursor: pointer;
        &:hover {
            background: #f0f6ff;
            border-color: #a3c5fd;
            color: #3a84ff;
        }
        i {
            position: relative;
            left: 5px;
            top: 2px;
            font-size: 22px;
        }
    }
</style>

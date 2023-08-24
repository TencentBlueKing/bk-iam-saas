<template functional>
  <div :class="[
    'iam-render-tag',
    { add: props.status === 'add' },
    { checked: props.status === 'checked' || props.status === 'unchecked' },
    { checked: props.status === 'delete' }
  ]">
    <span
      :class="['status-dot', { add: props.status === 'add' }, { delete: props.status === 'delete' }]"
      v-if="props.status === 'add' || props.status === 'delete'">
    </span>
    <template v-if="props.status === 'add' || props.status === 'checked' || props.status === 'unchecked'">
      <span style="display: inline-block; color: #979ba5; vertical-align: middle;">{{ props.content }}</span>
    </template>
    <template v-else>
      <s style="display: inline-block; color: #c4c6cc; vertical-align: middle;">{{ props.content }}</s>
    </template>
  </div>
</template>
<style lang="postcss" scoped>
    .iam-render-tag {
        display: inline-block;
        padding: 0 8px;
        border-radius: 2px;
        font-size: 12px;
        &.add,
        &.checked {
            background: #f5f6fa;
        }
        &.delete {
            background: #f5f6fa;
        }
        .status-dot {
            display: inline-block;
            width: 5px;
            height: 5px;
            border-radius: 50%;
            vertical-align: middle;
            &.add {
                border: 1px solid #10c178;
                background: #85dcb8;
            }
            &.delete {
                border: 1px solid #ff9c01;
                background: #ffd695;
            }
        }
    }
</style>

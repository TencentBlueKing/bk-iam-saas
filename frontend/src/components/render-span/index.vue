<template functional>
  <!-- status: add 为新增 delete 为删除 unchanged 为未改变 -->
  <div class="iam-render-span" :title="props.content || ''">
    <span v-if="props.visible && ['add', 'delete'].includes(props.status)"
      :class="['span-flag', { 'add': props.status === 'add' }, { 'delete': props.status === 'delete' }]">
    </span>
    <template v-if="props.status === 'add' || props.status === 'unchanged'">
      <span style="display: inline-block; color: #63656e; vertical-align: middle;">{{ props.content }}</span>
    </template>
    <template v-else>
      <s style="display: inline-block; color: #c4c6cc; vertical-align: middle;">{{ props.content }}</s>
    </template>
  </div>
</template>
<style lang="postcss" scoped>
    .iam-render-span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        .span-flag {
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

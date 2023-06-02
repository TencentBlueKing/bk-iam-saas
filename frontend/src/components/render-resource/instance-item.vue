<template functional>
  <div :class="['iam-instance-content', { 'set-marging-top': props.hasGap }]">
    <p class="iam-instance-title">{{ props.title || '--' }}</p>
    <div class="iam-instance-item">
      <p v-for="(item, index) in props.data" :key="index" class="value" :title="`ID：${item.id}`">
        {{ item.display_name }}
      </p>
    </div>
  </div>
</template>
<style lang="postcss" scoped>
    .iam-instance-content {
        &.set-marging-top {
            margin-top: 15px;
        }
        .iam-instance-title {
            font-size: 12px;
            color: #63656e;
        }
        .iam-instance-item {
            margin-top: 10px;
            padding: 13px 16px;
            max-height: 186px;
            overflow-y: auto;
            background: #f7f9fb;
            font-size: 12px;
            color: #63656e;
            .value {
                max-width: 400px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
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
    }
</style>

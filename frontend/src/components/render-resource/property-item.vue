<template functional>
  <div class="iam-property-content">
    <div
      v-for="(item, index) in props.data" :key="index"
      :class="['iam-property-item', { 'set-margin-bottom': index !== props.data.length - 1 }]">
      <label class="iam-property-label">{{ item.name + '：' || '--' }}</label>
      <div class="iam-property-value" :title="item.values.map(val => val.name).join('，')">
        {{ item.values.map(val => val.name).join('，') || '--' }}
      </div>
    </div>
  </div>
</template>
<style lang="postcss" scoped>
    .iam-property-content {
        padding: 13px 16px;
        max-height: 186px;
        background: #f7f9fb;
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
        .iam-property-item {
            display: flex;
            justify-content: flex-start;
            font-size: 12px;
            color: #63656e;
            &.set-margin-bottom {
                margin-bottom: 8px;
            }
            .iam-property-label {
                display: inline-block;
                max-width: 83px;
                text-align: left;
                color: #979ba5;
                font-weight: 600;
            }
            .iam-property-value {
                flex: 0 0 350px;
                color: #63656e;
                word-break: break-all
            }
        }
    }
</style>

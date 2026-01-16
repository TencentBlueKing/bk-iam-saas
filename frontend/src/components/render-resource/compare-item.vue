<template>
  <div :class="['iam-instance-content', { 'set-marging-top': hasGap }]">
    <p class="iam-instance-title" v-bk-xss-html="title" />
    <div class="iam-instance-item">
      <p v-for="(item, index) in data" :key="index" class="value">
        <render-span :content="item.name" :status="item.status" :visible="true" />
      </p>
    </div>
  </div>
</template>
<script>
  import RenderSpan from '../render-span';
  export default {
    name: '',
    components: {
      RenderSpan
    },
    props: {
      hasGap: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      data: {
        type: Array,
        default: () => []
      }
    }
  };
</script>
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
            .value {
                max-width: 400px;
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

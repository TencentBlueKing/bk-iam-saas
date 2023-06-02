<template>
  <div class="iam-collapse-item">
    <bk-collapse-item ref="collapseItem" v-bind="$attrs" v-on="$listeners" hide-arrow>
      <template #default>
        <slot />
      </template>
      <template #content>
        <slot name="content" />
      </template>
    </bk-collapse-item>
  </div>
</template>
<script>
  export default {
    inject: ['collapse'],
    data () {
      return {};
    },
    mounted () {
      // const unwatch = this.$watch(() => this.$refs.collapseItem.isActive, newValue => {
      //     this.iconType = newValue ? 'arrow-full-down' : 'arrow-full-right'
      // }, {
      //     immediate: true
      // })
      // this.$once('hook:beforeDestroy', () => {
      //     unwatch()
      // })
    }
  };
</script>
<style lang='postcss'>
    .bk-collapse {
        border-bottom: 1px solid #dcdee5;
    }
    .iam-collapse-item {
        .bk-collapse-item-header {
            font-size: 12px;
            font-weight: 600;
            border: 1px solid #dcdee5;
            border-bottom: none;
            background: #FAFBFD;
        }
        .bk-collapse-item .bk-collapse-item-content {
            min-height: 42px;
            border-right: 1px solid #dcdee5;
            border-left: 1px solid #dcdee5;
        }
        .bk-collapse-item .bk-collapse-item-content {
            padding: 0;
        }
    }
</style>

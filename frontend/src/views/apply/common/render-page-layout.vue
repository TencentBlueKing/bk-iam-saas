<template>
  <div class="page-layout">
    <div
      :class="[
        'left-layout',
        { 'external-left-height': externalLeftLayoutHeight }
      ]">
      <slot />
    </div>
    <div
      :class="[
        'right-layout',
        { 'external-right-height': externalRightLayoutHeight }
      ]">
      <slot name="right" />
    </div>
  </div>
</template>
<script>
    /**
     * render-page-layout
     *
     * @return component
     */
  export default {
    name: '',
    props: {
      externalLeftLayoutHeight: {
        type: Boolean,
        default: false
      },
      externalRightLayoutHeight: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {};
    }
  };
</script>
<style lang="postcss" scoped>
    .page-layout {
        display: flex;
        padding: 0;
        .left-layout {
            flex: 0 0 280px;
            height: calc(100vh - 61px);
            background: #fff;
            overflow: hidden;
        }
        .right-layout {
            padding: 30px;
            flex: 1 0 auto;
            width: calc(100% - 280px);
            height: calc(100vh - 61px);
            background: #f5f6fa;
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
        }

        .external-left-height {
            height: calc(100vh);
        }

        .external-right-height {
            padding: 30px 30px 0;
            height: calc(100vh - 5px);
        }
    }
</style>

<template>
  <div class="iam-action-block-wrapper" :class="extCls" @click.stop="handleClick">
    <section class="action-wrapper">
      <Icon bk type="plus-circle-shape" />
      <span>{{ title }}</span>
    </section>
    <Icon
      type="info-fill"
      class="info-icon"
      v-bk-tooltips.top="{ content: tips, width: 236, extCls: 'iam-tooltips-cls' }" />
    <slot />
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      title: {
        type: String,
        required: true
      },
      extCls: {
        type: String,
        default: ''
      },
      tips: {
        type: String,
        default: ''
      }
    },
    methods: {
      handleClick () {
        this.$emit('on-click');
      }
    }
  };
</script>
<style lang="postcss">
    .iam-action-block-wrapper {
        position: relative;
        display: flex;
        justify-content: flex-start;
        padding-left: 13px;
        line-height: 64px;;
        background: #fff;
        border-radius: 2px;
        box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .1);
        cursor: pointer;
        .action-wrapper {
            font-size: 14px;
            color: #3a84ff;
            &:hover {
                color: #699df4;
            }
            i {
                position: relative;
                top: -1px;
                left: 2px;
            }
        }
        .info-icon {
            margin-left: 2px;
            line-height: 64px;
            color: #c4c6cc;
            &:hover {
                color: #3a84ff;
            }
        }
    }
</style>

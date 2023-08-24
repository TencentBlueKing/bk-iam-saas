<template>
  <div class="system-access-action-block-wrapper" :class="extCls" @click.stop="handleClick">
    <section class="action-wrapper">
      <Icon bk type="plus-circle-shape" />
      <span>{{ title }}</span>
    </section>
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
      }
    },
    methods: {
      handleClick () {
        this.$emit('on-click');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .system-access-action-block-wrapper {
        position: relative;
        line-height: 64px;;
        background: #fff;
        border-radius: 2px;
        box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .1);
        cursor: pointer;
        .action-wrapper {
            padding-left: 13px;
            font-size: 14px;
            color: #3a84ff;
            &:hover {
                color: #699df4;
            }
            i {
                font-size: 18px;
                color: #63656e;
                position: relative;
                top: 0;
                left: 2px;
                margin-right: 5px;
            }
        }
    }
</style>

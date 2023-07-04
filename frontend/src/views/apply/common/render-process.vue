<template>
  <div class="iam-approval-process-wrapper"
    @click.stop="handleOpenProcessLink">
    <Icon type="url" />
    {{ $t(`m.myApply['查看审批详情']`) }}
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      link: {
        type: String,
        default: ''
      }
    },
    data () {
      return {};
    },
    methods: {
      handleOpenProcessLink () {
        window.open(this.link);
      }
    }
  };
</script>
<style lang='postcss' scoped>
    .iam-approval-process-wrapper {
        margin: 20px 0;
        padding: 0 20px;
        line-height: 64px;
        background: #fff;
        border-radius: 2px;
        box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .05);
        font-size: 14px;
        color: #3a84ff;
        cursor: pointer;
        &:hover {
            color: #699df4;
        }
    }
</style>

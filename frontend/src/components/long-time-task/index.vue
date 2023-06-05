<template>
  <bk-sideslider
    :is-show.sync="isShow"
    quick-close
    :title="'任务历史'"
    ext-cls="iam-long-time-task-slider">
    <div slot="content">

    </div>
  </bk-sideslider>
</template>
<script>
  export default {
    name: '',
    data () {
      return {
        isShow: false
      };
    },
    methods: {

    }
  };
</script>
<style lang="postcss">
    .iam-long-time-task-slider {

    }
</style>

<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      ext-cls="iam-member-template-detail-side"
      :quick-close="true"
      @update:isShow="handleCancel"
    >
      <div slot="header" class="iam-member-template-detail-side-header">
        <span>{{ $t(`m.memberTemplate['模板详情']`) }}</span>
        <span class="custom-header-divider">|</span>
        <span class="single-hide custom-header-name" :title="curDetailData.name">
          {{ curDetailData.name }}
        </span>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  export default {
    props: {
      show: {
        type: Boolean,
        default: false
      },
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        isShowSideSlider: false,
        width: 960
      };
    },
    methods: {
      handleCancel () {}
    }
  };
</script>

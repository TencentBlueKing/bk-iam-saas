<template>
  <div>
    <bk-dialog
      v-model="show"
      :show-footer="showFooter"
      :width="width"
      :position="position"
      ext-cls="space-interview-dialog"
      v-bind="$attrs"
      @after-leave="handleAfterEditLeave">
      <h2>{{ $t('m.common["一"]') }}、{{ $t('m.common["什么是管理空间"]') }}</h2>
      <p>{{ $t('m.common["管理空间概念"]') }}</p>
      <!-- <img src="@/images/boot-page/space@2x.png" alt="" style="width:765px; height: 263px"> -->
      <img src="@/images/boot-page/manageSpace@2x.png" alt="" style="width:765px;">
      <h2>{{ $t('m.common["二"]') }}、{{ $t('m.common["如何使用管理空间"]') }}</h2>
      <p>1. {{ $t('m.common["我的管理空间 > 申请新建（已有管理空间忽略）"]') }}</p>
      <!-- <img src="@/images/boot-page/space2@2x.png" alt="" style="width:765px; height:300px"> -->
      <img src="@/images/boot-page/manageSpace2@2x.png" alt="" style="width:765px;">
      <p>2. {{ $t('m.common["切换顶部导航至“管理空间” ，在左上角切换“管理空间”"]') }}</p>
      <!-- <img src="@/images/boot-page/three2x2.png" alt="" style="width:765px; height:235px"> -->
      <img src="@/images/boot-page/manageSpace3@2x.png" alt="" style="width:765px;">
      <p>3. {{ $t('m.common["在左侧导航，点击 用户组 > 新建，创建用户组，设置权限和成员"]') }}</p>
      <!-- <img src="@/images/boot-page/four2x2.png" alt="" style="width:765px;height:220px"> -->
      <img src="@/images/boot-page/manageSpace4@2x.png" alt="" style="width:765px;">
    </bk-dialog>
  </div>
</template>

<script>
  export default {
    props: {
      show: {
        type: Boolean,
        default: false
      },
      width: {
        type: Number,
        default: 820
      },
      position: {
        type: Object,
        default: {
          top: 50
        }
      },
      showFooter: {
        type: Boolean,
        default: false
      }
    },
    methods: {
      handleAfterEditLeave () {
        this.$emit('update:show', false);
      }
    }
  };
</script>

<style lang="postcss" scoped>
    .space-interview-dialog {
            h2 {
                font-size: 16px;
                font-family: PingFangSC, PingFangSC-Medium;
                font-weight: 500;
                color: #63656e;
            }
            p {
                font-size: 14px;
                font-family: PingFangSC, PingFangSC-Regular;
                color: #63656e;
                margin-bottom: 15px;
            }
        }
</style>

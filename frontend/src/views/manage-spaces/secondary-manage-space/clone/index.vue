<template>
  <div>
    <!-- 新建、克隆、编辑容器组件下的公共展示组件 -->
    <RenderInfoForm
      :title="title"
      :id="$route.params.id"
      :loading="submitLoading"
      @on-submit="handleSubmit"
    />
  </div>
</template>

<script>
  import RenderInfoForm from '../components/render-info-form.vue';
  export default {
    components: {
      RenderInfoForm
    },
    data () {
      return {
        submitLoading: false,
        title: this.$t(`m.nav['克隆二级管理空间']`)
      };
    },
    methods: {
      async handleSubmit (payload) {
        this.submitLoading = true;
        try {
          await this.$store.dispatch('spaceManage/addSecondManager', payload);
          await this.$store.dispatch('roleList');
          this.messageSuccess(this.$t(`m.info['克隆二级管理空间成功']`), 1000);
          this.$router.go(-1);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      }
    }
  };
</script>

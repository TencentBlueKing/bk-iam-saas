<template>
  <component
    ref="actionChild"
    :mode="'create'"
    :is="'CreateTemplate'"
  />
</template>

<script>
  import CreateTemplate from '../components/render-content';
  export default {
    components: {
      CreateTemplate
    },
    methods: {
      async fetchPageData () {
        await this.$refs.actionChild.fetchInitData();
      }
    }
  };
</script>

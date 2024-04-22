<template>
  <component
    ref="actionChild"
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
        await this.$refs.actionChild.fetchPageData();
      }
    }
  };
</script>

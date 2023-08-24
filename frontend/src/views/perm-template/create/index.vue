<template>
  <component
    :is="componentId"
    ref="com">
  </component>
</template>
<script>
  import CreateTemplate from '../components/render-content';

  export default {
    name: '',
    components: {
      CreateTemplate
    },
    data () {
      return {
        componentId: 'CreateTemplate'
      };
    },
    methods: {
      async fetchPageData () {
        await this.$refs.com.fetchPageData();
      }
    }
  };
</script>

<template>
  <component
    ref="actionChild"
    mode="edit"
    :is="componentId"
    :id="$route.params.id"
  />
</template>

<script>
  import EditTemplate from '../components/render-content';

  export default {
    components: {
      EditTemplate
    },
    data () {
      return {
        componentId: 'EditTemplate'
      };
    },
    methods: {
      async fetchPageData () {
        await this.$refs.actionChild.fetchInitData();
      }
    }
  };
</script>

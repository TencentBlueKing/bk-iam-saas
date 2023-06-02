<template>
  <component
    ref="com"
    mode="edit"
    :is="componentId"
    :id="$route.params.id" />
</template>
<script>
  import store from '@/store';
  import EditTemplate from '../components/render-content';

  export default {
    name: '',
    components: {
      EditTemplate
    },
    data () {
      return {
        componentId: 'EditTemplate'
      };
    },
    beforeRouteEnter (to, from, next) {
      store.commit('setHeaderTitle', '');
      next();
    },
    methods: {
      async fetchPageData () {
        await this.$refs.com.fetchPageData();
      }
    }
  };
</script>

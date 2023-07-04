<template>
  <content-loader
    :height="716"
    :width="maxWidth"
    v-bind="$attrs">
    <rect x="0" y="0" rx="2" ry="2" width="120" height="32" />
    <rect :x="leftBlockPosition" y="0" rx="2" ry="2" width="500" height="32" />
    <rect x="0" y="62" rx="2" ry="2" :width="maxWidth" height="24" />
    <rect x="0" y="105" rx="2" ry="2" :width="maxWidth" height="24" />
    <rect x="0" y="148" rx="2" ry="2" :width="maxWidth" height="24" />
    <rect x="0" y="190" rx="2" ry="2" :width="maxWidth" height="24" />
    <rect x="0" y="230" rx="2" ry="2" :width="maxWidth" height="24" />
    <rect x="0" y="273" rx="2" ry="2" :width="maxWidth" height="24" />
    <rect x="0" y="315" rx="2" ry="2" :width="maxWidth" height="24" />
    <rect x="0" y="358" rx="2" ry="2" :width="maxWidth" height="24" />
  </content-loader>
</template>
<script>
  import { ContentLoader } from 'vue-content-loader';
  export default {
    components: {
      ContentLoader
    },
    props: {
      maxWidth: {
        type: Number,
        required: true
      }
    },
    computed: {
      leftBlockPosition () {
        return this.maxWidth - 420;
      }
    }
  };
</script>

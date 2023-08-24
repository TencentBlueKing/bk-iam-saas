<template>
  <img :src="image" :class="['iam-svg', extCls]" :alt="alt">
</template>
<script>
  export default {
    name: '',
    props: {
      name: {
        type: String,
        default: 'empty-display'
      },
      alt: {
        type: String,
        default: ''
      },
      extCls: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        image: ''
      };
    },
    watch: {
      name: {
        handler (value) {
          this.image = require(`../../images/${value}.svg`);
        },
        immediate: true
      }
    }
  };
</script>

<template>
  <div>
    <div id="container-user-display-name">
      <bk-user-display-name :user-id="getDisplayTooltip()" />
    </div>
    <div v-bk-tooltips="htmlConfig">
      <bk-user-display-name :user-id="userId" />
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      userId: {
        type: [Array, String],
        default: '--'
      },
      displayValue: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        htmlConfig: {
          allowHtml: true,
          theme: 'dark',
          content: '#container-user-display-name',
          placement: 'top-start'
        }
      };
    },
    watch: {
      displayValue: {
        handler (value) {
          if (value.length) {
            this.getDisplayTooltip();
          }
        },
        immediate: true
      }
    },
    methods: {
      getDisplayTooltip () {
        if (this.displayValue.length) {
          const results = [];
          this.displayValue.map(v => {
            results.push(v.username || v);
          });
          return results;
        }
        return this.userId;
      }
    }
  };
</script>

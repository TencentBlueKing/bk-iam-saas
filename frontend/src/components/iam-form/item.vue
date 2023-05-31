<template>
  <bk-form-item
    ref="formItem"
    class="iam-form-item"
    v-bind="$attrs"
    v-on="$listeners">
    <slot />
    <p v-if="validator.state === 'error'" class="error">{{ validator.content }}</p>
  </bk-form-item>
</template>
<script>
  export default {
    name: 'iam-form-item',
    data () {
      return {
        validator: {
          state: '',
          content: ''
        }
      };
    },
    mounted () {
      this.validator = this.$refs.formItem.validator;
    }
  };
</script>
<style lang='postcss'>
    .iam-form-item {
        .bk-label {
            font-size: 12px;
            width: auto !important;
        }
        .bk-form-content {
            flex-direction: column;
        }
        .error {
            margin-bottom: -4px;
            font-size: 12px;
            color: #ff4d4d;
        }
        .tooltips-icon {
            display: none;
        }
    }
</style>

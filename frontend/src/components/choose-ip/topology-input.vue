<template>
  <div
    :class="[
      'iam-topology-input',
      { 'reset-padding': isUsedByTree }
    ]"
    :style="customStyle">
    <bk-input
      ref="input"
      :clearable="false"
      v-model="value"
      :placeholder="placeholder"
      ext-cls="iam-topology-search-input-cls"
      :disabled="disabled"
      @enter="handleKeyEnter">
    </bk-input>
  </div>
</template>
<script>
  import il8n from '@/language';
  export default {
    name: '',
    props: {
      disabled: {
        type: Boolean,
        default: false
      },
      scene: {
        type: String,
        default: ''
      },
      placeholder: {
        type: String,
        default: il8n('common', '搜索')
      },
      isFilter: {
        type: Boolean,
        default: false
      },
      customStyle: {
        type: Object,
        default: () => {}
      }
    },
    data () {
      return {
        value: ''
      };
    },
    computed: {
      isUsedByTree () {
        return this.scene === 'tree';
      }
    },
    watch: {
      value (newVal, oldVal) {
        if (newVal === '' && oldVal !== '' && this.isFilter) {
          this.$emit('on-search', '');
        }
      }
    },
    methods: {
      handleKeyEnter () {
        this.handleSearch();
      },

      handleSearch () {
        if (this.value === '') {
          return;
        }
        this.$emit('on-search', this.value);
      },

      handleSetFocus () {
        this.$refs.input.focus();
      }
    }
  };
</script>
<style lang="postcss">
    .iam-topology-input {
        padding: 0 10px;
        background: #fafbfd;
        &.reset-padding {
            padding: 0 0 0 3px;
        }
    }
</style>

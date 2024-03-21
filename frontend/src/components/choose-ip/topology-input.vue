<template>
  <div
    :class="[
      'iam-topology-input',
      customClass,
      { 'reset-padding': isUsedByTree }
    ]"
  >
    <bk-input
      ref="input"
      v-model="value"
      ext-cls="iam-topology-search-input-cls"
      :right-icon="'bk-icon icon-search'"
      :clearable="true"
      :placeholder="placeholder"
      :disabled="disabled"
      @enter="handleKeyEnter"
      @right-icon-click="handleIconClick"
      @clear="handleClear">
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
      customClass: {
        type: String
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

      handleIconClick () {
        this.handleSearch();
      },

      handleClear () {
        this.$emit('on-search', '');
      },

      handleSearch () {
        // if (!this.value) {
        //   return;
        // }
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
        padding: 16px 16px 8px 16px;
        background: #ffffff;
        &.reset-padding {
          padding: 0 0 0 3px;
        }
        .icon-search {
          color: #979BA5;
          cursor: pointer;
        }
        &-side {
          padding: 0;
          background: #fafbfd;
        }
    }
</style>

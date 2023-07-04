<template>
  <div :class="['iam-render-perm', extCls]">
    <div class="header">
      <label class="title" v-if="hasTitle">{{ title }}</label>
      <div :class="['sub-title', { 'set-margin-left': hasTitle }]">{{ subTitle }}</div>
    </div>
    <div class="content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      expanded: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      subTitle: {
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
        isExpanded: this.expanded
      };
    },
    computed: {
      hasTitle () {
        return this.title !== '';
      }
    },
    watch: {
      expanded (value) {
        this.isExpanded = !!value;
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-render-perm {
        position: relative;
        min-height: 258px;
        padding-bottom: 32px;
        background: #fff;
        border-radius: 2px;
        border: 1px solid #fff;
        &:hover {
            .action {
                display: block;
            }
        }
        &.is-not-expanded:hover {
            .header {
                cursor: pointer;
            }
        }
        .header {
            display: flex;
            justify-content: flex-start;
            padding: 0 30px;
            height: 64px;
            line-height: 60px;
            font-size: 14px;
            color: #63656e;
            border-radius: 2px;
            .title {
                font-weight: 600;
            }
            .sub-title {
                color: #979ba5;
                &.set-margin-left {
                    margin-left: 42px;
                }
            }
        }
        .content {
            position: relative;
            .expand-action {
                padding: 20px 0 5px 0;
                width: 100%;
                line-height: 16px;
                font-size: 12px;
                color: #979ba5;
                text-align: center;
                cursor: pointer;
            }
            .slot-content {
                padding: 0 30px 0 30px;
            }
        }
    }
</style>

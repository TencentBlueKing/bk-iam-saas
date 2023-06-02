<template>
  <div class="iam-popover-confirm">
    <slot></slot>
    <div class="iam-popover-content" ref="popoverContent"
      :style="{
        width: parsedWidth,
        minWidth: parsedMinWidth
      }">
      <h2 class="confirm-title" ref="confirmTitle">
        <slot name="title">{{title}}</slot>
      </h2>
      <p class="confirm-content" ref="confirmContent">
        <slot name="content">{{content}}</slot>
      </p>
      <div class="confirm-options">
        <slot name="options">
          <bk-button class="confirm-option-button"
            theme="primary"
            size="small"
            :loading="pending"
            @click="handleConfirm">
            {{confirmText}}
          </bk-button>
          <bk-button class="confirm-option-button"
            size="small"
            :disabled="pending"
            @click="handleCancel">
            {{cancelText}}
          </bk-button>
        </slot>
      </div>
    </div>
  </div>
</template>
<script>
  import il8n from '@/language';

  export default {
    name: 'iam-popover-confirm',
    props: {
      title: {
        type: String,
        default: ''
      },
      content: {
        type: String,
        default: ''
      },
      confirmText: {
        type: String,
        default: il8n('common', '确定')
      },
      cancelText: {
        type: String,
        default: il8n('common', '取消')
      },
      placement: {
        type: String,
        default: 'top'
      },
      theme: {
        type: String,
        default: 'light'
      },
      contentWidth: {
        type: [String, Number],
        default: 280
      },
      contentMinWidth: {
        type: [String, Number],
        default: ''
      },
      disabled: Boolean,
      confirmHandler: Function,
      cancelHandler: Function
    },
    data () {
      return {
        instance: null,
        pending: false
      };
    },
    computed: {
      parsedWidth () {
        const width = parseInt(this.contentWidth);
        return isNaN(width) ? 'auto' : (width + 'px');
      },
      parsedMinWidth () {
        const minWidth = parseInt(this.contentMinWidth);
        return isNaN(minWidth) ? 'auto' : (minWidth + 'px');
      }
    },
    watch: {
      disabled (disabled) {
        if (this.instance) {
          disabled ? this.instance.disable() : this.instance.enable();
        }
      }
    },
    mounted () {
      this.init();
    },
    beforeDestroy () {
      this.instance = null;
    },
    methods: {
      init () {
        this.instance = this.$bkPopover(this.$el, {
          theme: this.theme + ' iam-popover-confirm',
          interactive: true,
          placement: this.placement,
          content: this.$refs.popoverContent,
          trigger: 'click',
          arrow: true,
          onShow: () => {
            this.$emit('show');
          },
          onHidden: () => {
            this.$emit('cancel', this);
          }
        });
        this.disabled && this.instance.disable();
      },
      async handleConfirm () {
        if (typeof this.confirmHandler === 'function') {
          try {
            this.pending = true;
            await this.confirmHandler(this.instance);
          } catch (e) {
            console.error(e);
          } finally {
            this.pending = false;
          }
        }
        this.instance && this.hide();
        this.$emit('confirm', this);
      },
      hide () {
        this.instance && this.instance.hide();
      },
      handleCancel () {
        this.hide();
        this.$emit('cancel', this);
      }
    }
  };
</script>

<style lang="postcss">
    .iam-popover-confirm {
        display: inline-block;
    }
    .iam-popover-confirm-theme.tippy-tooltip {
        .tippy-content{
            padding: 20px;
        }
        .iam-popover-content {
            .confirm-title {
                font-size: 16px;
                line-height: 20px;
                font-weight: normal;
                color: #313238;
            }
            .confirm-content {
                margin: 10px 0 0 0;
                font-size: 12px;
                color: #63656E;
            }
            .confirm-options {
                display: flex;
                justify-content: flex-end;
                margin: 16px 0 0 0;
            }
            .confirm-option-button {
                margin: 0 0 0 10px;
                min-width: 60px;
                height: 24px;
                line-height: 22px;
            }
        }
    }
</style>

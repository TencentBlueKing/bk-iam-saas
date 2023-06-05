<template>
  <div class="bk-tooltip">
    <div class="bk-tooltip-content" ref="html">
      <slot name="content">{{content}}</slot>
    </div>
    <div ref="reference" class="bk-tooltip-ref" tabindex="-1">
      <slot></slot>
    </div>
  </div>
</template>

<script>
  import Tippy, { getValidTippyProps } from 'bk-magic-vue/lib/utils/tippy';
  import zIndexManager from 'bk-magic-vue/lib/utils/z-index-manager';
  import popManager from 'bk-magic-vue/lib/utils/pop-manager';

  export default {
    name: 'iamCascadePopover',
    props: {
      placement: {
        type: String,
        default: 'top'
      },
      content: {
        type: String,
        default: ''
      },
      theme: {
        type: String,
        default: 'dark'
      },
      interactive: {
        type: [Boolean, String],
        default: true
      },
      arrow: {
        type: [Boolean, String],
        default: true
      },
      arrowType: {
        type: String,
        default: 'sharp'
      },
      showOnInit: {
        type: Boolean,
        default: false
      },
      arrowTransform: {
        type: String,
        default: ''
      },
      trigger: {
        type: String,
        default: 'mouseenter focus'
      },
      animation: {
        type: String,
        default: 'shift-away'
      },
      distance: {
        type: Number,
        default: 10
      },
      width: {
        type: [String, Number],
        default: 'auto'
      },
      maxWidth: {
        type: [String, Number],
        default: 'auto'
      },
      offset: {
        type: [Number, String],
        default: 0
      },
      always: {
        type: Boolean,
        default: false
      },
      followCursor: {
        type: [Boolean, String],
        default: false
      },
      sticky: {
        type: [Boolean, String],
        default: false
      },
      delay: {
        type: Number,
        default: 100
      },
      size: {
        type: String,
        default: 'small'
      },
      onShow: {
        type: Function,
        default () {}
      },
      onHide: {
        type: Function,
        default () {}
      },
      tippyOptions: {
        type: Object,
        default () {
          return {};
        }
      },
      // 外部设置的 class name
      extCls: {
        type: String,
        default: ''
      },
      disabled: Boolean
    },
    data () {
      return {
        instance: null
      };
    },
    watch: {
      disabled (disabled) {
        if (this.instance) {
          disabled ? this.instance.disable() : this.instance.enable();
        }
      }
    },
    mounted () {
      const options = getValidTippyProps(
        Object.assign({}, { appendTo: popManager.container }, this.tippyOptions, this.$props)
      );
      const onShow = options.onShow;
      const onHide = options.onHide;
      options.onShow = tip => {
        tip.set({ zIndex: zIndexManager.nextTickIndex(2) });
        onShow && onShow(tip);
        this.$emit('show');
      };
      options.onHide = tip => {
        onHide && onHide(tip);
        this.$emit('hide');
      };
      options.content = this.$refs.html;
      if (this.always) {
        options.showOnInit = true;
        options.hideOnClick = false;
        options.trigger = 'manual';
      }
      this.instance = Tippy(this.$refs.reference, options);
      if (this.disabled) {
        this.instance.disable();
      }
    },
    updated () {
      this.instance.setContent(this.$refs.html);
      if (this.instance.popperInstance) {
        this.instance.popperInstance.update();
      }
    },
    beforeDestroy () {
      this.instance.destroy();
    },
    methods: {
      showHandler () {
        this.instance.show();
      },
      hideHandler () {
        this.instance.hide();
      }
    }
  };
</script>

<style scoped>
    @import './popover.css';
</style>

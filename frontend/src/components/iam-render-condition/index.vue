<template>
  <div
    :class="[
      'iam-condition-item',
      { active: isActive },
      { error: isError },
      { disabled: isDisabled }
    ]"
    @mouseenter="handleMouseenter"
    @mouseleave="handleMouseleave"
    @click.stop="handleClick"
  >
    <div
      class="iam-input-text"
      :title="!isEmpty ? hoverTitle || curValue : ''"
      @click.stop="handleClick"
    >
      <section
        :class="[
          'iam-condition-input',
          { 'is-empty': isEmpty || ['', $t(`m.verify['请选择']`)].includes(curValue) }
        ]"
        @click.stop="handleClick"
      >
        {{ curValue || $t(`m.verify['请选择']`) }}
      </section>
    </div>
    <div class="operate-icons">
      <div
        v-if="canView && canOperate"
        class="operate-icon"
        :title="$t(`m.common['预览']`)"
        @click.stop="handleView"
      >
        <Icon type="see-details" />
      </div>
      <div
        v-if="!isEmpty && canOperate && canCopy"
        class="operate-icon"
        :title="$t(`m.common['复制']`)"
        @click.stop="handleCopy">
        <Icon type="copy" />
      </div>
      <div
        v-if="canOperate && canPaste"
        class="operate-icon paste-icon"
        :title="$t(`m.common['粘贴']`)"
        @click.stop="handlePaste"
      >
        <spin-loading v-if="pasteLoading" />
        <Icon v-else type="paste" />
      </div>

      <!-- 批量粘贴 -->
      <div
        v-if="(canOperate && canPaste) || immediatelyShow"
        class="operate-icon"
        :title="$t(`m.common['批量粘贴']`)"
        @mouseenter="iconEnter = true"
        @mouseleave="iconEnter = false"
        @click.stop="handleBatchPaste"
      >
        <iam-svg :name="iconEnter ? 'brush-fill-active' : 'brush-fill'" />
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      value: {
        type: String,
        default: ''
      },
      isEmpty: {
        type: Boolean,
        default: false
      },
      canView: {
        type: Boolean,
        default: false
      },
      canPaste: {
        type: Boolean,
        default: false
      },
      canOperate: {
        type: Boolean,
        default: true
      },
      canCopy: {
        type: Boolean,
        default: true
      },
      isError: {
        type: Boolean,
        default: false
      },
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      disabled: {
        type: Boolean,
        default: false
      },
      hoverTitle: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        curValue: '',
        isActive: false,
        immediatelyShow: false,
        isLoading: false,
        pasteLoading: false,
        iconEnter: false
      };
    },
    computed: {
      isDisabled () {
        return this.isLoading || this.pasteLoading || this.disabled;
      }
    },
    watch: {
      value: {
        handler (val) {
          this.curValue = val;
        },
        immediate: true
      }
    },
    methods: {
      handleView () {
        this.$emit('on-view');
      },

      handleCopy () {
        this.$emit('on-copy');
      },

      handleClick () {
        if (this.isDisabled) {
          return;
        }
        this.$emit('on-click');
      },

      handleMouseenter () {
        this.isActive = true;
        this.$emit('on-mouseover');
      },

      handleMouseleave () {
        this.isActive = false;
        this.immediatelyShow = false;
        this.$emit('on-mouseleave');
      },

      async handlePaste () {
        // 无限制时无需请求接口
        if (Object.keys(this.params).length < 1) {
          this.$emit('on-paste');
          return;
        }
        if (this.params.resource_type.condition.length === 0) {
          this.$emit('on-paste', {
            flag: true,
            data: []
          });
          return;
        }
        this.pasteLoading = true;
        const params = {
          resource_type: this.params.resource_type,
          actions: this.params.actions.slice(0, 1)
        };
        try {
          const { data } = await this.$store.dispatch('permApply/resourceBatchCopy', params);
          if (data && data.length) {
            const condition = data[0].resource_type.condition;
            this.$emit('on-paste', {
              flag: true,
              data: condition
            });
          } else {
            this.messageWarn(this.$t(`m.info['暂无可复制的资源实例']`), 3000);
          }
        } catch (e) {
          this.$emit('on-paste', {
            flag: false,
            data: null
          });
          this.messageAdvancedError(e);
        } finally {
          this.pasteLoading = false;
        }
      },

      async handleBatchPaste () {
        if (Object.keys(this.params).length < 1) {
          this.$emit('on-batch-paste');
          return;
        }
        // 无限制时无需请求接口
        if (this.params.resource_type.condition.length === 0) {
          this.$emit('on-batch-paste', {
            flag: true,
            data: []
          });
          return;
        }
        this.isLoading = true;
        try {
          const res = await this.$store.dispatch('permApply/resourceBatchCopy', this.params);
          if (res.data.length) {
            this.$emit('on-batch-paste', {
              flag: true,
              data: res.data
            });
          } else {
            this.messageWarn(this.$t(`m.info['暂无可批量复制的资源实例']`), 3000);
          }
        } catch (e) {
          this.$emit('on-batch-paste', {
            flag: false,
            data: null
          });
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      setImmediatelyShow (payload) {
        this.immediatelyShow = !!payload;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-condition-item {
  display: flex;
  align-items: center;
  position: relative;
  gap: 6px;
  padding: 0 6px;
  line-height: 1;
  vertical-align: middle;
  border: 1px solid #c4c6cc;
  border-radius: 2px;
  font-size: 0;
  color: #63656e;
  background-color: #ffffff;
  cursor: pointer;

  &:hover {
    border-color: #3a84ff;
    .operate-icon {
      visibility: visible;
    }
  }

  &.active {
    border-color: #3a84ff;
  }

  &.error {
    border-color: #ff5656;
  }

  .iam-input-text {
    flex: 1;
    min-width: 0;

    .iam-condition-input {
      height: 32px;
      line-height: 32px;
      background-color: #ffffff;
      width: 100%;
      font-size: 12px;
      box-sizing: border-box;
      border: none;
      text-align: left;
      vertical-align: middle;
      outline: none;
      resize: none;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      cursor: pointer;

      &.is-empty {
        color: #c4c6cc;
      }
    }
  }

  &.disabled {
    color: #c4c6cc;
    background-color: #fafbfd;
    border-color: #dcdee5;

    .iam-condition-input {
      cursor: not-allowed !important;
      background-color: #fafbfd;
    }
  }

  .operate-icons {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .original-resource-icon {
    padding-top: 6px;
    outline: none;
    cursor: pointer;

    img {
      width: 20px;
    }
  }

  .operate-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    visibility: hidden;
    width: 20px;
    height: 20px;
    margin-left: 6px;
    color: #979ba5;
    outline: none;
    cursor: pointer;
    flex-shrink: 0;

    &:hover {
      color: #3a84ff;
      border-radius: 2px;
      background-color: #e1ecff;

      i {
        color: #3a84ff;
      }
    }

    &.paste-icon {
      visibility: visible;
    }

    i {
      font-size: 16px;
      color: #979ba5;
    }
  }

  .iam-condition-batch-paste {
    position: absolute;
    right: -65px;
    top: 0px;
    width: 71px;
    height: 32px;
    line-height: 30px;
    text-align: center;
    background-color: #ffffff;
    border: 1px solid #dcdee5;
    box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, .1);
    z-index: 999999;

    .batch-paste-wrapper {
      position: relative;
      height: 38px;
      background-color: transparent;
    }

    .batch-paste-action {
      line-height: 25px;
      background-color: #ffffff;
    }

    .triangle {
      position: absolute;
      left: -5px;
      bottom: 18px;
      width: 10px;
      height: 10px;
      background-color: #ffffff;
      transform: rotate(45deg);
      border-bottom: 1px solid #dcdee5;
      border-right: 1px solid #dcdee5;
      z-index: -1;
    }
  }
}
</style>

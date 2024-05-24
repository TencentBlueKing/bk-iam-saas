<template>
  <div
    :class="['iam-condition-item', { active: isActive }, { error: isError }]"
    @mouseenter="handleMouseenter"
    @mouseleave="handleMouseleave"
    @click.stop="handleClick"
  >
    <div class="iam-input-text" :style="style" @click.stop="handleClick">
      <span :class="['iam-condition-input', { 'is-empty': isEmpty }]" @click.stop="handleClick" v-html="curValue" />
    </div>
    <div
      v-if="canView && canOperate"
      v-bk-tooltips="{ content: $t(`m.common['预览']`), disabled: !(canView && canOperate) }"
      class="operate-icon"
      @click.stop="handleView"
    >
      <Icon type="see-details" class="icon" />
    </div>
    <!-- v-if="!isEmpty && canOperate && canCopy" -->
    <div
      v-if="canOperate && canCopy"
      v-bk-tooltips="{ content: $t(`m.common['复制']`), disabled: !(canOperate && canCopy) }"
      class="operate-icon"
      @click.stop="handleCopy"
    >
      <Icon type="copy" class="icon" />
    </div>
    <div
      v-if="canOperate && canPaste"
      v-bk-tooltips="{ content: $t(`m.common['粘贴']`) }"
      :class="['operate-icon', { 'is-disabled': isPasteDisabled }]"
      @click.stop="handlePaste"
    >
      <spin-loading v-if="pasteLoading" />
      <Icon v-else type="paste" class="icon" />
    </div>

    <!-- <div class="iam-condition-batch-paste"
      v-if="(canOperate && canPaste) || immediatelyShow">
      <section class="batch-paste-wrapper">
        <section class="batch-paste-action">
          <spin-loading v-if="isLoading" />
          <bk-button
            v-else
            text
            theme="primary"
            @click.native.stop
            @click="handleBatchPaste">
            {{ $t(`m.common['批量粘贴']`) }}
          </bk-button>
        </section>
        <div class="triangle"></div>
      </section>
    </div> -->
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
      aggregateParams: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        curValue: '',
        isActive: false,
        immediatelyShow: false,
        isLoading: false,
        pasteLoading: false
      };
    },
    computed: {
      style () {
        const statusLen = [this.canView, this.canPaste, this.canCopy].filter(status => !!status).length;
        return {
          width: `calc(100% - ${statusLen * 20}px)`
        };
      },
      isDisabled () {
        return this.isLoading || this.pasteLoading;
      },
      isPasteDisabled () {
        return Object.keys(this.params).length < 1;
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

      handleCopy () {
        if (this.isEmpty) {
          this.messageWarn(this.$t(`m.common['暂无可复制内容']`), 3000);
          return;
        }
        this.$emit('on-copy');
      },

      async handlePaste () {
        console.log(this.params, 5455);
        if (this.isPasteDisabled) {
          this.$emit('on-paste');
          return;
        }
        const { actions, isAggregate, resource_type } = this.params;
        // 无限制时无需请求接口
        // eslint-disable-next-line camelcase
        if (resource_type && resource_type.condition.length === 0) {
          this.$emit('on-paste', {
            flag: true,
            data: []
          });
          return;
        }
        this.pasteLoading = true;
        const params = {
          resource_type,
          actions: isAggregate ? actions : actions.slice(0, 1)
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
            this.messageWarn(this.$t(`m.info['暂无可批量复制包含有属性条件的资源实例']`), 3000);
          }
        } catch (e) {
          this.$emit('on-paste', {
            flag: false,
            data: null
          });
          console.error(e);
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
          const { data } = await this.$store.dispatch('permApply/resourceBatchCopy', this.params);
          if (data && data.length) {
            this.$emit('on-batch-paste', {
              flag: true,
              data
            });
          } else {
            this.messageWarn(this.$t(`m.info['暂无可批量复制包含有属性条件的资源实例']`), 3000);
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
    justify-content: flex-start;
    position: relative;
    padding: 0 12px;
    width: 100%;
    line-height: 1;
    vertical-align: middle;
    border: 1px solid #c4c6cc;
    border-radius: 2px;
    font-size: 0;
    color: #63656e;
    background: #fff;
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
      .iam-condition-input {
          height: 32px;
          line-height: 32px;
          background-color: #fff;
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
    .operate-icon {
      display: inline-block;
      visibility: hidden;
      margin: 6px 0 0 6px;
      padding: 2px;
      width: 20px;
      height: 20px;
      outline: none;
      cursor: pointer;
      .icon {
        font-size: 16px;
        color: #3a84ff;
      }
      &:hover {
        border-radius: 2px;
        background-color: #e1ecff;
      }
      &.is-disabled {
        color: #dcdee5;
        &:hover {
          background-color: transparent;
          cursor: not-allowed;
        }
        .icon {
          color: #dcdee5;
        }
      }
    }
    .iam-condition-batch-paste {
      position: absolute;
      right: 0;
      top: -40px;
      width: 71px;
      height: 32px;
      line-height: 30px;
      text-align: center;
      background: #fff;
      border: 1px solid #dcdee5;
      box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, .1);
      z-index: 1;
      .batch-paste-wrapper {
        position: relative;
        height: 38px;
        background: transparent;
      }
      .batch-paste-action {
        line-height: 25px;
        background: #fff;
      }
      .triangle {
        position: absolute;
        left: 29px;
        bottom: 3px;
        width: 10px;
        height: 10px;
        background: #fff;
        transform: rotate(45deg);
        border-bottom: 1px solid #dcdee5;
        border-right: 1px solid #dcdee5;
        z-index: -1;
      }
    }
  }
</style>

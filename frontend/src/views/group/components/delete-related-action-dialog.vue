<template>
  <bk-dialog
    v-model="isShowDialog"
    :width="width"
    :title="title"
    :mask-close="false"
    :close-icon="false"
    header-position="center"
    :show-footer="false"
    :ext-cls="!relatedActionList.length
      ? 'iam-delete-related-action-dialog no-padding-dialog'
      : 'iam-delete-related-action-dialog'"
    @after-leave="handleAfterDeleteLeave">
    <div class="delete-content-wrapper">
      <div
        v-if="tip.length > 0"
        class="delete-tips"
      >
        <p class="delete-tips-title">
          {{ tip }}
        </p>
        <div
          v-if="relatedActionList.length > 0"
          class="delete-tips-content"
        >
          <p
            v-for="item in relatedActionList"
            :key="item.id"
          >
            <Icon bk type="info-circle-shape" class="warn" />
            {{ item.name }}
          </p>
        </div>
        <slot name="external" />
      </div>
      <div class="operate-buttons">
        <bk-button :theme="confirmTheme" :loading="loading" @click="handleSubmitDelete">
          {{ confirmText }}
        </bk-button>
        <bk-button theme="default" style="margin-left: 10px;" @click="handleCancelDelete">
          {{ $t(`m.common['取消-dialog']`) }}
        </bk-button>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
  import il8n from '@/language';

  export default {
    props: {
      show: {
        type: Boolean,
        default: false
      },
      width: {
        type: Number,
        default: 700
      },
      title: {
        type: String,
        default: ''
      },
      tip: {
        type: String,
        default: ''
      },
      name: {
        type: String,
        default: ''
      },
      confirmText: {
        type: String,
        default: il8n('common', '确定')
      },
      confirmTheme: {
        type: String,
        default: 'primary'
      },
      loading: {
        type: Boolean,
        default: false
      },
      relatedActionList: {
        type: Array,
        default: () => []
      }
    },
    computed: {
      isShowDialog: {
        get () {
          return this.show;
        },
        set (value) {
          this.$emit('update:show', value);
        }
      }
    },
    methods: {
      handleSubmitDelete () {
        this.$emit('on-submit');
      },
  
      handleCancelDelete () {
        this.$emit('update:show', false);
      },
  
      handleAfterDeleteLeave () {
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
      }
    }
  };
  </script>

<style lang='postcss' scoped>
/deep/ .iam-delete-related-action-dialog {
  .delete-content-wrapper {
    .delete-tips {
      padding-left: 44px;
      text-align: left;
      word-break: break-all;

      &-title {
        margin-bottom: 10px;
      }
      
      &-content {
        max-height: 500px;
        overflow-y: auto;

        &::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }

        &::-webkit-scrollbar-thumb {
          background: #dcdee5;
          border-radius: 3px;
        }

        &::-webkit-scrollbar-track {
          background: transparent;
          border-radius: 3px;
        }

        .warn {
          color: #ffb848;
        }
      }
    }

    .operate-buttons {
      margin-top: 32px;
      text-align: center;
    }
  }
  
  &.no-padding-dialog {
    .bk-dialog-header {
      padding: 0;
    }
  }
}
</style>

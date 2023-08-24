<template>
  <bk-dialog
    v-model="isShowDialog"
    :width="width"
    :title="title"
    :mask-close="false"
    :close-icon="false"
    header-position="center"
    :show-footer="false"
    :ext-cls="[
      'iam-confirm-dialog',
      { 'iam-custom-confirm': isCustomStyle }
    ]"
    @after-leave="handleAfterDeleteLeave">
    <div class="confirm-content-wrapper">
      <div class="iam-custom-dialog-title">{{ subTitle }}</div>
      <div class="operate-buttons">
        <bk-button theme="primary" :loading="loading" @click="handleSumbitDelete">
          {{ $t(`m.common['确定']`) }}
        </bk-button>
        <bk-button theme="default" style="margin-left: 10px;" @click="hideCancelDelete">
          {{ $t(`m.common['取消-dialog']`) }}
        </bk-button>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
  export default {
    name: '',
    props: {
      show: {
        type: Boolean,
        default: false
      },
      width: {
        type: Number,
        default: 400
      },
      title: {
        type: String,
        default: ''
      },
      subTitle: {
        type: String,
        default: ''
      },
      loading: {
        type: Boolean,
        default: false
      },
      isCustomStyle: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isShowDialog: false
      };
    },
    watch: {
      show: {
        handler (value) {
          this.isShowDialog = !!value;
        },
        immediate: true
      }
    },
    methods: {
      handleSumbitDelete () {
        this.$emit('on-sumbit');
      },

      hideCancelDelete () {
        this.$emit('on-cancel');
      },

      handleAfterDeleteLeave () {
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-confirm-dialog {
        .confirm-content-wrapper {
            padding-bottom: 14px;
            .operate-buttons {
                margin-top: 34px;
                text-align: center;
            }
        }
        &.iam-custom-confirm {
            .confirm-content-wrapper {
                padding-bottom: 0;
                .operate-buttons {
                    margin-top: 0;
                }
            }
        }
    }
</style>

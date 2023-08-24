<template>
  <bk-dialog
    v-model="isShowDialog"
    width="560"
    title=""
    :mask-close="false"
    header-position="left"
    :ok-text="$t(`m.common['提交']`)"
    :cancel-text="$t(`m.common['取消']`)"
    :loading="loading"
    :auto-close="false"
    ext-cls="iam-apply-join-dialog"
    @confirm="handleSumbitDelete"
    @cance="hideCancelDelete"
    @after-leave="handleAfterDeleteLeave">
    <div slot="header" class="title">
      {{ $t(`m.myApply['申请加入']`)}}
      <span class="name" :title="name">{{ $t(`m.common['【']`)}}{{ name }}{{ $t(`m.common['】']`)}}</span>
    </div>
    <div class="confirm-content-wrapper">
      <bk-input
        :placeholder="$t(`m.verify['请输入理由']`)"
        type="textarea"
        :ext-cls="isShowReasonError ? 'join-reason-error' : ''"
        :rows="3"
        :maxlength="255"
        v-model="reason"
        @input="handleReasonInput"
        @blur="handleReasonBlur">
      </bk-input>
      <p class="reason-empty-wrapper" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
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
      name: {
        type: String,
        default: ''
      },
      loading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isShowDialog: false,
        reason: '',
        isShowReasonError: false
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
      handleReasonInput (payload) {
        this.isShowReasonError = false;
      },

      handleReasonBlur (payload) {
        if (payload === '') {
          this.isShowReasonError = true;
        }
      },

      handleSumbitDelete () {
        if (this.reason === '') {
          this.isShowReasonError = true;
          return;
        }
        this.$emit('on-sumbit', this.reason);
      },

      hideCancelDelete () {
        this.$emit('on-cancel');
      },
            
      handleAfterDeleteLeave () {
        this.reason = '';
        this.isShowReasonError = false;
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-apply-join-dialog {
        .title {
            line-height: 26px;
            color: #313238;
            .name {
                display: inline-block;
                max-width: 382px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: top;
            }
        }
        .confirm-content-wrapper {
            .join-reason-error {
                .bk-textarea-wrapper {
                    border-color: #ff5656;
                }
            }
            .reason-empty-wrapper {
                margin-top: 5px;
                font-size: 12px;
                color: #ff4d4d;
            }
        }
    }
</style>

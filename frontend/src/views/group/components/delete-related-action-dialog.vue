<template>
  <bk-dialog
    v-model="isShowDialog"
    width="700"
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
        class="delete-tips"
        v-if="relatedActionList.length">
        <p class="delete-tips-title">
          {{ tip }}
        </p>
        <div class="delete-tips-content">
          <p
            v-for="item in relatedActionList"
            :key="item.id">
            <Icon bk type="info-circle-shape" class="warn" />
            {{ item.name }}
          </p>
        </div>
      </div>
      <div class="operate-buttons">
        <bk-button theme="primary" :loading="loading" @click="handleSubmitDelete">
          {{ $t(`m.common['确定']`) }}
        </bk-button>
        <bk-button theme="default" style="margin-left: 10px;" @click="handleCancelDelete">
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
                    .warn {
                        color: #ffb848;
                    }
                  }
              }
              .operate-buttons {
                  margin-top: 34px;
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

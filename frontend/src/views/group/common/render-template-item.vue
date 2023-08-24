<template>
  <div :class="
    [
      'iam-template-item',
      extCls,
      { 'is-not-expanded': !isExpanded },
      { 'external-iam-template-item': externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle }
    ]"
  >
    <div
      :class="[
        'header',
        { 'external-header-lang': externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle
          && !['zh-cn'].includes(language) }
      ]"
      @click="handleExpanded"
      @mousemove="isShowEditFill"
      @mouseleave="cancelShowEditFill">
      <section>
        <Icon
          v-if="!externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle"
          class="expanded-icon"
          :type="isExpanded ? 'down-angle' : 'right-angle'"
        />
        <span v-if="!externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle">
          {{ title }}
          <template v-if="count > 0">
            ({{ count }})
          </template>
        </span>
        <template v-if="(isExpanded || ShowEditFill) && !isUser">
          <section
            class="edit-action"
            @click.stop="handleEdit"
            v-if="!externalEdit"
          >
            <Icon type="edit-fill" v-if="isStaff || isPermTemplateDetail || isDetail ? false : true" />
          </section>
        </template>
        <bk-popconfirm
          trigger="click"
          :title="$t(`m.info['确定删除']`)"
          @confirm="handleDelete"
          v-if="isStaff || isPermTemplateDetail || isUser || isDetail ? false : true">
          <template v-if="isExpanded || ShowEditFill && !isUser">
            <template v-if="!externalDelete">
              <section class="delete-action" @click.stop="toDeletePolicyCount">
                <Icon type="delete-line" v-if="isStaff || isPermTemplateDetail ? false : true" />
              </section>
            </template>
            <!-- <section class="delete-action" @click.stop="toDeletePolicyCount">
                            <Icon type="delete-line" v-if="isStaff || isPermTemplateDetail ? false : true" />
                        </section> -->
          </template>
        </bk-popconfirm>
      </section>
    </div>
    <div class="content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
    </div>
    <section style="margin:20px 0 0 30px;" v-if="isExpanded && isEditMode" @click.stop>
      <bk-button theme="primary" size="small" :loading="loading" @click="handleSave" @click.native.stop>
        {{ $t(`m.common['保存']`) }}
      </bk-button>
      <bk-button size="small" style="margin-left: 6px;" @click="handleCancel" @click.native.stop>
        {{ $t(`m.common['取消']`) }}
      </bk-button>
    </section>
    <bk-dialog
      ext-cls="comfirmDialog"
      v-model="isShowDeleteDialog"
      :close-icon="showIcon"
      :footer-position="footerPosition"
      @confirm="handleDelete">
      <h3 style="text-align:center">{{ $t(`m.common['确认删除']`) }}</h3>
    </bk-dialog>
  </div>
</template>
<script>
  import store from '@/store';
  import { mapGetters } from 'vuex';
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
      extCls: {
        type: String,
        default: ''
      },
      count: {
        type: Number,
        default: 0
      },
      isEdit: {
        type: Boolean,
        default: false
      },
      loading: {
        type: Boolean,
        default: false
      },
      // mode: edit，detail
      mode: {
        type: String,
        default: 'edit'
      },
      externalEdit: {
        type: Boolean,
        default: false
      },
      externalDelete: {
        type: Boolean,
        default: false
      },
      externalHeaderWidth: {
        type: Number,
        default: 0
      }
    },
    data () {
      return {
        isExpanded: this.expanded,
        isEditMode: false,
        ShowEditFill: false,
        role: '',
        isShowDeleteDialog: false,
        showIcon: false,
        footerPosition: 'center',
        language: window.CUR_LANGUAGE,
        initDistance: 40
      };
    },
    computed: {
            ...mapGetters(['externalSystemsLayout']),
            isDetail () {
                return this.mode === 'detail';
            },
            isPermTemplateDetail () {
                return this.$route.name === 'permTemplateDetail';
            },
            isStaff () {
                return store.state.user.role.type === 'staff';
            },
            isUser () {
                return this.$route.name === 'user';
            }
    },
    watch: {
      expanded (value) {
        this.isExpanded = !!value;
      },
      isEdit: {
        handler (value) {
          this.isEditMode = value;
        },
        immediate: true
      }
    },
    mounted () {
      this.fetchDynamicStyle();
    },
    methods: {
      fetchDynamicStyle () {
        if (this.externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle) {
          // const len = String(this.count).length;
          // const isCN = ['zh-cn'].includes(this.language);
          // const langLen = isCN ? this.initDistance : 80;
          // const distance = len > 2 ? (len - 1) * this.initDistance : langLen;
          const root = document.querySelector(':root');
          root.style.setProperty('--translate-icon', `translate(${this.externalHeaderWidth}px, -40px)`);
        }
      },
      handleExpanded () {
        this.isExpanded = !this.isExpanded;
        this.$emit('update:expanded', true);
        this.$emit('on-expanded', this.isExpanded);
        this.$emit('toIsExpanded', false);
      },

      handleEdit () {
        this.isExpanded = true;
        this.$emit('on-expanded', this.isExpanded);
        this.$emit('on-edit');
        this.$emit('toIsExpanded', this.isExpanded);
      },

      handleSave () {
        this.$emit('on-save');
      },

      handleCancel () {
        this.isEditMode = false;
        this.$emit('on-cancel');
      },

      toDeletePolicyCount () {
        this.isExpanded = true;
        this.isShowDeleteDialog = true;
        this.$emit('on-expanded', this.isExpanded);
      },

      handleDelete () {
        this.$emit('on-delete');
      },

      isShowEditFill () {
        this.ShowEditFill = true;
      },

      cancelShowEditFill () {
        this.ShowEditFill = false;
      }
    }
  };
</script>
<style lang="postcss" scoped>
    :root {
        --translate-icon: translate(40px, -40px);
    }
    .iam-template-item {
        &.is-not-expanded:hover {
            background: #f0f1f5;
            .header {
                cursor: pointer;
            }
        }
        .header {
            position: relative;
            display: flex;
            justify-content: space-between;
            padding: 0 10px;
            height: 40px;
            line-height: 40px;
            font-size: 12px;
            color: #63656e;
            border-radius: 2px;
            cursor: pointer;
            .expanded-icon {
                line-height: 40px;
                font-size: 14px;
            }
        }
        .edit-action,
        .delete-action {
            display: inline-block;
            width: 40px;
            text-align: center;
            &:hover {
                i {
                    color: #3a84ff;
                }
            }
        }
        .content {
            position: relative;
            .slot-content {
                padding: 0 30px 0 30px;
            }
        }

        &.external-iam-template-item {
            .header {
                height: 0;
                .edit-action,
                .delete-action {
                    display: inline-block;
                    width: 40px;
                    text-align: center;
                    transform: var(--translate-icon);
                    &:hover {
                        i {
                            color: #3a84ff;
                        }
                    }
                }
                &.external-header-lang {
                    .edit-action,
                    .delete-action {
                        transform: var(--translate-icon);
                    }
                }
            }
            .slot-content {
                padding: 0;
            }
        }
    }
</style>

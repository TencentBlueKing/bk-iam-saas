<template>
  <div :class="
    [
      'system-render-template-item',
      extCls,
      { 'is-not-expanded': !isExpanded }
    ]"
  >
    <div class="header">
      <div class="flex-between sub-header-item">
        <div
          :class="[
            'sub-header-content',
            { 'has-delete': externalDelete }
          ]"
          @click.stop="handleExpanded"
        >
          <Icon
            bk
            v-if="!externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle"
            class="expanded-icon"
            :type="isExpanded ? 'down-shape' : 'right-shape'"
          />
          <span v-if="!externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle">
            <span class="sub-header-item-title">{{ title }}</span>
            <template v-if="count > 0">
              ({{ count }})
            </template>
          </span>
        </div>
        <div v-if="externalDelete" @click.stop="">
          <bk-popconfirm
            trigger="click"
            placement="bottom-end"
            ext-popover-cls="resource-perm-delete-confirm"
            :width="280"
            @confirm="handleDelete"
          >
            <div slot="content">
              <div class="popover-title">
                <div class="popover-title-text">
                  {{ deleteConfirm.title }}
                </div>
              </div>
              <div class="popover-content">
                <div class="popover-content-item">
                  <span class="popover-content-item-label">{{ deleteConfirm.label }}{{ $t(`m.common['：']`)}}</span>
                  <span class="popover-content-item-value"> {{ deleteConfirm.value }}</span>
                </div>
                <div class="popover-content-tip">
                  {{ deleteConfirm.tip }}
                </div>
              </div>
            </div>
            <div class="delete-action">
              <Icon class="delete-action-icon" type="delete-line" />
              <span class="delete-action-title">{{ deleteTitle }}</span>
            </div>
          </bk-popconfirm>
        </div>
      </div>
    </div>
    <div class="system-render-template-item-content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  export default {
    props: {
      isEdit: {
        type: Boolean,
        default: false
      },
      loading: {
        type: Boolean,
        default: false
      },
      externalEdit: {
        type: Boolean,
        default: false
      },
      externalDelete: {
        type: Boolean,
        default: false
      },
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
      mode: {
        type: String,
        default: 'edit'
      },
      deleteTitle: {
        type: String,
        default: ''
      },
      count: {
        type: Number,
        default: 0
      },
      externalHeaderWidth: {
        type: Number,
        default: 0
      },
      deleteConfirm: {
        type: Object,
        default: () => {
          return {
            title: '',
            tip: '',
            label: ''
          };
        }
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
      ...mapGetters(['user', 'externalSystemsLayout']),
      isDetail () {
        return this.mode === 'detail';
      },
      isStaff () {
        return this.user.role.type === 'staff';
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

      handleDeletePolicy () {
        // this.isExpanded = true;
        this.isShowDeleteDialog = true;
        this.$emit('on-expanded', this.isExpanded);
      },

      handleDelete () {
        this.$emit('on-delete');
      }
    }
  };
</script>

<style lang="postcss" scoped>
  :root {
    --translate-icon: translate(40px, -40px);
  }
  .system-render-template-item {
    background-color: #f0f1f5;
    .header {
      position: relative;
      display: flex;
      justify-content: space-between;
      padding-left: 28px;
      padding-right: 16px;
      height: 40px;
      line-height: 40px;
      font-size: 12px;
      color: #63656e;
      border-radius: 2px;
      cursor: pointer;
      .sub-header-item {
        width: 100%;
        .expanded-icon {
          color: #979BA5;
          line-height: 40px;
          font-size: 12px;
        }
        .edit-action,
        .delete-action {
          display: inline-block;
          color: #3a84ff;
          &-icon {
            font-size: 14px;
          }
          &-title {
            font-size: 12px;
          }
        }
        &-title {
          color: #313238;
          font-size: 12px;
          font-weight: 700;
          margin-left: 4px;
        }
        .sub-header-content {
          width: 100%;
          &.has-delete {
            width: calc(100% - 100px);
          }
        }
      }
    }
    &-content {
      position: relative;
      .slot-content {
        /* padding: 0 30px 0 30px; */
      }
    }
    &.is-not-expanded {
      &:hover {
        background-color: #f0f1f5;
        .header {
          cursor: pointer;
        }
      }
    }
  }
</style>

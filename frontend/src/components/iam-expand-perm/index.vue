<template>
  <div :class="
    [
      'system-render-template-item',
      extCls,
      { 'is-not-expanded': !isExpanded }
    ]"
  >
    <div class="expand-header">
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
            class="expanded-icon"
            :type="isExpanded ? 'down-shape' : 'right-shape'"
          />
          <slot name="headerTitle" />
        </div>
        <div @click.stop="">
          <slot name="headerOperate" />
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
      count: {
        type: Number,
        default: 0
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
      ...mapGetters(['user', 'externalSystemsLayout'])
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
    .expand-header {
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
          color: #3A84FF;
          &-icon {
            font-size: 14px;
          }
          &-title {
            font-size: 12px;
          }
          &.is-disabled {
            color: #c4c6cc;
            cursor: not-allowed;
          }
        }
        .sub-header-content {
          width: 100%;
          display: flex;
          &.has-delete {
            width: calc(100% - 200px);
          }
        }
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
    &.no-perm-item-wrapper {
      display: none;
    }
  }
</style>

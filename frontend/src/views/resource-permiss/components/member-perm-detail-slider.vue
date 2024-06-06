<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      :quick-close="true"
      ext-cls="resource-perm-member-detail-side"
      @update:isShow="handleCancel"
    >
      <div slot="header" class="resource-perm-member-detail-side-header">
        <span>{{ $t(`m.resourcePermiss['人员权限详情']`) }}</span>
        <span class="custom-header-divider">|</span>
        <span class="single-hide custom-header-name" :title="curDetailData.name">
          {{ curDetailData.name }}
        </span>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  export default {
    props: {
      show: {
        type: Boolean,
        default: false
      },
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        isShowSideSlider: false,
        width: 960
      };
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideSlider = !!value;
          if (value) {
            // this.fetchGroupDetail();
          }
        },
        immediate: true
      }
    },
    methods: {
      handleCancel () {
        this.resetData();
        this.$emit('update:show', false);
      },
  
      resetData () {
        this.width = 960;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.resource-perm-member-detail-side {
  &-header {
    display: flex;
    .custom-header-divider {
      margin: 0 8px;
      color: #dcdee5;
    }
    .custom-header-name {
      max-width: 700px;
      font-size: 12px;
      color: #979ba5;
      word-break: break-all;
    }
  }
  &-content {
    .member-template-tab {
      padding: 24px 24px 0;
      background-color: #f5f7fa;
      position: sticky;
      top: 0;
      left: 0;
      z-index: 99;
      .member-tab-groups {
        display: flex;
        &-item {
          min-width: 96px;
          display: flex;
          font-size: 14px;
          color: #63656e;
          padding: 0 20px;
          margin-right: 8px;
          height: 42px;
          line-height: 42px;
          background-color: #eaebf0;
          border-radius: 4px 4px 0 0;
          cursor: pointer;
          &:last-child {
            margin-right: 0px;
            .member-tab-groups-item-count {
              padding-left: 5px;
            }
          }
          &.is-active {
            color: #3a84ff;
            background: #ffffff;
            border-radius: 4px 4px 0 0;
          }
        }
      }
    }
    .member-template-content {
      padding: 24px 0;
    }
  }
}
</style>

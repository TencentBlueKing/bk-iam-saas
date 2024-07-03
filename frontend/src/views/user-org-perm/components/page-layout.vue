<template>
  <div class="page-layout">
    <div :class="[
      'left-layout',
      { 'no-expand': !isExpand }
    ]">
      <slot />
    </div>
    <slot name="expand-icon" />
    <div :class="[
      'right-layout',
      { 'right-layout-no-search': !isShowResourceSearch },
      { 'right-layout-no-search-show-notice': !isShowResourceSearch && showNoticeAlert && showNoticeAlert() },
      { 'no-expand': isNoExpandNoSearchData },
      { 'no-expand-has-search': isNoExpandHasSearchData },
      { 'expand-show-notice': !isNoExpandNoSearchData && showNoticeAlert && showNoticeAlert() },
      {
        'no-expand-show-notice':
          (isNoExpandNoSearchData || isNoExpandHasSearchData ) && showNoticeAlert && showNoticeAlert()
      }
    ]">
      <slot name="right" />
    </div>
  </div>
</template>

<script>
  export default {
    inject: ['showNoticeAlert'],
    props: {
      isExpand: {
        type: Boolean,
        default: true
      },
      isNoExpandNoSearchData: {
        type: Boolean,
        default: false
      },
      isNoExpandHasSearchData: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isShowResourceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true'
      };
    }
  };
</script>

<style lang="postcss" scoped>
.page-layout {
  display: flex;
  padding: 0;
  .left-layout {
    flex: 0 0 240px;
    height: calc(100vh - 61px);
    background-color: #ffffff;
    overflow: hidden;
    &.no-expand {
      display: none;
    }
  }
  .right-layout {
    padding: 16px 16px 0 0;
    flex: 1 0 auto;
    width: calc(100% - 240px);
    height: calc(100vh - 314px);
    /* background-color: #f5f6fa; */
    overflow-y: auto;
    &::-webkit-scrollbar {
      width: 4px;
      background-color: lighten(transparent, 80%);
    }
    &::-webkit-scrollbar-thumb {
      height: 5px;
      border-radius: 2px;
      background-color: #e6e9ea;
    }
    &-no-search {
      height: calc(100vh - 240px);
    }
    &.no-expand {
      height: calc(100vh - 112px);
    }
    &.no-expand-has-search {
      height: calc(100vh - 112px);
    }
    &.expand-show-notice {
      height: calc(100vh - 375px);
    }
    &.no-expand-show-notice {
      height: calc(100vh - 146px);
    }
    &-no-search-show-notice {
      height: calc(100vh - 295px);
    }
  }

  .external-right-height {
    padding: 30px 30px 0;
    height: calc(100vh - 5px);
  }
}
</style>

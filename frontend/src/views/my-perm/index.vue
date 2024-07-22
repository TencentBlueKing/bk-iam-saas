<template>
  <div class="my-perm-wrapper">
    <div
      :class="[
        'my-perm-wrapper-left-layout',
        { 'no-expand': !isExpand }
      ]"
    >
      <LeftLayout
        @on-select-tab="handleSelectTab"
      />
    </div>
    <div class="my-perm-wrapper-center">
      <div class="expand-icon" @click.stop="handleToggleExpand">
        <Icon bk :type="isExpand ? 'angle-left' : 'angle-right'" class="icon" />
      </div>
    </div>
    <div class="my-perm-wrapper-right-layout">
      <component
        ref="childRef"
        :key="comKey"
        :is="curCom"
        :group-data="selectTabData"
        :left-layout-width="leftLayoutWidth"
        :cur-search-params="querySearchParams"
        @on-clear="handleEmptyClear"
        @on-refresh="handleEmptyRefresh"
      />
    </div>
  </div>
</template>

<script>
  import LeftLayout from './components/left-layout.vue';
  import RightLayout from './components/right-layout.vue';
  export default {
    components: {
      LeftLayout,
      RightLayout
    },
    data () {
      return {
        isExpand: true,
        comKey: -1,
        comMap: new Map(
          [
            [['all', 'personalPerm', 'departPerm', 'memberTempPerm', 'customPerm', 'managerPerm', 'renewalPerm'], 'RightLayout']
          ]
        ),
        selectTabData: {
          value: ''
        },
        querySearchParams: {}
      };
    },
    computed: {
      curCom () {
        let com = '';
        for (const [key, value] of this.comMap.entries()) {
          if (Object.keys(this.selectTabData).length && key.includes(this.selectTabData.value)) {
            com = value;
            break;
          }
        }
        return com;
      },
      leftLayoutWidth () {
        return this.isExpand ? 240 : 0;
      }
    },
    methods: {
      handleToggleExpand () {
        this.isExpand = !this.isExpand;
        this.$nextTick(() => {
          this.$refs.childRef && this.$refs.childRef.handleToggleExpand();
        });
      },

      handleSelectTab (payload) {
        this.selectTabData = { ...payload };
      },

      handleEmptyClear () {
        
      },

      handleEmptyRefresh () {

      }
    }
  };
</script>

<style lang="postcss" scoped>
.my-perm-wrapper {
  position: relative;
  display: flex;
  padding: 0;
  &-left-layout {
    position: relative;
    flex-grow: 0;
    flex-shrink: 0;
    position: relative;
    width: 240px;
    min-width: 240px;
    background-color: #ffffff;
    &.no-expand {
      display: none;
    }
  }
  &-center {
    width: 16px;
    height: calc(100vh - 234px);
    .expand-icon {
      width: 16px;
      height: 64px;
      background-color: #dcdee5;
      border-radius: 0 4px 4px 0;
      position: relative;
      top: 50%;
      transform: translateY(-50%);
      cursor: pointer;
      .icon {
        color: #ffffff;
        font-size: 24px !important;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
      &:hover {
        background-color: #3a84ff;
      }
    }
  }
  &-right-layout {
    padding-top: 12px;
    padding-right: 16px;
    box-sizing: border-box;
    overflow: hidden;
  }
}
</style>

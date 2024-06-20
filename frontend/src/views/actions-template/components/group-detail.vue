<template>
  <div class="group-detail-wrapper">
    <div class="group-detail-wrapper-header">
      <span class="group-title">{{ $t(`m.actionsTemplate['用户组详情']`) }}</span>
      <span class="group-divider">|</span>
      <span class="group-name single-hide">{{ expandData.name || '--' }}</span>
    </div>
    <div class="group-detail-wrapper-tab">
      <div class="group-tab-header">
        <div
          v-for="item in tabList"
          :key="item.id"
          :class="['group-tab-item', { 'is-active': tabActive === item.id }]"
          @click.stop="handleTabChange(item.id, true)"
        >
          <span class="group-tab-item-name">{{ item.name }}</span>
        </div>
      </div>
      <div class="group-tab-content">
        <component
          ref="groupDetailComRef"
          :is="curCom"
          :key="comKey"
          :mode="'detail'"
          :cur-detail-data="curDetailData"
          :tab-active="tabActive"
        />
      </div>
    </div>
  </div>
</template>

<script>
  import GroupBasicInfo from './group-basic-info.vue';
  import GroupPermTable from './group-perm-policy.vue';
  export default {
    components: {
      GroupBasicInfo,
      GroupPermTable
    },
    props: {
      expandData: {
        type: Object
      }
    },
    data () {
      return {
        comKey: -1,
        tabActive: 'group_perm',
        curDetailData: {},
        COM_MAP: Object.freeze(
          new Map([
            [['basic_info'], 'GroupBasicInfo'],
            [['group_perm'], 'GroupPermTable']
          ])
        ),
        tabList: [
          { name: this.$t(`m.common['基本信息']`), id: 'basic_info' },
          { name: this.$t(`m.userGroup['组权限']`), id: 'group_perm' }
        ]
      };
    },
    computed: {
      curCom () {
        let com = '';
        for (const [key, value] of this.COM_MAP.entries()) {
          if (key.includes(this.tabActive)) {
            com = value;
            break;
          }
        }
        return com;
      }
    },
    watch: {
      expandData: {
        handler (value) {
          this.curDetailData = Object.assign({}, value);
          this.handleGetDetailData();
        },
        immediate: true
      }
    },
    methods: {
      handleTabChange (payload, isClick) {
        if (payload === this.tabActive && isClick) {
          return;
        }
        this.tabActive = payload;
        this.handleGetDetailData();
      },

      handleGetDetailData () {
        const typeMap = {
          basic_info: () => {
            this.$nextTick(() => {
              this.$refs.groupDetailComRef && this.$refs.groupDetailComRef.fetchDetailInfo();
            });
          },
          group_perm: () => {
            this.$nextTick(() => {
              // this.$refs.groupDetailComRef && this.$refs.groupDetailComRef.fetchDetailInfo();
            });
          }
        };
        return typeMap[this.tabActive]();
      }
    }
  };
</script>

<style lang="postcss" scoped>
.group-detail-wrapper {
  &-header {
    padding-left: 16px;
    font-size: 14px;
    display: flex;
    .group-title {
      min-width: 70px;
      color: #313238;
    }
    .group-divider {
      color: #dcdee5;
      margin: 0 8px;
    }
    .group-name {
      color: #63656E;
    }
  }
  &-tab {
    padding-top: 16px;
    background-color: #f5f7fa;
    position: sticky;
    top: 0;
    left: 0;
    z-index: 50;
    .group-tab-header {
      position: relative;
      display: flex;
      padding: 0 16px;
      .group-tab-item {
        min-width: 96px;
        display: flex;
        font-size: 14px;
        color: #63656e;
        padding: 0 24px;
        margin-right: 8px;
        height: 42px;
        line-height: 42px;
        background-color: #eaebf0;
        border-radius: 4px 4px 0 0;
        cursor: pointer;
        &:last-child {
          margin-right: 0px;
        }
        &.is-active {
          color: #3a84ff;
          background: #ffffff;
          border-radius: 4px 4px 0 0;
        }
      }
    }
    .group-tab-content {
      background-color: #ffffff;
      padding: 12px 16px;
      height: calc(100vh - 246px);
    }
  }
}
</style>

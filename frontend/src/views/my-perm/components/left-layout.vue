<template>
  <div class="my-perm-left-layout">
    <div
      v-if="renewalData.count > 0"
      :class="[
        'my-perm-left-layout-all',
        { 'is-active': active === renewalData.value }
      ]"
      @click.stop="handleSelectPerm(renewalData)"
    >
      <div class="flex-between renewal-perm-content">
        <div class="renewal-perm-label">
          <div>
            <Icon
              type="file-close"
              class="icon"
            />
          </div>
          <div class="name">
            {{ renewalData.label }}
          </div>
        </div>
        <div class="renewal-perm-total">{{ renewalData.count }}</div>
      </div>
    </div>
    <div class="my-perm-left-layout-content">
      <div
        v-for="item in permList"
        :key="item.id"
        :class="[
          'flex-between',
          'my-perm-left-layout-item',
          { 'my-perm-left-layout-item-active': item.value === active }
        ]"
        @click.stop="handleSelectPerm(item)"
      >
        <div class="perm-type-content">
          <div class="perm-type-name">
            <div
              v-if="['all'].includes(item.value)"
              class="folder-icon"
            >
              All
            </div>
            <Icon
              v-else
              :type="item.icon"
              class="folder-icon"
            />
            <div
              class="single-hide name"
              v-bk-tooltips="{
                content: item.label,
                placements: ['right-start'],
                disabled: formatShowToolTip(item)
              }"
              :ref="`perm_${item.value}`"
            >
              {{ item.label }}
            </div>
          </div>
        </div>
        <div class="perm-type-count">{{ item.count || 0 }}</div>
      </div>
    </div>
  </div>
</template>
  
<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { existValue, formatCodeData } from '@/common/util';
  export default {
    data () {
      return {
        active: 'all',
        renewalTotal: 0,
        initPermList: [
          {
            label: this.$t(`m.perm['全部权限']`),
            value: 'all',
            icon: '',
            count: 0
          },
          {
            label: this.$t(`m.userOrOrg['个人用户组权限']`),
            value: 'personalPerm',
            icon: 'file-close',
            count: 0
          },
          {
            label: this.$t(`m.userOrOrg['组织用户组权限']`),
            value: 'departPerm',
            icon: 'file-close',
            count: 0
          },
          {
            label: this.$t(`m.perm['人员模板用户组权限']`),
            value: 'memberTempPerm',
            icon: 'file-close',
            count: 0
          },
          {
            label: this.$t(`m.perm['自定义权限']`),
            value: 'customPerm',
            icon: 'file-close',
            count: 0
          },
          {
            label: this.$t(`m.perm['管理员权限']`),
            value: 'managerPerm',
            icon: 'file-close',
            count: 0
          }
        ],
        permList: [],
        permListBack: [],
        renewalData: {
          label: this.$t(`m.perm['可续期']`),
          value: 'renewalPerm',
          icon: '',
          count: 0
        },
        emptyPermData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemsLayout', 'externalSystemId', 'user']),
      isShowCustomPerm () {
        return this.externalSystemsLayout.myPerm.transfer.hideCustomData;
      },
      isShowManagerPerm () {
        return this.externalSystemsLayout.myPerm.transfer.hideManagerData;
      }
    },
    created () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-update-all-perm');
      });
      this.fetchInitTab();
    },
    mounted () {
      bus.$on('on-update-all-perm', (payload) => {
        const { allPerm, renewalGroupPermLen, renewalCustomPermLen } = payload;
        this.renewalData.count = renewalGroupPermLen + renewalCustomPermLen;
        this.permList.forEach((item) => {
          const hasData = allPerm.find((v) => v.id === item.value);
          if (hasData) {
            item.count = hasData.pagination.count;
          }
          if (['all'].includes(item.value)) {
            item.count = allPerm.reduce((prev, cur) => {
              return cur.pagination.count + prev;
            }, 0);
          }
        });
      });
    },
    methods: {
      fetchInitTab () {
        // 处理嵌入系统需要显示哪些组权限
        if (existValue('externalApp') && this.externalSystemId) {
          let hidePermTab = [];
          if (this.isShowCustomPerm) {
            hidePermTab = ['customPerm'];
          }
          if (this.isShowManagerPerm) {
            hidePermTab = [...hidePermTab, ...['managerPerm']];
          }
          this.permList = this.initPermList.filter((v) => !hidePermTab.includes(v.value));
        } else {
          this.permList = cloneDeep(this.initPermList);
        }
      },

      formatShowToolTip (payload) {
        const permRef = this.$refs[`perm_${payload.value}`];
        if (permRef && permRef.length) {
          const offsetWidth = permRef[0].offsetWidth;
          return !(offsetWidth > 132);
        }
      },

      handleSelectPerm (payload) {
        this.active = payload.value;
        this.$emit('on-select-tab', payload);
      },

      handleSearchSystem () {
        this.emptyPermData.tipType = 'search';
        this.permList = this.permListBack.filter(
          (item) =>
            item.name.indexOf(this.systemValue) > -1
            || item.id.toLowerCase().indexOf(this.systemValue.toLowerCase()) > -1
        );
        if (!this.permList.length) {
          this.emptyPermData = formatCodeData(0, this.emptyPermData);
        }
      },

      async handleEmptyRefresh () {
        await this.fetchSystems();
      }
    }
  };
</script>
  
<style lang="postcss" scoped>
.my-perm-left-layout {
  position: relative;
  &-all {
    margin: 16px 16px 8px 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #dcdee5;
    .renewal-perm-content {
      padding: 8px;
      cursor: pointer;
      .renewal-perm-label {
        display: flex;
        align-items: center;
        .name {
          font-size: 13px;
        }
        .icon {
          font-size: 14px;
          margin-right: 8px;
        }
      }
      .renewal-perm-total {
        background-color: #eaebf0;
        color: #979ba5;
        font-size: 12px;
        border-radius: 2px;
        padding: 0 8px;
      }
    }
    &.is-active {
      .renewal-perm-content {
        background-color: #e1ecff;
        color: #3a84ff;
        .renewal-perm-total {
          background-color: #a3c5fd;
          color: #ffffff;
        }
      }
    }
  }
  &-border {
    width: 100%;
    height: 1px;
    background-color: #dcdee5;
    margin-top: 8px;
  }
  &-content {
    position: relative;
    overflow-y: auto;
    &::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    /*滚动条里面的小方块*/
    &::-webkit-scrollbar-thumb {
      background: #dcdee5;
      border-radius: 3px;
    }
    &::-webkit-scrollbar-track {
      background: transparent;
      border-radius: 3px;
    }
    .my-perm-left-layout-item {
      padding: 8px;
      margin: 0 16px 7px 16px;
      border-radius: 4px;
      cursor: pointer;
      .perm-type-content {
        display: flex;
        align-items: center;
        font-size: 13px;
        color: #63656e;
        .perm-type-name {
          display: flex;
          align-items: center;
          word-break: break-all;
          .folder-icon {
            font-size: 14px;
            color: #c4c6cc;
            margin-right: 8px;
            &-active {
              color: #3a84ff;
            }
          }
          .name {
            max-width: 135px;
          }
        }
      }
      .perm-type-count {
        background-color: #eaebf0;
        color: #979ba5;
        font-size: 12px;
        padding: 0 7px;
        border-radius: 2px;
      }
      &-active {
        background-color: #e1ecff;
        .perm-type-content {
          .perm-type-name {
            color: #3a84ff;
            .folder-icon {
              color: #3a84ff;
            }
          }
        }
        .perm-type-count {
          background-color: #a3c5fd;
          color: #ffffff;
        }
      }
    }
    .system-empty-wrapper {
      margin-top: 100px;
    }
  }
}
</style>

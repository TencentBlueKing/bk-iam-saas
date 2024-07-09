<template>
  <div class="my-perm-left-layout">
    <div class="flex-between my-perm-left-layout-all">
      <div class="renewal-perm-label">
        <div>
          <Icon
            type="file-close"
            class="icon"
          />
        </div>
        <div class="name">
          {{ $t(`m.perm['可续期']`) }}
        </div>
      </div>
      <div class="renewal-perm-total">{{ renewalTotal }}</div>
    </div>
    <div class="my-perm-left-layout-content">
      <template>
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
                type="file-close"
                class="folder-icon"
              />
              <div class="label single-hide">
                {{ item.label }}
              </div>
            </div>
          </div>
          <div class="perm-type-count">{{ item.count || 0 }}</div>
        </div>
      </template>
    </div>
  </div>
</template>
  
<script>
  // import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData } from '@/common/util';
  export default {
    data () {
      return {
        active: 'all',
        renewalTotal: 0,
        permList: [
          {
            label: this.$t(`m.perm['全部权限']`),
            value: 'all',
            icon: '',
            count: 0
          },
          {
            label: this.$t(`m.userOrOrg['个人用户组权限']`),
            value: 'personalPerm',
            icon: '',
            count: 0
          },
          {
            label: this.$t(`m.userOrOrg['组织用户组权限']`),
            value: 'departPerm',
            icon: '',
            count: 0
          },
          {
            label: this.$t(`m.userOrOrg['人员模板用户组权限']`),
            value: 'memberTempPerm',
            icon: '',
            count: 0
          },
          {
            label: this.$t(`m.perm['自定义权限']`),
            value: 'customPerm',
            count: 0
          },
          {
            label: this.$t(`m.perm['管理员权限']`),
            value: 'managerPerm',
            count: 0
          }
        ],
        permListBack: [],
        emptyPermData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemId', 'user'])
    },
    methods: {
      async fetchPageData () {
        // await this.fetchSystems();
      },

      // async fetchSystems () {
      //   this.systemLoading = true;
      //   try {
      //     const params = {};
      //     if (this.externalSystemId) {
      //       params.hidden = false;
      //     }
      //     const { code, data } = await this.$store.dispatch('system/getSystems', params);
      //     let list = [...data];
      //     if (data && data.length) {
      //       const { role } = this.user;
      //       if (['system_manager'].includes(role.type) && role.code) {
      //         list = data.filter((item) => item.id === role.code);
      //       }
      //       this.permList = await this.getSystemCount(list);
      //       this.permListBack = [...this.permList];
      //     }
      //     this.emptyPermData = formatCodeData(
      //       code,
      //       this.emptyPermData,
      //       list.length === 0
      //     );
      //   } catch (e) {
      //     this.emptyPermData = formatCodeData(e.code, this.emptyPermData);
      //     this.messageAdvancedError(e);
      //   } finally {
      //     this.systemLoading = false;
      //   }
      // },

      // // 根据系统id查找对应系统的敏感等级
      // async getSystemCount (payload) {
      //   const list = [...payload];
      //   try {
      //     for (let i = 0; i < list.length; i++) {
      //       this.$store
      //         .dispatch('sensitivityLevel/getSensitivityLevelCount', {
      //           system_id: list[i].id
      //         })
      //         .then(({ data }) => {
      //           // const curSystemId = list[i].id;
      //           // if (systemCountMockData[curSystemId]) {
      //           //   const { data } = systemCountMockData[curSystemId];
      //           this.$set(list[i], 'levelItem', data);
      //           this.$set(list[i], 'count', data.all || 0);
      //           if (i === 0) {
      //             const params = {
      //             ...list[i],
      //             ...{
      //               isFirst: true
      //             }
      //             };
      //             this.handleSelectPerm(params);
      //           }
      //         });
      //     }
      //   // }
      //   } catch (e) {
      //     this.messageAdvancedError(e);
      //   }
      //   return list;
      // },

      async handleSelectPerm (payload) {
        const { value } = payload;
        this.active = value;
        // const list = [];
        // const params = {
        // ...levelItem
        // };
        // if (isFirst) {
        //   this.$set(params, 'isFirst', isFirst);
        //   this.$emit('on-select-system', payload);
        bus.$emit('on-systems-level-count');
        // } else {
        //   list = await this.getSystemCount([payload]);
        //   this.$set(params, 'isFirst', isFirst);
        //   this.$emit('on-select-system', list[0]);
        //   bus.$emit('on-systems-level-count', list[0].levelItem);
        // }
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
    padding: 16px 0;
    margin: 0 24px;
    margin-bottom: 8px;
    border-bottom: 1px solid #dcdee5;
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
    &-active {
      background-color: #e1ecff;
      color: #3a84ff;
      .renewal-perm-total {
        background-color: #a3c5fd;
        color: #ffffff;
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

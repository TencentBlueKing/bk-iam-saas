<template>
  <div class="all-custom-perm">
    <!-- <div
        :class="[
          'all-custom-perm-all',
          { 'all-custom-perm-all-active': active === 'all' }
        ]"
        @click.stop="handleSelectPerm({ id: 'all', isFirst: false })"
      > -->
    <!-- <div :class="['all-custom-perm-all', { 'all-custom-perm-all-active': active === 'all' }]">
        <div class="system-all-text">
          <div class="system-all-text-name">
            {{ $t(`m.sensitivityLevel['全部系统']`) }}
          </div>
        </div>
        <div class="system-all-total">{{ systemTotal }}</div>
      </div> -->
    <div
      class="all-custom-perm-content"
      :style="formatSystemsHeight"
      v-bkloading="{
        isLoading: systemLoading,
        opacity: 1,
        color: '#f5f6fa'
      }"
    >
      <template>
        <div
          v-for="item in permList"
          :key="item.id"
          :class="[
            'all-custom-perm-item',
            { 'all-custom-perm-item-active': item.id === active }
          ]"
          @click.stop="handleSelectPerm(item)"
        >
          <div class="sensitivity-system-name">
            <div
              :style="{ width: `${getDragWidth() - 50}px` }"
              class="sensitivity-system-name-left"
            >
              <Icon
                type="file-close"
                :class="['folder-icon', { 'folder-icon-active': item.id === active }]"
              />
              <div class="single-hide">
                {{ item.name }}
              </div>
            </div>
          </div>
          <div class="sensitivity-system-count">{{ item.count || 0 }}</div>
        </div>
      </template>
    </div>
  </div>
</template>
  
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  export default {
    inject: {
      getDragWidth: { value: 'getDragWidth', default: 280 }
    },
    data () {
      return {
        active: '',
        systemLoading: false,
        systemTotal: 0,
        systemValue: '',
        permList: [],
        permListBack: [],
        allSystemData: {
          all: 0,
          L1: 0,
          L2: 0,
          L3: 0,
          L4: 0,
          L5: 0
        },
        emptySystemData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
    ...mapGetters(['externalSystemId', 'user']),
    formatSystemsHeight () {
      return {
        maxHeight: `${getWindowHeight() - 185}px`
      };
    }
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
      //     this.emptySystemData = formatCodeData(
      //       code,
      //       this.emptySystemData,
      //       list.length === 0
      //     );
      //   } catch (e) {
      //     this.emptySystemData = formatCodeData(e.code, this.emptySystemData);
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
        const { id, levelItem, isFirst } = payload;
        this.active = id;
        let list = [];
        const params = {
        ...levelItem
        };
        if (isFirst) {
          this.$set(params, 'isFirst', isFirst);
          this.$emit('on-select-system', payload);
          bus.$emit('on-systems-level-count', params);
        } else {
          list = await this.getSystemCount([payload]);
          this.$set(params, 'isFirst', isFirst);
          this.$emit('on-select-system', list[0]);
          bus.$emit('on-systems-level-count', list[0].levelItem);
        }
      },

      handleSearchSystem () {
        this.emptySystemData.tipType = 'search';
        this.permList = this.permListBack.filter(
          (item) =>
            item.name.indexOf(this.systemValue) > -1
            || item.id.toLowerCase().indexOf(this.systemValue.toLowerCase()) > -1
        );
        if (!this.permList.length) {
          this.emptySystemData = formatCodeData(0, this.emptySystemData);
        }
      },

      handleClearSystem () {
        this.systemValue = '';
        this.emptySystemData.tipType = '';
        this.permList = _.cloneDeep(this.permListBack);
      },

      async handleEmptyRefresh () {
        await this.fetchSystems();
      }
    }
  };
</script>
  
<style lang="postcss" scoped>
.all-custom-perm {
  position: relative;
  flex-basis: 280px;
  .all-custom-perm-all {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    cursor: pointer;
    .system-all-text {
      display: flex;
      font-size: 13px;
      /* &-name {
        margin-left: 5px;
      } */
    }
    .system-all-total {
      background-color: #eaebf0;
      color: #979ba5;
      font-size: 12px;
      border-radius: 2px;
      padding: 0 7px;
    }
    &-active {
      background-color: #e1ecff;
      color: #3a84ff;
      .system-all-total {
        background-color: #a3c5fd;
        color: #ffffff;
      }
    }
  }
  .all-custom-perm-border {
    width: 100%;
    height: 1px;
    background-color: #dcdee5;
    margin-top: 8px;
  }
  .all-custom-perm-search {
    margin-bottom: 10px;
  }
  .all-custom-perm-content {
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
    .all-custom-perm-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 5px;
      margin-bottom: 5px;
      cursor: pointer;
      .sensitivity-system-name {
        display: flex;
        align-items: center;
        font-size: 13px;
        color: #63656e;
        &-left {
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
      .sensitivity-system-count {
        background-color: #eaebf0;
        color: #979ba5;
        font-size: 12px;
        padding: 0 7px;
        border-radius: 2px;
      }
      &-active {
        background-color: #e1ecff;
        .sensitivity-system-name {
          color: #3a84ff;
        }
        .sensitivity-system-count {
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

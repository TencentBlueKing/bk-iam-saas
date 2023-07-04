<template>
  <div class="iam-transfer-group-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
    v-bkloading="{ isLoading, opacity: 1 }">
    <template v-if="!isLoading && !isEmpty">
      <div class="transfer-group-content">
        <div class="header" @click="handlesuperExpanded">
          <Icon bk class="expanded-icon" :type="superExpanded ? 'down-shape' : 'right-shape'" />
          <label class="title">{{ $t(`m.permTransfer['超级管理员权限交接']`) }}</label>
        </div>
        <div class="content" v-if="superExpanded">
          <div class="slot-content">
            <div class="member-item">
              <span class="member-name">
                {{ $t(`m.myApproval['超级管理员']`) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template v-if="!isLoading && isEmpty">
      <div class="empty-wrapper">
        <!-- <iam-svg />
                <p class="text">{{ $t(`m.common['暂无数据']`) }}</p> -->
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-refresh="handleEmptyRefresh"
        />
      </div>
    </template>
  </div>
</template>
<script>
  import { formatCodeData } from '@/common/util';
  export default {
    name: '',
    components: {
    },
    data () {
      return {
        isEmpty: false,
        isLoading: false,
        superListAll: [], // 超级管理员权限交接
        superExpanded: true,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    mounted () {
      this.fetchData();
    },
    methods: {
      async fetchData () {
        this.isLoading = true;
        try {
          const { code, data } = await this.$store.dispatch('role/getSuperManager'); // 普通用户没有获取超级管理员接口数据的权限...需要确认
          const superListAll = data || [];
          this.superListAll.splice(0, this.superListAll.length, ...superListAll);
          this.isEmpty = superListAll.length < 1;
          this.emptyData = formatCodeData(code, this.emptyData, this.isEmpty);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.isLoading = false;
        }
      },
      handleEmptyRefresh () {
        this.fetchData();
      },

      handlesuperExpanded () {
        this.superExpanded = !this.superExpanded;
      }
    }
  };
</script>
<style lang="postcss">
    @import './group.css';
</style>

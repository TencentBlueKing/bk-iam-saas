<template>
  <bk-sideslider
    :is-show.sync="isShowSideslider"
    :title="$t(`m.common['详情']`)"
    :width="640"
    ext-cls="iam-transfer-history-sideslider"
    :quick-close="true"
    @animation-end="handleAnimationEnd">
    <div slot="content" class="content-wrapper" v-bkloading="{ isLoading, opacity: 1, color: '#1a1a1a' }">
      <section v-if="!isLoading">
        <div class="detail-header">{{$t(`m.user['日志详情']`)}}</div>
        <div class="detail-content">
          <div class="detail-item" v-for="(log, index) in logList" :key="index"
            :style="{ color: log.status === 'failed' ? '#ea3636' : '#fff' }">
            <div class="time">
              [{{log.created_time}}] {{log.title}}
            </div>
            <div class="info">
              {{log.info}}
              {{log.ret}}
            </div>
          </div>
        </div>
      </section>
    </div>
  </bk-sideslider>
</template>
<script>
  export default {
    name: '',
    components: {
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      curHistory: {
        type: Object,
        default: () => ({})
      }
    },
    data () {
      return {
        tabActive: 'perm',
        isShowSideslider: false,
        isLoading: true,
        logList: []
      };
    },
    watch: {
      show: {
        async handler (value) {
          this.isShowSideslider = !!value;
          if (this.isShowSideslider) {
            await this.fetchTransferHistoryDetail();
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchTransferHistoryDetail () {
        try {
          const res = await this.$store.dispatch('perm/getTransferHistoryDetail', {
            id: this.curHistory.id
          });
          const list = res.data || [];
          list.forEach(item => {
            // 2021-12-08 06:28:15.384996+00:00
            const timeArr = item.created_time.split('.');
            item.created_time = timeArr[0];

            // item.objectDetail = JSON.parse(item.object_detail)
            item.objectDetail = item.object_detail;
            if (item.object_type === 'group_ids') {
              item.title = this.$t(`m.permTransfer['用户组权限交接：']`);
              item.info = item.objectDetail.name;
            } else if (item.object_type === 'custom_policies') {
              item.title = this.$t(`m.permTransfer['自定义权限交接：']`);
              item.info = `[${this.$t(`m.common['系统']`)}:${item.objectDetail.name}]`;
              // + `[${this.$t(`m.common['操作']`)}:${item.objectDetail.policy_info.name}]`
            } else if (item.object_type === 'role_ids') {
              if (item.objectDetail.type === 'super_manager') {
                item.title = this.$t(`m.permTransfer['超级管理员交接：']`);
                item.info = '';
              } else if (item.objectDetail.type === 'system_manager') {
                item.title = this.$t(`m.permTransfer['系统管理员交接：']`);
                item.info = item.objectDetail.name;
              } else if (item.objectDetail.type === 'rating_manager') {
                item.title = this.$t(`m.permTransfer['分级管理员交接：']`);
                item.info = item.objectDetail.name;
              }
            } else {
              item.title = '--';
            }

            if ((item.status || '').toLowerCase() === 'succeed') {
              item.ret = this.$t(`m.user['成功']`);
            }
            if ((item.status || '').toLowerCase() === 'failed') {
              item.ret = this.$t(`m.user['失败']`);
            }
            if ((item.status || '').toLowerCase() === 'running') {
              item.ret = this.$t(`m.permTransfer['交接中']`);
            }
          });
          this.logList.splice(0, this.logList.length, ...list);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      handleAnimationEnd () {
        this.$emit('animation-end');
        this.isLoading = true;
        this.curHistory = null;
      }
    }
  };
</script>
<style lang="postcss">
    @import './history-detail.css';
</style>

<template>
  <div class="iam-apply-group-detail-wrapper" v-bkloading="{ isLoading, opacity: 1, zIndex: 1000 }">
    <template v-if="isShowPage">
      <basic-info :data="basicInfo" :is-show-expired="isShowExpired" />
      <render-group-table :data="tableList" :count="count" />
      <render-process :link="basicInfo.ticket_url" />
      <div class="action" v-if="isShowAction">
        <bk-button :loading="loading" @click="handleCancel">{{ $t(`m.common['撤销']`) }}</bk-button>
      </div>
    </template>
  </div>
</template>
<script>
  import BasicInfo from './basic-info';
  import RenderGroupTable from './apply-group-table';
  import RenderProcess from '../common/render-process';
  import { mapGetters } from 'vuex';
  export default {
    name: '',
    components: {
      BasicInfo,
      RenderGroupTable,
      RenderProcess
    },
    props: {
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      loading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        basicInfo: {},
        initRequestQueue: ['detail'],
        status: '',
        tableList: [],
        count: 0
      };
    },
    computed: {
            ...mapGetters(['externalSystemId']),
            isLoading () {
                return this.initRequestQueue.length > 0;
            },
            isShowAction () {
                return this.status === 'pending';
            },
            isShowPage () {
                return !this.isLoading;
            },
            isShowExpired () {
                return this.basicInfo.type === 'join_group';
            }
    },
    watch: {
      params: {
        handler (value) {
          if (Object.keys(value).length > 0) {
            this.initRequestQueue = ['detail'];
            this.fetchData(value.id);
          } else {
            this.initRequestQueue = [];
            this.status = '';
            this.basicInfo = {};
            this.tableList = [];
            this.count = 0;
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchData (id) {
        try {
          const params = {
            id
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const res = await this.$store.dispatch('myApply/getApplyDetail', params);
          const {
            sn, type, applicant, organizations, reason, data,
            status, created_time, ticket_url
          } = res.data;
          this.basicInfo = {
            sn,
            type,
            organizations,
            applicant,
            reason,
            expiredDisplay: data.expired_display,
            created_time,
            ticket_url,
            applicants: data.applicants || []
          }
          ;(data.groups || []).forEach(item => {
            item.display_id = `#${item.id}`;
          });
          this.tableList = [...data.groups];
          this.count = data.groups.length;
          this.status = status;
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.initRequestQueue.shift();
        }
      },

      handleCancel () {
        this.$emit('on-cancel');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-apply-group-detail-wrapper {
        /* height: calc(100vh - 121px); */
        .action {
            padding-bottom: 50px;
        }
    }
</style>

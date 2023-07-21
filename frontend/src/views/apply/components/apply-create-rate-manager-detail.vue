<template>
  <div class="iam-apply-create-rate-manager-detail-wrapper" v-bkloading="{ isLoading, opacity: 1, zIndex: 1000 }">
    <template v-if="isShowPage">
      <basic-info :data="basicInfo" />
      <p class="rate-manager-info">
        <span class="name">{{ name }}</span>
        <span class="text">({{ $t(`m.nav['管理空间']`) }})</span>
      </p>
      <render-perm
        v-for="(item, index) in authorizationScopes"
        :key="index"
        :title="item.system.name"
        :expanded.sync="item.expanded"
        :perm-length="item.list.length"
        :ext-cls="index !== 0 ? 'set-maring-top' : ''">
        <perm-table
          :data="item.list" />
      </render-perm>
      <render-vertical-block
        :label="$t(`m.myApply['可授权人员范围']`)"
        ext-cls="apply-title">
        <render-member-item :data="users" v-if="isHasUser" mode="view" />
        <render-member-item :data="departments" type="department" mode="view" v-if="isHasDepartment" />
        <div style="margin-top: 9px;" v-if="!isHasUser && !isHasDepartment">
          <div class="all-item">
            <span class="member-name">{{ $t(`m.common['全员']`) }}</span>
            <span class="display-name">(All)</span>
          </div>
        </div>
      </render-vertical-block>
      <render-process :link="basicInfo.ticket_url" />
      <div class="action" v-if="isShowAction">
        <bk-button :loading="loading" @click="handleCancel">{{ $t(`m.common['撤销']`) }}</bk-button>
      </div>
    </template>
    <template v-if="isEmpty">
      <div class="apply-content-empty-wrapper">
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
  import _ from 'lodash';
  import RenderPerm from '@/components/render-perm';
  import BasicInfo from './basic-info';
  import PermTable from './rate-manager-perm-table';
  import PermPolicy from '@/model/my-perm-policy';
  import RenderProcess from '../common/render-process';
  import RenderMemberItem from '../common/render-member-display';
  import { formatCodeData } from '@/common/util';
  import { mapGetters } from 'vuex';
  export default {
    name: '',
    components: {
      RenderPerm,
      BasicInfo,
      PermTable,
      RenderProcess,
      RenderMemberItem
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
        systemName: '',
        systemId: '',
        status: '',
        authorizationScopes: [],
        name: '',
        users: [],
        departments: [],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
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
                return !this.isLoading && this.authorizationScopes.length > 0;
            },
            isEmpty () {
                return !this.isLoading && this.authorizationScopes.length < 1;
            },
            isHasUser () {
                return this.users.length > 0;
            },
            isHasDepartment () {
                return this.departments.length > 0;
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
            this.authorizationScopes = [];
            this.name = '';
            this.users = [];
            this.departments = [];
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchData (id) {
        const params = {
          id
        };
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
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
            created_time,
            ticket_url,
            applicants: data.applicants || []
          };
          this.status = status;
          this.name = data.name;
          data.authorization_scopes.forEach((item, index) => {
            item.list = item.actions.map(subItem => new PermPolicy(subItem)); // 添加属性（此处会关联多个js文件，继承很多属性，暂时不清楚目的）
            this.$set(item, 'expanded', index === 0); // 默认第一项展开
          });
          this.authorizationScopes = _.cloneDeep(data.authorization_scopes);
          this.users = data.subject_scopes.filter(item => item.type === 'user');
          this.departments = data.subject_scopes.filter(item => item.type === 'department');
          this.emptyData = formatCodeData(res.code, this.emptyData, this.authorizationScopes.length === 0);
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
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
<style lang="postcss">
    .iam-apply-create-rate-manager-detail-wrapper {
        /* height: calc(100vh - 121px); */
        .action {
            padding-bottom: 50px;
        }
        .rate-manager-info {
            line-height: 50px;
            font-size: 14px;
            color: #63656e;
            .name {
                font-weight: 600;
            }
            .text {
                color: #c4c6cc;
            }
        }
        .set-maring-top {
            margin-top: 16px;
        }
        .apply-title {
            margin-top: 20px;
            padding: 20px 30px;
            .label {
                margin-bottom: 15px;
                font-size: 14px !important;
                color: #63656e;
                font-weight: bold;
            }
        }
        .apply-content-empty-wrapper {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            img {
                width: 120px;
            }
        }
        .all-item {
            position: relative;
            display: inline-block;
            margin: 0 6px 6px 10px;
            padding: 0 10px;
            line-height: 22px;
            background: #f5f6fa;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            font-size: 12px;
            .member-name {
                display: inline-block;
                max-width: 200px;
                line-height: 17px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: text-top;
            }
            .display-name {
                display: inline-block;
                vertical-align: top;
            }
        }
    }
</style>

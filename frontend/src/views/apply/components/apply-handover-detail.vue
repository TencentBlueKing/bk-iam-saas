<template>
  <div
    v-bkloading="{ isLoading, opacity: 1, zIndex: 1000 }"
    class="iam-apply-handover-detail-wrapper"
  >
    <template v-if="isShowPage">
      <div
        v-if="warningList.length"
        class="handover-detail-warning"
      >
        <bk-alert type="warning">
          <template #title>
            <div
              v-for="(item, index) of warningList"
              :key="index"
              class="warning-item"
            >
              {{ item }}
            </div>
          </template>
        </bk-alert>
      </div>
      <BasicInfo :data="basicInfo" :reason-label="`${$t(`m.myApply['交接理由']`)}${$t(`m.common['：']`)}`">
        <div class="item">
          <label class="label">{{ $t(`m.myApply['交出人']`) }}{{$t(`m.common['：']`)}}</label>
          <div class="content">{{ basicInfo.handover_from }}</div>
        </div>
        <div class="item">
          <label class="label">{{ $t(`m.myApply['接收人']`) }}{{$t(`m.common['：']`)}}</label>
          <div class="content">{{ basicInfo.handover_to }}</div>
        </div>
      </BasicInfo>

      <!-- 用户组权限 -->
      <template v-if="groupList.length">
        <div class="handover-content-info">
          <span class="name">{{ $t('m.perm.用户组权限') }}</span>
        </div>
        <GroupTable
          :data="groupList"
          :count="groupList.length"
          :apply-type="'group_handover'"
          :is-show-role-name="true"
          :is-show-sensitivity-level="true"
          :is-show-expired="true"
        />
      </template>

      <!-- 自定义权限 -->
      <template v-if="policyList.length">
        <div class="handover-content-info">
          <span class="name">{{ $t('m.approvalProcess.自定义权限') }}</span>
        </div>
        <RenderPerm
          v-for="policy of policyList"
          :key="policy.system.id"
          :title="policy.system.name"
          :expanded.sync="policy.expanded"
          :perm-length="policy.list.length"
          ext-cls="mt-16"
        >
          <PermTable
            :data="policy.list"
            :is-show-sensitivity-level="true"
            :is-show-expired="true"
          />
        </RenderPerm>
      </template>

      <!-- 管理员身份 -->
      <template v-if="rolesList.length">
        <div class="handover-content-info">
          <span class="name">{{ $t('m.myApply.管理员身份') }}</span>
        </div>
        <RolesTable
          :count="rolesList.length"
          :list="rolesList"
        />
      </template>

      <RenderProcess :link="basicInfo.ticket_url" />

      <div class="action" v-if="isShowAction">
        <bk-button :loading="loading" @click="handleCancel">
          {{ $t('m.common.撤销') }}
        </bk-button>
      </div>
    </template>

    <div
      v-if="isEmpty"
      class="apply-content-empty-wrapper"
    >
      <ExceptionEmpty
        v-bind="emptyData"
        @on-refresh="handleEmptyRefresh"
      />
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { formatCodeData } from '@/common/util';
  import PermPolicy from '@/model/my-perm-policy';
  import RenderPerm from '@/components/render-perm';
  import RenderProcess from '../common/render-process';
  import BasicInfo from './basic-info';
  import GroupTable from './apply-group-table';
  import PermTable from './rate-manager-perm-table';
  import RolesTable from './apply-roles-table';

  export default {
    name: 'IamApplyHandoverDetail',
    components: {
      BasicInfo,
      GroupTable,
      PermTable,
      RolesTable,
      RenderPerm,
      RenderProcess
    },
    props: {
      params: {
        type: Object,
        default: () => ({})
      },
      loading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        initRequestQueue: ['detail'],
        groupList: [],
        policyList: [],
        rolesList: [],
        warningList: [],
        basicInfo: {},
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
      // 加载状态：队列存在即加载中
      isLoading () {
        return this.initRequestQueue.length > 0;
      },
      // 展示主内容：非加载 + 有权限数据
      isShowPage () {
        return !this.isLoading
          && (this.policyList.length > 0 || this.groupList.length > 0 || this.rolesList.length > 0);
      },
      // 空状态：非加载 + 无权限数据
      isEmpty () {
        return !this.isLoading && !this.policyList.length && !this.groupList.length && !this.rolesList.length;
      },
      // 显示撤销按钮：待审批状态
      isShowAction () {
        return this.basicInfo.status === 'pending';
      }
    },
    watch: {
      params: {
        handler (newVal) {
          // 无参数清空页面状态
          if (!Object.keys(newVal).length) {
            this.resetPageData();
            return;
          }
          // 有参数重新拉取详情
          this.initRequestQueue = ['detail'];
          this.fetchData(newVal.id);
        },
        immediate: true
      }
    },
    methods: {
      /** 拉取交接申请详情 */
      async fetchData (id) {
        const reqParams = { id };
        
        if (this.externalSystemId) {
          reqParams.hidden = false;
        }

        try {
          const res = await this.$store.dispatch('myApply/getApplyDetail', reqParams);
          const {
            data = {},
            sn,
            type,
            reason,
            status,
            applicant,
            organizations,
            created_time,
            ticket_url
          } = res.data || {};

          const {
            handover_from,
            handover_to,
            applicants = [],
            warnings = [],
            // eslint-disable-next-line camelcase
            custom_policies = [],
            groups = [],
            roles = []
          } = data;

          // 基础信息
          this.basicInfo = {
            sn,
            type,
            status,
            organizations,
            applicant,
            reason,
            created_time,
            ticket_url,
            handover_from,
            handover_to,
            applicants
          };
          this.warningList = warnings;
          // 用户组列表和管理员列表
          this.groupList = groups;
          this.rolesList = roles;
          // eslint-disable-next-line camelcase
          const policyList = custom_policies;
          policyList.forEach((item, index) => {
            item.list = item.actions.map(action => new PermPolicy(action));
            // 权限列表默认展开第一条
            item.expanded = index === 0;
          });
          this.policyList = policyList;
          // 处理空状态文案
          this.emptyData = formatCodeData(res.code, this.emptyData, !policyList.length);
        } catch (e) {
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          // 移除加载标记
          this.initRequestQueue.shift();
        }
      },

      /** 撤销申请 */
      handleCancel () {
        this.$emit('on-cancel');
      },

      /** 空状态刷新 */
      handleEmptyRefresh () {
        this.initRequestQueue = ['detail'];
        this.fetchData(this.params.id);
      },

      /** 重置页面所有数据 */
      resetPageData () {
        this.policyList = [];
        this.rolesList = [];
        this.initRequestQueue = [];
        this.basicInfo = {};
        this.emptyData = {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        };
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-apply-handover-detail-wrapper {
  position: relative;
  box-sizing: border-box;

  .handover-detail-warning {
    margin-bottom: 16px;

   .warning-item {
     word-break: break-all;

      &:not(&:last-of-type) {
        margin-bottom: 8px;
      }
   }
  }

  .handover-content-info {
    margin-top: 24px;
    font-size: 14px;
    color: #63656e;

    .name {
      font-weight: 600;
    }

    .text {
      color: #c4c6cc;
    }
  }

  .mt-16 {
    margin-top: 16px;
  }

  .action {
    padding-bottom: 50px;
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
    display: inline-block;
    margin: 0 6px 6px 10px;
    padding: 0 10px;
    line-height: 22px;
    background-color: #f5f6fa;
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
    }
  }
}
</style>

<template>
  <div
    :class="[
      'iam-apply-basic-info-wrapper',
      { 'is-en-large': !curLanguageIsCn && isShowExpired },
      { 'is-en-middle': !curLanguageIsCn && !isShowExpired }
    ]"
  >
    <div class="title">{{ $t(`m.common['基本信息']`) }}</div>
    <div class="item">
      <label class="label">{{ $t(`m.myApply['申请单号']`) }}{{$t(`m.common['：']`) }}</label>
      <div class="content">{{ data.sn }}</div>
    </div>
    <div class="item">
      <label class="label">{{ $t(`m.myApply['申请类型']`) }}{{$t(`m.common['：']`) }}</label>
      <div class="content">{{ getApplyTypeDisplay(data.type) }}</div>
    </div>
    <div class="item">
      <label class="label">{{ $t(`m.myApply['申请人']`) }}{{$t(`m.common['：']`)}}</label>
      <div class="content">{{ data.applicant }}</div>
    </div>
    <div class="item" v-if="isShowPermManager">
      <label class="label">{{ $t(`m.myApply['权限获得者']`) }}{{$t(`m.common['：']`) }}</label>
      <div class="content">
        {{
          data.applicants && data.applicants.length > 0
            ? data.applicants.map((item) => ['user'].includes(item.type) ?
              `${item.id}(${item.display_name})`
              : item.display_name).join(';') : ''
        }}
      </div>
    </div>
    <div class="item" v-if="isShowExpired">
      <label class="label">{{ $t(`m.common['申请期限']`) }}{{$t(`m.common['：']`) }}</label>
      <div class="content">{{ data.expiredDisplay }}</div>
    </div>
    <div class="item">
      <label class="label">{{ $t(`m.myApply['申请时间']`) }}{{$t(`m.common['：']`) }}</label>
      <div class="content">{{ data.created_time }}</div>
    </div>
    <div class="item">
      <label class="label">{{ $t(`m.myApply['所在组织']`) }}{{$t(`m.common['：']`)}}</label>
      <div class="content">
        <template v-if="isHasOrg">
          <p v-for="(org, orgIndex) in data.organizations" :key="orgIndex">
            {{ org.full_name }}
          </p>
        </template>
        <template v-else>--</template>
      </div>
    </div>
    <slot />
    <div class="item">
      <label class="label">{{ reasonLabel }}</label>
      <div class="content" :title="Boolean(data.reason) ? data.reason : ''">
        {{ data.reason || '--' }}
      </div>
    </div>
  </div>
</template>

<script>
  import il8n from '@/language';
  export default {
    props: {
      data: {
        type: Object,
        default: () => {
          return {};
        }
      },
      isShowExpired: {
        type: Boolean,
        default: false
      },
      reasonLabel: {
        type: String,
        default: `${il8n('common', '理由')}${il8n('common', '：')}`
      }
    },
    computed: {
      isHasOrg () {
        return this.data.organizations && this.data.organizations.length > 0;
      },
      isShowPermManager () {
        return !['handover', 'create_rating_manager', 'update_rating_manager'].includes(this.data.type);
      }
    },
    methods: {
      /**
       * getApplyTypeDisplay
       */
      getApplyTypeDisplay (payload) {
        let str = '';
        const { source } = this.$route.query;
        switch (payload) {
          case 'grant_action':
            str = this.$t(`m.myApply['自定义权限申请']`);
            break;
          case 'grant_temporary_action':
            str = this.$t(`m.myApply['自定义临时权限申请']`);
            break;
          case 'renew_action':
            str = this.$t(`m.renewal['权限续期']`);
            break;
          case 'join_group':
            str = this.$t(`m.myApply['加入用户组']`);
            break;
          case 'renew_group':
            str = this.$t(`m.myApply['用户组续期']`);
            break;
          case 'handover':
            str = this.$t(`m.permTransfer['权限交接']`);
            break;
          case 'create_rating_manager':
            str = this.$t(source && source === 'externalApp' ? `m.myApply['创建项目']` : `m.myApply['创建管理空间']`);
            break;
          case 'update_rating_manager':
            str = this.$t(source && source === 'externalApp' ? `m.myApply['编辑项目']` : `m.myApply['编辑管理空间']`);
            break;
          default:
            str = '';
        }

        return str;
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import './basic-info.css';
</style>

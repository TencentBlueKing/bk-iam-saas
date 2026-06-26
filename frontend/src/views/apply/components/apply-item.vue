<template>
  <div :class="['item', { 'has-bottom-border': hasBottomBorder }, { 'is-active': isActive }]"
    @click.stop="handleClick">
    <div class="up-info">
      <span class="title" :title="getApplyTitle(data)">{{ getApplyTitle(data) }}</span>
      <div class="status">
        <template v-if="curLanguageIsCn">
          <iam-svg name="icon-apply-current" v-if="data.status === 'pending'" />
          <iam-svg name="icon-apply-reject" v-if="data.status === 'reject'" />
          <iam-svg name="icon-apply-pass" v-if="data.status === 'pass'" />
          <iam-svg name="icon-apply-revoke" v-if="data.status === 'cancelled'" />
        </template>
        <template v-else>
          <iam-svg name="icon-apply-current-en" v-if="data.status === 'pending'" />
          <iam-svg name="icon-approve-reject-en" v-if="data.status === 'reject'" />
          <iam-svg name="icon-apply-pass-en" v-if="data.status === 'pass'" />
          <iam-svg name="icon-apply-revoke-en" v-if="data.status === 'cancelled'" />
        </template>
      </div>
    </div>
    <div class="down-info">
      <section>
        <label class="label">{{ fieldMap.field }}</label>
        <span class="value" :title="data[fieldMap.value]">{{ data[fieldMap.value] || '--' }}</span>
      </section>
      <section>
        {{ getComputedCreateTime(data.created_time) }}
      </section>
    </div>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      data: {
        type: Object,
        default: () => {
          return {};
        }
      },
      active: {
        type: Number,
        required: true
      },
      hasBottomBorder: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        fieldMap: { field: `${this.$t(`m.common['理由']`)}：`, value: 'reason' }
      };
    },
    computed: {
      /**
       * isActive
       */
      isActive () {
        return this.active === this.data.id;
      }
    },
    methods: {
      /**
       * handleClick
       */
      handleClick () {
        this.$emit('on-change', this.data);
      },

      /**
       * getApplyTitle
       */
      getApplyTitle (data) {
        const { source } = this.$route.query;
        let str = '';
        switch (data.type) {
          case 'grant_action':
            str = this.curLanguageIsCn ? `${data.extra_info.system_name}权限申请` : `Apply for ${data.extra_info.system_name} permissions`;
            break;
          case 'grant_temporary_action':
            str = this.curLanguageIsCn ? `${data.extra_info.system_name}临时权限申请` : `Temporary Apply for ${data.extra_info.system_name} permissions`;
            break;
          case 'renew_action':
            str = this.curLanguageIsCn ? `${data.extra_info.system_name}权限续期` : `Renewal for ${data.extra_info.system_name} permissions`;
            break;
          case 'join_group':
            str = `${this.$t(`m.myApply['申请加入']`)} ${data.extra_info.group_count} ${this.$t(`m.common['个用户组#']`)}`;
            break;
          case 'renew_group':
            str = `${this.$t(`m.info['申请续期']`)} ${data.extra_info.group_count} ${this.$t(`m.common['个用户组#']`)}`;
            break;
          case 'create_rating_manager':
            str = this.$t(source && source === 'externalApp' ? `m.myApply['申请创建项目']` : `m.info['申请创建管理空间']`);
            break;
          case 'update_rating_manager':
            str = this.$t(source && source === 'externalApp' ? `m.myApply['申请编辑项目']` : `m.info['申请编辑管理空间']`);
            break;
          default:
            str = '';
        }
        return str;
      },

      /**
       * getComputedCreateTime
       */
      getComputedCreateTime (payload) {
        if (payload === '') {
          return '--';
        }
        const date = payload.split(' ')[0];
        const time = date.split('-');
        return `${time[1]}-${time[2]}`;
      }
    }
  };
</script>
<style lang="postcss" scoped>
    @import './apply-item.css';
</style>

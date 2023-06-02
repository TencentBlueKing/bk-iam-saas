<template>
  <div class="iam-audit-status-item">
    <div v-if="status === 'Running'" class="refresh-icon">
      <Icon type="refresh" />
    </div>
    <span v-else :class="['status-circle', { success: isSuccess }]"></span>
    <bk-popover placement="top" ext-cls="iam-tooltips-cls" v-if="status === 'Failed'">
      {{ statusMap[status] }}
      <div slot="content">
        同步操作失败，请在用户管理后台API日志中查询详情
      </div>
    </bk-popover>
    <span v-else>
      {{ statusMap[status] }}
    </span>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      status: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        statusMap: {
          'Succeed': this.$t(`m.user['成功']`),
          'Failed': this.$t(`m.user['失败']`),
          'Running': this.$t(`m.user['同步中']`)
        }
      };
    },
    computed: {
      isSuccess () {
        return this.status === 'Succeed';
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-audit-status-item {
        .status-circle {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #fd9c9c;
            border: 1px solid #ea3636;
            border-radius: 50%;
            &.success {
                background: #7de2b8;
                border-color: #10c178;
            }
        }
        .refresh-icon{
            display: inline-block;
            color: #3a84ff;
            transform: rotate(360deg);
            animation: rotation 1.5s linear infinite;
        }
        @keyframes rotation {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    }
</style>

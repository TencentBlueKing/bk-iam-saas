<template>
  <div class="iam-audit-status-item">
    <span :class="['status-circle', { success: isSuccess }]"></span>
    {{ statusMap[status] }}
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      status: {
        type: Number,
        default: 0
      }
    },
    data () {
      return {
        statusMap: {
          0: this.$t(`m.audit['成功']`),
          1: this.$t(`m.audit['失败']`)
        }
      };
    },
    computed: {
      isSuccess () {
        return this.status === 0;
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
    }
</style>

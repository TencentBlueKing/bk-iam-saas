<template>
  <div class="iam-expire-time-wrapper" :style="{ lineHeight: `${lineHeight}` }">
    <span :class="['cur-text', status]">{{ curDisplay }}</span>
    <template v-if="ischeck">
      <Icon type="arrows-left" :style="{ lineHeight: `${lineHeight}` }" />
      <span class="after-renewal-text">{{ afterRenewalDisplay }}</span>
    </template>
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  // 过期时间的天数区间
  const EXPIRED_DISTRICT = 15;
  export default {
    name: '',
    props: {
      // 续期时间戳: 默认6个月的
      renewalTime: {
        type: Number,
        default: 15552000
      },
      curTime: {
        type: Number,
        default: 0
      },
      selected: {
        type: Boolean,
        default: false
      },
      lineHeight: {
        type: String,
        default: '32px'
      }
    },
    data () {
      return {
        ischeck: true
      };
    },
    computed: {
            ...mapGetters(['user']),
            curRestDays () {
                const dif = this.curTime - this.user.timestamp;
                if (dif < 1) {
                    return 0;
                }
                return Math.ceil(dif / (24 * 3600));
            },
            status () {
                if (!this.curRestDays) {
                    return 'yet';
                }
                if (this.curRestDays < EXPIRED_DISTRICT) {
                    return 'immediately';
                }
                return 'normal';
            },
            curDisplay () {
                if (this.status === 'yet') {
                    return this.$t(`m.common['已过期']`);
                }
                return this.$t(`m.info['天数']`, { value: this.curRestDays });
            },
            afterRenewalDisplay () {
                if (this.renewalTime === PERMANENT_TIMESTAMP) {
                    return this.$t(`m.common['永久']`);
                }
                const days = Math.floor(this.renewalTime / (24 * 60 * 60));
                if (this.status === 'yet') {
                    return this.$t(`m.info['天数']`, { value: days });
                }
                return this.$t(`m.info['天数']`, { value: days + this.curRestDays });
            }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-expire-time-wrapper {
        display: flex;
        justify-content: flex-start;
        font-size: 12px;
        .cur-text {
            &.immediately {
                color: #ff9c01;
            }
            &.yet {
                color: #c4c6cc;
            }
        }
        .after-renewal-text {
            color: #699df4;
        }
        i {
            display: inline-block;
            margin: 0 8px;
            font-size: 14px;
            color: #699df4;
            transform: rotate(180deg);
        }
    }
</style>

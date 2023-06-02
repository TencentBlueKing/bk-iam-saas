<template>
  <bk-dialog
    v-model="visible"
    width="780"
    theme="primary"
    :mask-close="false"
    header-position="left"
    ext-cls="iam-group-perm-renewal-dialog"
    :title="$t(`m.renewal['续期']`)"
    @after-leave="handleAfterLeave">
    <div class="item">
      <label :class="{ 'en': !curLanguageIsCn }">{{ curLabel }}</label>
      <span class="name">
        {{ data.name || '--' }}
        <template v-if="data.id">
          ({{ data.id }})
        </template>
      </span>
    </div>
    <div class="item">
      <label :class="{ 'en': !curLanguageIsCn }">
        {{ $t(`m.common['授权期限']`) }}<span class="required">*</span>
      </label>
      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
    </div>
    <div class="item">
      <label :class="{ 'en': !curLanguageIsCn }">{{ $t(`m.common['有效期']`) }}</label>
      <render-expire-display selected :renewal-time="expiredAt" :cur-time="curTime" />
    </div>
    <section slot="footer">
      <bk-button theme="primary" :loading="loading" @click="handleSubmit">{{ $t(`m.common['提交']`) }}</bk-button>
      <bk-button @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </section>
  </bk-dialog>
</template>
<script>
  import { mapGetters } from 'vuex';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import { PERMANENT_TIMESTAMP, ONE_DAY_TIMESTAMP } from '@/common/constants';
  import renderExpireDisplay from './display';

  export default {
    name: '',
    components: {
      IamDeadline,
      renderExpireDisplay
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      loading: {
        type: Boolean,
        default: false
      },
      data: {
        type: Object,
        default: () => {
          return {};
        }
      },
      type: {
        type: String,
        default: 'department'
      }
    },
    data () {
      return {
        visible: false,
        // 默认6个月
        expiredAt: 15552000
      };
    },
    computed: {
            ...mapGetters(['user']),
            curTime () {
                if (this.data.expired_at) {
                    return this.data.expired_at;
                }
                return 0;
            },
            curLabel () {
                if (this.type === 'department') {
                    return this.$t(`m.perm['组织名']`);
                }
                if (this.type === 'group') {
                    return this.$t(`m.userGroup['用户组名']`);
                }
                return this.$t(`m.common['成员']`);
            }
    },
    watch: {
      show: {
        handler (value) {
          this.visible = !!value;
        },
        immediate: true
      }
    },
    methods: {
      handleSubmit () {
        const getTimestamp = payload => {
          if (this.expiredAt === PERMANENT_TIMESTAMP) {
            return PERMANENT_TIMESTAMP;
          }
          if (payload < this.user.timestamp) {
            return this.user.timestamp + this.expiredAt;
          }
          return payload + this.expiredAt;
        };
        const timestamp = getTimestamp(this.curTime);
        this.$emit('on-submit', timestamp);
      },

      handleCancel () {
        this.$emit('update:show', false);
      },

      handleDeadlineChange (payload) {
        this.expiredAt = payload || ONE_DAY_TIMESTAMP;
      },

      handleAfterLeave () {
        this.expiredAt = 15552000;
        this.$emit('update:show', false);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-group-perm-renewal-dialog {
        .item {
            display: flex;
            justify-self: start;
            margin: 30px 0;
            label {
                position: relative;
                width: 60px;
                margin-right: 20px;
                line-height: 32px;
                .required {
                    position: absolute;
                    right: -7px;
                    color: #ea3636;
                }
                &.en {
                    width: 103px;
                }
            }
            .name {
                line-height: 32px;
            }
        }
    }
</style>

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
    <div class="renewal-content-wrapper">
      <template v-if="Object.keys(data).length">
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
      </template>
      <template v-else>
        <div
          v-if="selectNoRenewalList.length"
          class="no-renewal-tip"
        >
          <Icon bk type="info-circle-shape" class="warn" />
          <span class="no-renewal-name">{{ $t(`m.info['不可续期的用户组成员如下']`, { value: formatNoRenewal }) }}</span>
        </div>
        <template v-for="(item,index) in curLabelList">
          <div
            v-if="item.values.length"
            :key="index"
            class="item">
            <label :class="{ 'en': !curLanguageIsCn }">{{ item.label }}</label>
            <span class="name">
              {{ item.values.join(',') }}
            </span>
          </div>
        </template>
        <div class="item">
          <label :class="{ 'en': !curLanguageIsCn }">
            {{ $t(`m.common['授权期限']`) }}<span class="required">*</span>
          </label>
          <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
        </div>
        <div class="item item-expiration">
          <label
            :class="[
              { 'en': !curLanguageIsCn }
            ]"
          >
            {{ $t(`m.common['有效期']`) }}
          </label>
          <div>
            <div
              v-for="(item, i) in selectList"
              :key="i"
              class="item-expiration-date"
            >
              <span class="item-expiration-date-name">
                {{ item.id && item.type === 'user' ? `${item.name}(${item.id})` : item.name }}:
              </span>
              <render-expire-display selected :renewal-time="expiredAt" :cur-time="item.expired_at || 0" />
            </div>
          </div>
        </div>
      </template>
    </div>
    <section slot="footer">
      <bk-button theme="primary" :loading="loading" @click="handleSubmit">{{ $t(`m.common['提交']`) }}</bk-button>
      <bk-button @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </section>
  </bk-dialog>
</template>

<script>
  import _ from 'lodash';
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
      },
      list: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        visible: false,
        // 默认6个月
        expiredAt: 15552000,
        selectList: [],
        selectNoRenewalList: [],
        curLabelList: [],
        defaultLabelList: [
          {
            type: 'user',
            label: this.$t(`m.common['成员']`),
            values: []
          },
          {
            type: 'department',
            label: this.$t(`m.perm['组织名']`),
            values: []
          },
          {
            type: 'group',
            label: this.$t(`m.userGroup['用户组名']`),
            values: []
          }
        ]
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
      },
      formatNoRenewal () {
        return this.selectNoRenewalList.map((item) => item.id ? `${item.name}(${item.id})` : item.name);
      }
    },
    watch: {
      show: {
        handler (value) {
          this.visible = !!value;
          if (value && this.list.length) {
            const labelList = _.cloneDeep(this.defaultLabelList);
            this.selectNoRenewalList = [...this.list].filter((item) => item.expired_at === PERMANENT_TIMESTAMP);
            this.selectList = [...this.list].filter((item) => item.expired_at !== PERMANENT_TIMESTAMP);
            this.selectList.forEach((item) => {
              labelList.forEach((v) => {
                if (item.type === v.type) {
                  v.values.push(item.id ? `${item.name}(${item.id})` : item.name);
                }
              });
            });
            this.curLabelList = _.cloneDeep(labelList);
          }
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
        if (Object.keys(this.data).length) {
          const timestamp = getTimestamp(this.curTime);
          this.$emit('on-submit', timestamp, []);
        } else {
          const list = this.selectList.map((item) => {
            const { id, type, expired_at } = item;
            return {
              expired_at: getTimestamp(expired_at),
              id,
              type
            };
          });
          this.$emit('on-submit', list);
        }
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
    .renewal-content-wrapper {
      max-height: 500px;
      overflow-y: auto;
      &::-webkit-scrollbar     {
        width: 6px;
        height: 6px;
      }
      &::-webkit-scrollbar-thumb {
        background: #dcdee5;
        border-radius: 3px;
      }
      &::-webkit-scrollbar-track {
        background: transparent;
        border-radius: 3px;
      }
      .item {
        display: flex;
        justify-self: start;
        margin-bottom: 30px;
        label {
            position: relative;
            width: 60px;
            min-width: 60px;
            margin-right: 20px;
            line-height: 32px;
            .required {
              position: absolute;
              right: -7px;
              color: #ea3636;
            }
            &.en {
              width: 103px;
              min-width: 103px;
            }
        }
        .name {
          line-height: 32px;
          word-break: break-all;
        }
        &-expiration {
          .item-expiration-date {
            display: flex;
            align-items: center;
            &-name {
              max-width: 400px;
              margin-right: 10px;
              word-break: break-all;
            }
          }
        }
      }
      .no-renewal-tip {
        margin-bottom: 20px;
        .warn {
          color: #ffb848;
        }
        .no-renewal-name {
          word-break: break-all;
        }
      }
    }
  }
</style>

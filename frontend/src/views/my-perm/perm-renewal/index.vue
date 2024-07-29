<template>
  <smart-action :class="['iam-perm-renewal-wrapper', { 'iam-perm-renewal-wrapper-lang': !curLanguageIsCn }]">
    <render-horizontal-block :label="$t(`m.renewal['续期时长']`)" :required="true">
      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
    </render-horizontal-block>
    <render-horizontal-block
      ext-cls="reason-wrapper"
      :label="$t(`m.renewal['续期理由']`)"
      :required="true">
      <section ref="reasonRef">
        <bk-input
          type="textarea"
          v-model="reason"
          :maxlength="100"
          :placeholder="$t(`m.verify['请输入']`)"
          :ext-cls="isShowReasonError ? 'renewal-reason-error' : ''"
          @input="handleReasonInput"
          @blur="handleReasonBlur"
        />
        <p class="error-tips reason-error-tips" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
      </section>
    </render-horizontal-block>
    <render-horizontal-block
      :label="$t(`m.renewal['选择权限']`)"
      :required="true">
      <bk-tab
        ref="tabRef"
        ext-cls="iam-renewal-tab-cls"
        :key="tabKey"
        :active.sync="active"
        :label-height="44"
        @tab-change="handleTabChange">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index">
          <template slot="label">
            <span class="panel-name">
              <span>{{ panel.label }}</span>
              <span :style="{ 'color': active === panel.name ? '#3a84ff' : '' }">({{panel.total}})</span>
            </span>
          </template>
        </bk-tab-panel>
      </bk-tab>
      <!-- <div
        v-for="item in allPermTab"
        :key="item.id"
        :class="[
          'transfer-preview-tab',
          { 'is-active': activeTab === item.id }
        ]"
        @click.stop="handleTabChange(item)"
      >
        <div class="transfer-preview-tab-item">
          <span class="tab-name">{{ item.name }}</span>
          <span class="tab-count">{{ item.pagination.count }}</span>
        </div>
      </div> -->
      <render-table
        :renewal-time="expiredAt"
        :type="active"
        :data="getTableList"
        :count="formatCount"
        :loading="tableLoading"
        :empty-data="curEmptyData"
        @on-select="handleSelected"
        @on-change-count="handleChangeCount"
        @on-filter-system="handleFilterSystem"
      />
      <div class="transfer-footer no-fixed-footer" v-if="!isFixedFooter">
        <bk-button theme="primary" @click.stop="handleSubmit">
          <span v-bk-tooltips="{ content: $t(`m.renewal['暂无将过期的权限']`), extCls: 'iam-tooltips-cls' }">
            {{ $t(`m.common['提交']`) }}
          </span>
        </bk-button>
        <bk-button @click.stop="handleCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </render-horizontal-block>
    <p class="error-tips" v-if="isShowErrorTips">{{ $t(`m.renewal['请选择过期权限']`) }}</p>
    <div slot="action" class="transfer-footer" v-if="isFixedFooter">
      <!-- <bk-button theme="primary" disabled v-if="isEmpty">
        <span v-bk-tooltips="{ content: $t(`m.renewal['暂无将过期的权限']`), extCls: 'iam-tooltips-cls' }">
          {{ $t(`m.common['提交']`) }}
        </span>
      </bk-button> -->
      <bk-popover
        ext-cls="iam-tooltips-cls"
        :content="$t(`m.renewal['暂无将过期的权限']`)"
        :disabled="isEmpty"
      >
        <bk-button theme="primary" :loading="submitLoading" @click="handleSubmit">
          {{ $t(`m.common['提交']`) }}
        </bk-button>
      </bk-popover>
      <bk-button @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>
  </smart-action>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, getNowTimeExpired } from '@/common/util';
  import { SIX_MONTH_TIMESTAMP, ONE_DAY_TIMESTAMP } from '@/common/constants';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import RenderTable from '../components/render-renewal-table';
  import PermPolicy from '@/model/my-perm-policy';

  export default {
    components: {
      IamDeadline,
      RenderTable
    },
    data () {
      return {
        panels: [
          {
            name: 'group',
            label: this.$t(`m.userOrOrg['个人用户组权限']`),
            count: 0,
            total: 0,
            data: [],
            emptyData: {
              type: '',
              text: '',
              tip: '',
              tipType: ''
            }
          },
          {
            name: 'custom',
            label: this.$t(`m.perm['自定义权限']`),
            count: 0,
            total: 0,
            data: [],
            emptyData: {
              type: '',
              text: '',
              tip: '',
              tipType: ''
            }
          }
        ],
        active: 'group',
        expiredAt: SIX_MONTH_TIMESTAMP,
        tableList: [],
        curSelectedList: [],
        tabKey: 'tab-key',
        reason: this.$t(`m.renewal['权限续期']`),
        submitLoading: false,
        tableLoading: false,
        isFixedFooter: true,
        isShowErrorTips: false,
        isShowReasonError: false,
        isEmpty: false,
        curEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemsLayout', 'externalSystemId']),
      getTableList () {
          const panelData = this.panels.find(item => item.name === this.active);
          if (panelData) {
            this.curEmptyData = _.cloneDeep(panelData.emptyData);
            return panelData.data;
          }
          return [];
      },
      formatCount () {
        const panel = this.panels.find(item => item.name === this.active);
        if (panel) {
          return panel.total;
        }
        return this.panels[0].total;
      },
      formatExpireSoon () {
        return (payload) => {
          const dif = payload - getNowTimeExpired();
          const days = Math.ceil(dif / (24 * 3600));
          return days < 16;
        };
      },
      formatExpired () {
        return (payload) => {
          return payload < getNowTimeExpired();
        };
      }
    },
    watch: {
      panels: {
        handler (value) {
          this.fetchActiveTabData(value);
        },
        immediate: true
      },
      externalSystemsLayout: {
        handler (value) {
          if (value.myPerm.renewal.hideCustomTab) {
            this.panels.splice(1, 1);
            this.active = 'group';
          }
        },
        immediate: true,
        deep: true
      },
      active () {
        this.fetchActiveTabData(this.panels);
      }
    },
    async created () {
      this.isEmpty = false;
      this.curSelectedList = [];
      const query = this.$route.query;
      this.active = query.tab || 'group';
      await this.fetchData();
    },
    methods: {
      async fetchData () {
        this.tableLoading = true;
        try {
          const userGroupParams = {
            page_size: 10,
            page: 1
          };
          if (this.externalSystemId) {
            userGroupParams.system_id = this.externalSystemId;
          }
          const resultList = await Promise.all([
            this.$store.dispatch('renewal/getExpireSoonGroupWithUser', userGroupParams),
            this.$store.dispatch('renewal/getExpireSoonPerm')
          ]).finally(() => {
            this.tableLoading = false;
          });
          const { code, data } = resultList[0];
          const { code: customCode, data: customList } = resultList[1];
          this.panels[0].emptyData
            = formatCodeData(code, this.panels[0].emptyData, data.results.length === 0);
          this.panels[0] = Object.assign(this.panels[0], { data: data.results, total: data.count });
          if (this.panels[1]) {
            customList.forEach((item) => {
              item.policy = new PermPolicy(item.policy);
            });
            this.panels[1] = Object.assign(this.panels[1], {
              data: customList,
              total: customList.length,
              emptyData: formatCodeData(customCode, this.panels[1].emptyData, customList.length === 0)
            });
          }
          this.tabKey = +new Date();
          this.fetchActiveTabData(this.panels);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.curEmptyData = formatCodeData(code, this.curEmptyData);
          this.messageAdvancedError(e);
        }
      },

      async fetchActiveTabData (payload) {
        const activeItem = {
          group: () => {
            return !(payload[0].total > 0);
          },
          custom: () => {
            return !(payload[1] && payload[1].total > 0);
          }
        };
        this.isEmpty = activeItem[this.active]();
        this.tabKey = +new Date();
      },

      handleTabChange (payload) {
        this.$nextTick(() => {
          this.$refs.tabRef
            && this.$refs.tabRef.$refs.tabLabel
            && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
        });
        window.history.replaceState({}, '', `?${buildURLParams({ tab: payload })}`);
      },

      handleFilterSystem (payload) {
        this.$nextTick(() => {
          const { list } = payload;
          let customData = this.panels.find((item) => item.name === 'custom');
          if (customData) {
            customData = Object.assign(customData, {
              total: list.length
            });
            this.$refs.tabRef
              && this.$refs.tabRef.$refs.tabLabel
              && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
          }
        });
      },

      handleReasonInput () {
        this.isShowReasonError = false;
      },

      handleReasonBlur (payload) {
        if (!payload) {
          this.isShowReasonError = true;
        }
      },

      handleDeadlineChange (payload) {
        this.expiredAt = payload || ONE_DAY_TIMESTAMP;
      },

      handleSelected (type, value) {
        if (type === 'group') {
          this.panels[0].count = this.panels[0].total;
          this.curSelectedList = value;
        } else {
          if (this.panels[1]) {
            this.panels[1].count = value.length;
            this.curSelectedList = value;
          }
        }
        this.isShowErrorTips = false;
        this.$nextTick(() => {
          this.$refs.tabRef
            && this.$refs.tabRef.$refs.tabLabel
            && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
        });
      },

      handleChangeCount (count, data) {
        const tabMap = {
          group: () => {
            this.$set(this.panels[0], 'total', count);
            this.tabKey = +new Date();
          },
          custom: async () => {
            if (this.panels[1]) {
              this.panels[1] = Object.assign(this.panels[1], {
                total: count,
                data
              });
            }
          }
        };
        return tabMap[this.active]();
      },

      async handleSubmit () {
        if (this.curSelectedList.length < 1) {
          this.isShowErrorTips = true;
          return;
        }
        if (!this.reason) {
          this.isShowReasonError = true;
          this.scrollToLocation(this.$refs.reasonRef);
          return;
        }
        this.submitLoading = true;
        const isGroup = this.active === 'group';
        const params = {
          reason: this.reason
        };
        if (isGroup) {
          if (this.externalSystemId) {
            params.source_system_id = this.externalSystemId;
          }
          params.groups = this.curSelectedList.map(
            ({ id, name, description, expired_at }) => ({ id, name, description, expired_at })
          );
        } else {
          params.policies = this.curSelectedList.map(({ id, expired_at }) => ({ id, expired_at }));
        }
        const dispatchMethod = isGroup ? 'groupPermRenewal' : 'customPermRenewal';
        try {
          await this.$store.dispatch(`renewal/${dispatchMethod}`, params);
          this.messageSuccess(this.$t(`m.renewal['批量申请提交成功']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      },

      handleCancel () {
        this.$router.push({
          name: 'myPerm'
        });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-perm-renewal-wrapper {
  .horizontal-item {
    padding: 0 32px 24px 24px;
    margin-bottom: 0;
    &:first-child {
      padding-top: 24px;
    }
    .label {
      min-width: 88px !important;
      width: 0;
    }
  }
  .panel-name {
    margin: 0 3px;
    display: inline-block;
    vertical-align: middle;
  }
  .error-tips {
    position: relative;
    top: -10px;
    font-size: 12px;
    color: #ea3636;
  }
  .reason-error-tips {
    top: 0;
  }
  .reason-wrapper {
    .renewal-reason-error {
      .bk-textarea-wrapper {
        border-color: #ea3636;
      }
    }
  }
  /deep/ .iam-renewal-tab-cls {
    background-color: #DCDEE5;
    .bk-tab-section {
      padding: 0;
    }
  }
  /deep/ .transfer-footer {
    font-size: 0;
    padding-left: 112px;
    .bk-button {
      min-width: 88px;
      margin-right: 8px;
    }
  }
  /deep/ [role~="action-position"] {
    margin-top: 0 !important;
  }
  &-lang {
    .horizontal-item {
      .label {
        min-width: 150px !important;
        width: 0;
      }
    }
    /deep/ .transfer-footer {
      padding-left: 175px;
    }
  }
}
</style>

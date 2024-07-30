<template>
  <smart-action
    ref="iamRenewalPerm"
    :class="[
      'iam-perm-renewal-wrapper',
      { 'iam-perm-renewal-wrapper-lang': !curLanguageIsCn },
      { 'no-fixed-footer-wrapper': !isFixedFooter }
    ]"
  >
    <render-horizontal-block :label="$t(`m.renewal['续期时长']`)" :required="true">
      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
    </render-horizontal-block>
    <render-horizontal-block
      ext-cls="reason-wrapper"
      :label="$t(`m.renewal['续期理由']`)"
      :required="true"
    >
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
        <p class="error-tips reason-error-tips" v-if="isShowReasonError">{{ $t(`m.verify['请输入续期理由']`) }}</p>
      </section>
    </render-horizontal-block>
    <render-horizontal-block
      :label="$t(`m.userOrOrg['续期预览']`)"
      :required="true">
      <!-- <bk-tab
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
            <span
              :class="[
                'panel-content',
                { 'is-active': active === panel.name }
              ]"
            >
              <span class="panel-name">{{ panel.label }}</span>
              <span class="panel-count">{{panel.total}}</span>
            </span>
          </template>
        </bk-tab-panel>
      </bk-tab> -->
      <div class="renewal-preview">
        <div
          v-for="item in panels"
          :key="item.name"
          :class="[
            'renewal-preview-tab',
            { 'is-active': active === item.name }
          ]"
          @click.stop="handleTabChange(item.name)"
        >
          <div class="renewal-preview-tab-item">
            <span class="tab-name">{{ item.label }}</span>
            <span class="tab-count">{{ item.total }}</span>
          </div>
        </div>
      </div>
      <RenderTable
        :ref="`permRenewalRef_${active}`"
        :renewal-time="expiredAt"
        :type="active"
        :data="getTableList"
        :count="formatCount"
        :loading="tableLoading"
        :empty-data="curEmptyData"
        @on-select="handleSelected"
        @on-change-count="handleChangeCount"
        @on-filter-system="handleFilterSystem"
        @on-page-change="handlePageChange"
        @on-limit-change="handleLimitChange"
      />
      <div class="renewal-footer" v-if="!isFixedFooter">
        <bk-popover
          ext-cls="iam-tooltips-cls"
          :content="$t(`m.renewal['暂无将过期的权限']`)"
          :disabled="isEmpty"
        >
          <bk-button theme="primary" :loading="submitLoading" @click="handleSubmit">
            {{ $t(`m.common['提交']`) }}
          </bk-button>
        </bk-popover>
        <bk-button @click.stop="handleCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </render-horizontal-block>
    <p class="error-tips" v-if="isShowErrorTips">{{ $t(`m.renewal['请选择过期权限']`) }}</p>
    <div slot="action" class="renewal-footer" v-if="isFixedFooter">
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
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, getNowTimeExpired } from '@/common/util';
  import { SIX_MONTH_TIMESTAMP, ONE_DAY_TIMESTAMP } from '@/common/constants';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import RenderTable from '../components/render-renewal-table';
  import PermPolicy from '@/model/my-perm-policy';

  export default {
    inject: ['showNoticeAlert'],
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
            this.curEmptyData = cloneDeep(panelData.emptyData);
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
      this.curSelectedList = [];
      const { tab, isBatch } = this.$route.query;
      this.active = tab || 'group';
      this.$store.commit('setHeaderTitle', isBatch ? this.$t(`m.renewal['批量权限续期']`) : this.$t(`m.renewal['权限续期']`));
      await this.fetchData();
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.handleGetPageHeight);
      });
      window.addEventListener('resize', this.handleGetPageHeight);
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
          // this.tabKey = +new Date();
          this.fetchActiveTabData(this.panels);
        } catch (e) {
          this.curEmptyData = formatCodeData(e.code, this.curEmptyData);
          this.messageAdvancedError(e);
        } finally {
          this.handleGetPageHeight();
        }
      },

      fetchActiveTabData (payload) {
        this.isEmpty = payload.some((v) => v.total > 0);
        // this.tabKey = +new Date();
      },

      handleGetPageHeight () {
        setTimeout(() => {
          // 第一个32和24代表上下外边距， 第二个32代表按钮的行高
          const noticeComHeight = this.showNoticeAlert && this.showNoticeAlert() ? 40 : 0;
          const viewHeight = window.innerHeight - 51 - 51 - 32 - 32 - 24 - noticeComHeight;
          this.isFixedFooter = this.$refs.iamRenewalPerm.$refs.smartActionWrapper.offsetHeight > viewHeight;
        }, 0);
      },

      handleTabChange (payload) {
        this.active = payload;
        // this.$nextTick(() => {
        //   this.$refs.tabRef
        //     && this.$refs.tabRef.$refs.tabLabel
        //     && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
        // });
        window.history.replaceState({}, '', `?${buildURLParams({ tab: payload })}`);
        this.handleGetPageHeight();
      },

      handleFilterSystem (payload) {
        this.$nextTick(() => {
          const { list } = payload;
          let customData = this.panels.find((item) => item.name === 'custom');
          if (customData) {
            customData = Object.assign(customData, {
              total: list.length
            });
            // this.$refs.tabRef
            //   && this.$refs.tabRef.$refs.tabLabel
            //   && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
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
        this.isShowErrorTips = false;
        const typeMap = {
          group: () => {
            this.panels[0].count = this.panels[0].total;
            this.curSelectedList = value;
          },
          custom: () => {
            this.panels[1].count = value.length;
            this.curSelectedList = value;
          }
        };
        if (typeMap[type]) {
          return typeMap[type]();
        }
        // this.$nextTick(() => {
        //   this.$refs.tabRef
        //     && this.$refs.tabRef.$refs.tabLabel
        //     && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
        // });
      },

      handleChangeCount (count, data) {
        const tabMap = {
          group: () => {
            this.$set(this.panels[0], 'total', count);
            // this.tabKey = +new Date();
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

      handlePageChange () {
        this.handleGetPageHeight();
      },

      handleLimitChange () {
        this.handleGetPageHeight();
      },

      // 续期个人用户组
      async fetchRenewalPersonalPerm () {
        try {
          const renewalGroup = this.curSelectedList.filter((v) => ['group'].includes(v.mode_type));
          if (!renewalGroup.length) {
            return;
          }
          const params = {
            reason: this.reason,
            groups: renewalGroup.map(({ id, name, description, expired_at }) => ({ id, name, description, expired_at }))
          };
          if (this.externalSystemId) {
            params.source_system_id = this.externalSystemId;
          }
          await this.$store.dispatch(`renewal/groupPermRenewal`, params);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      },

      // 续期自定义权限
      async fetchRenewalCustomPerm () {
        try {
          const renewalCustom = this.curSelectedList.filter((v) => ['custom'].includes(v.mode_type));
          if (!renewalCustom.length) {
            return;
          }
          const params = {
            reason: this.reason,
            policies: renewalCustom.map(({ id, expired_at }) => ({ id, expired_at }))
          };
          await this.$store.dispatch(`renewal/customPermRenewal`, params);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      },

      async handleSubmit () {
        if (!this.reason) {
          this.isShowReasonError = true;
          this.scrollToLocation(this.$refs.reasonRef);
          return;
        }
        if (this.curSelectedList.length < 1) {
          this.isShowErrorTips = true;
          return;
        }
        this.submitLoading = true;
        await Promise.all([this.fetchRenewalPersonalPerm(), this.fetchRenewalCustomPerm()]);
        this.messageSuccess(this.$t(`m.renewal['批量申请提交成功']`), 3000);
        this.$router.push({
          name: 'apply'
        });
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
  min-height: auto;
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
  .renewal-preview {
    display: flex;
    background-color: #F0F1F5;
    color: #313238;
    font-size: 14px;
    border: 1px solid #DCDEE5;
    &-tab {
      min-width: 140px;
      border-right: 1px solid #DCDEE5;
      cursor: pointer;
      &-item {
        display: flex;
        align-items: center;
        padding: 11px 16px 12px 16px;
        .tab-count {
          min-width: 16px;
          height: 16px;
          line-height: 16px;
          padding: 0 8px;
          margin-left: 8px;
          border-radius: 8px;
          text-align: center;
          font-size: 12px;
          color: #63656E;
          background-color: #DCDEE5;
        }
      }
      &.is-active {
        margin-bottom: -1px;
        color: #3a84ff;
        background-color: #ffffff;
        border-top: 4px solid #3a84ff;
        .renewal-preview-tab-item {
          padding: 7px 16px 12px 16px;
          .tab-count {
            background-color: #E1ECFF;
            color: #3a84ff;
          }
        }
      }
    }
  }
  /deep/ .renewal-footer {
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
    /deep/ .renewal-footer {
      padding-left: 175px;
    }
  }
   &.no-fixed-footer-wrapper {
    .horizontal-item {
      .renewal-footer {
        margin-top: 32px;
        padding-left: 0;
      }
    }
    /deep/ [role~="action-position"] {
      display: none;
    }
  }
}
</style>

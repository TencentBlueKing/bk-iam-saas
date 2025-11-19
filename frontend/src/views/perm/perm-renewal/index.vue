<template>
  <smart-action class="iam-perm-renewal-wrapper">
    <render-horizontal-block
      :label="$t(`m.renewal['选择权限']`)"
      :required="true">
      <bk-tab
        :key="tabKey"
        :active.sync="active"
        ref="tabRef"
        type="unborder-card"
        ext-cls="iam-renewal-tab-cls"
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
            <!-- <bk-badge :val="panel.count" :theme="curBadgeTheme(panel.name)" /> -->
          </template>
        </bk-tab-panel>
      </bk-tab>
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
    </render-horizontal-block>
    <p class="error-tips" v-if="isShowErrorTips">{{ $t(`m.renewal['请选择过期权限']`) }}</p>
    <render-horizontal-block :label="$t(`m.renewal['续期时长']`)">
      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
    </render-horizontal-block>
    <render-horizontal-block
      ext-cls="reason-wrapper"
      :label="$t(`m.common['理由']`)"
      :required="true">
      <section ref="reasonRef">
        <bk-input
          type="textarea"
          v-model="reason"
          :maxlength="255"
          :placeholder="$t(`m.verify['请输入']`)"
          :ext-cls="isShowReasonError ? 'renewal-reason-error' : ''"
          @input="handleReasonInput"
          @blur="handleReasonBlur">
        </bk-input>
        <p class="error-tips reason-error-tips" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
      </section>
    </render-horizontal-block>
    <div slot="action">
      <bk-button theme="primary" disabled v-if="isEmpty">
        <span v-bk-tooltips="{ content: $t(`m.renewal['暂无将过期的权限']`), extCls: 'iam-tooltips-cls' }">
          {{ $t(`m.common['提交']`) }}
        </span>
      </bk-button>
      <bk-button theme="primary" :loading="submitLoading" v-else @click="handleSubmit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <bk-button style="margin-left: 6px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData } from '@/common/util';
  import { SIX_MONTH_TIMESTAMP, ONE_DAY_TIMESTAMP } from '@/common/constants';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import RenderTable from '../components/render-renewal-table';
  import PermPolicy from '@/model/my-perm-policy';

  export default {
    name: '',
    components: {
      IamDeadline,
      RenderTable
    },
    data () {
      return {
        panels: [
          {
            name: 'group',
            label: this.$t(`m.perm['用户组权限']`),
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
        tabKey: 'tab-key',
        reason: this.$t(`m.renewal['权限续期']`),
        submitLoading: false,
        tableLoading: false,
        isShowErrorTips: false,
        isEmpty: false,
        curEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        isShowReasonError: false
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId']),
      getTableList () {
          const panelData = this.panels.find(item => item.name === this.active);
          if (panelData) {
            this.curEmptyData = _.cloneDeep(panelData.emptyData);
            return panelData.data;
          }
          return [];
      },
      curBadgeTheme () {
        return payload => {
          return payload === this.active ? '#e1ecff' : '#f0f1f5';
        };
      },
      formatCount () {
        const panel = this.panels.find(item => item.name === this.active);
        if (panel) {
          return panel.total;
        }
        return this.panels[0].total;
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
        window.history.replaceState({}, '', `?${buildURLParams({
          tab: payload,
          role_name: this.user.role.name
        })}`);
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
          console.error(e);
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
<style lang="postcss">
    .iam-perm-renewal-wrapper {
        .iam-renewal-tab-cls {
            margin-top: -15px;
            .bk-tab-section {
              padding: 0;
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
    }
</style>

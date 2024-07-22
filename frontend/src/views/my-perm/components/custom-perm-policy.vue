<template>
  <div class="my-custom-perm-policy">
    <template v-if="hasPerm">
      <bk-checkbox
        ext-cls="all-system-checkbox"
        v-model="isAllSystem"
        @change="handleAllSystemChange"
      >
        {{ $t(`m.perm['跨系统全选']`) }}
      </bk-checkbox>
      <CustomPermSystemPolicy
        v-for="(sys, sysIndex) in systemPolicyList"
        :key="sys.id"
        :ref="`rPolicy_${sys.id}`"
        :mode="'detail'"
        :title="sys.name"
        :count="sys.pagination.count || 0"
        :ext-cls="formatExtCls(sys)"
        :external-delete="true"
        :expanded.sync="sys.expanded"
        @on-expanded="handleExpanded(...arguments, sys)"
      >
        <div slot="headerTitle" class="single-hide header-content">
          <span class="header-content-title">{{ sys.name }}</span>
          <span class="header-content-count">
            ({{ $t(`m.common['共']`) }}
            <span class="count">{{ sys.pagination.count || 0 }}</span>
            {{ $t(`m.common['个']`) }}{{ $t(`m.perm['操作权限']`) }})
          </span>
        </div>
        <div slot="headerOperate">
          <bk-popconfirm
            trigger="click"
            placement="bottom-end"
            ext-popover-cls="iam-custom-popover-confirm"
            :ref="`delTempConfirm_${sys.id}`"
            :width="280"
            @confirm="handleDeleteSystem(sys, sysIndex)"
          >
            <div slot="content">
              <div class="popover-title">
                <div class="popover-title-text">
                  {{ deleteConfirmData.title }}
                </div>
              </div>
              <div class="popover-content">
                <div class="popover-content-item">
                  <span class="popover-content-item-label">{{ deleteConfirmData.label }}{{ $t(`m.common['：']`)}}</span>
                  <span class="popover-content-item-value"> {{ sys.name }}</span>
                </div>
                <div class="popover-content-tip">
                  {{ deleteConfirmData.tip }}
                </div>
              </div>
            </div>
            <div
              :class="['delete-action', { 'is-disabled': isDisabledOperate }]"
              @click.stop="handleShowDelConfirm(sys)"
            >
              <Icon class="delete-action-icon" type="delete-line" v-if="deleteConfirmData.icon" />
              <span class="delete-action-title">{{ deleteConfirmData.btnTitle }}</span>
            </div>
          </bk-popconfirm>
        </div>
        <CustomPermTable
          class="iam-perm-edit-table"
          :ref="`customPermTable_${sys.id}_${mode}`"
          :mode="mode"
          :key="sys.id"
          :system-id="sys.id"
          :pagination="sys.pagination"
          :renewal-custom-perm="renewalCustomPerm"
          :group-data="groupData"
          :cur-selected-group="curSelectedGroup"
          :cur-search-params="curSearchParams"
          :empty-data="emptyPolicyData"
          :is-search-perm="isSearchPerm"
          @on-select-perm="handleSelectPerm"
          @on-update-pagination="handleUpdatePagination(...arguments, sys)"
          @on-page-change="handlePageChange(...arguments, sys)"
          @on-limit-page="handleLimitChange(...arguments, sys)"
          @on-delete-action="handleDeleteAction(...arguments, sysIndex)"
        />
      </CustomPermSystemPolicy>
    </template>
    <template v-else>
      <div class="my-custom-perm-policy-empty-wrapper">
        <ExceptionEmpty
          :type="emptyPolicyData.type"
          :empty-text="emptyPolicyData.text"
          :tip-text="emptyPolicyData.tip"
          :tip-type="emptyPolicyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </div>
    </template>
  </div>
</template>

<script>
  import { uniqWith, isEqual } from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData } from '@/common/util';
  import { bus } from '@/common/bus';
  import PermSystem from '@/model/my-perm-system';
  import CustomPermSystemPolicy from '@/components/iam-expand-perm/index.vue';
  import CustomPermTable from './custom-perm-table.vue';

  export default {
    components: {
      CustomPermSystemPolicy,
      CustomPermTable
    },
    props: {
      mode: {
        type: String
      },
      list: {
        type: Array,
        default: () => []
      },
      renewalCustomPerm: {
        type: Array,
        default: () => []
      },
      groupData: {
        type: Object
      },
      deleteConfirmData: {
        type: Object,
        default: () => {
          return {
            title: '',
            tip: '',
            label: ''
          };
        }
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: 'empty',
            text: '暂无数据',
            tip: '',
            tipType: ''
          };
        }
      },
      curSearchParams: {
        type: Object,
        default: () => {}
      },
      curSearchPagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            count: 0,
            limit: 10
          };
        }
      },
      isSearchPerm: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isAllSystem: false,
        isDisabledOperate: false,
        systemPolicyList: [],
        curSelectedGroup: [],
        emptyPolicyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemId']),
      hasPerm () {
        return this.systemPolicyList.length > 0;
      },
      formatExtCls () {
        return (payload) => {
          if (payload && !payload.pagination.count) {
            return 'no-perm-item-wrapper';
          }
          return '';
        };
      }
    },
    watch: {
      list: {
        handler (v) {
          this.curSelectedGroup = [];
          this.handleGetSystemData(v);
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.emptyPolicyData = Object.assign({}, value);
          if (this.isSearchPerm || ['search'].includes(value.tipType)) {
            this.handleSystemSearch();
          }
        },
        immediate: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-all-delete-policy');
      });
      // 处理跨系统删除操作更新
      bus.$on('on-all-delete-policy', ({ allDeletePolicy }) => {
        this.systemPolicyList.forEach((item) => {
          const curSystem = allDeletePolicy.keys().find((v) => v === item.id);
          if (curSystem) {
            this.$nextTick(() => {
              const customRef = this.$refs[`customPermTable_${curSystem}_${this.mode}`];
              if (customRef && customRef.length) {
                customRef[0].fetchActions(curSystem);
                customRef[0].fetchPolicy({ systemId: curSystem });
              }
            });
          }
        });
      });
    },
    methods: {
      async handleDeleteSystem (payload, sysIndex) {
        const { id } = payload;
        try {
          const { data } = await this.$store.dispatch('permApply/getPolicies', {
            system_id: id
          });
          const policyIdList = data.map((item) => item.policy_id);
          const { code } = await this.$store.dispatch('permApply/deletePerm', {
            policyIds: policyIdList,
            systemId: id
          });
          if (code === 0) {
            this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            bus.$emit('on-update-perm-group', {
              active: 'customPerm',
              count: 0,
              systemId: this.systemPolicyList[sysIndex].id
            });
            this.handleAllSystemChange(false);
            this.systemPolicyList.splice(sysIndex, 1);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleRefreshSystem () {
        if (!this.isSearchPerm && this.curSearchParams.system_id) {
          //  处理需要重新获取系统下的操作业务
          await this.handleGetSystemAction();
        } else {
          this.handleGetSystemData(this.systemPolicyList || []);
          this.emptyPolicyData = formatCodeData(
            0,
            this.emptyPolicyData,
            this.systemPolicyList.length === 0
          );
        }
      },

      async handleGetSystemAction () {
        const externalParams = {};
        if (this.externalSystemId) {
          externalParams.system_id = this.externalSystemId;
        }
        this.emptyPolicyData.tipType = '';
        const { code, data } = await this.$store.dispatch(
          'permApply/getHasPermSystem',
          externalParams
        );
        this.handleGetSystemData(data || []);
        this.emptyPolicyData = formatCodeData(
          code,
          this.emptyPolicyData,
          data.length === 0
        );
      },

      handleAllSystemChange (payload) {
        this.isAllSystem = payload;
        this.$nextTick(() => {
          this.systemPolicyList.forEach((item) => {
            const permRef = this.$refs[`customPermTable_${item.id}_${this.mode}`];
            if (permRef && permRef.length) {
              const customPermRef = permRef[0].$refs[`customPermRef_${this.mode}_${item.id}`];
              customPermRef && permRef[0].policyListBack.forEach((sub) => {
                this.$set(sub, 'mode_type', 'customPerm');
                this.$set(sub, 'system_id', item.id);
                customPermRef.toggleRowSelection(sub, payload);
                if (payload) {
                  permRef[0].currentSelectList.push(sub);
                  this.curSelectedGroup.push(sub);
                } else {
                  permRef[0].currentSelectList = [];
                  this.curSelectedGroup = [];
                }
              });
            }
          });
          this.$emit('on-selected-group', this.curSelectedGroup);
        });
      },

      handleUpdatePagination (payload, row) {
        row.pagination = { ...payload };
      },

      handlePageChange (payload, row) {
        row.pagination = Object.assign(row.pagination, { current: payload });
      },

      handleLimitChange (payload, row) {
        row.pagination = Object.assign(row.pagination, { current: 1, limit: payload });
      },

      handleExpanded (value, payload) {
        
      },

      handleShowDelConfirm (payload) {
        this.$nextTick(() => {
          const delConfirmRef = this.$refs[`delTempConfirm_${payload.id}`];
          if (delConfirmRef && delConfirmRef.length > 0 && delConfirmRef[0].$refs.popover) {
            delConfirmRef[0].$refs.popover.showHandler();
          }
        });
      },

      handleSelectPerm (payload) {
        this.curSelectedGroup = uniqWith([...payload], isEqual);
        this.$emit('on-selected-group', this.curSelectedGroup);
        // 判断是否系统全选
        const isCustom = ['customPerm'].includes(this.mode);
        if (isCustom) {
          const customList = this.curSelectedGroup.filter((v) => ['customPerm'].includes(v.mode_type));
          const countList = this.systemPolicyList.map((v) => v.count);
          const customTotal = countList.reduce((prev, cur) => {
            return cur + prev;
          }, 0);
          this.isAllSystem = customTotal === customList.length;
        }
      },

      handleDeleteAction (policyListLen, sysIndex) {
        this.$set(this.systemPolicyList[sysIndex], 'count', policyListLen);
        bus.$emit('on-update-perm-group', {
          active: 'customPerm',
          count: policyListLen,
          systemId: this.systemPolicyList[sysIndex].id
        });
        if (this.systemPolicyList[sysIndex].count < 1) {
          this.systemPolicyList.splice(sysIndex, 1);
        }
        if (!this.systemPolicyList.length) {
          this.handleRefreshSystem();
        }
      },

      // 格式化系统列表数据
      handleGetSystemData (payload) {
        const systemPolicyList = payload.map((item) => {
          return {
            ...new PermSystem(item),
            ...{
              pagination: {
                current: 1,
                limit: 10,
                count: 0
              }
            }
          };
        });
        this.systemPolicyList.splice(0, this.systemPolicyList.length, ...systemPolicyList);
        this.systemPolicyList.sort((curr, next) => curr.name.localeCompare(next.name));
        if (this.externalSystemId && this.systemPolicyList.length > 1) {
          const externalSystemIndex = this.systemPolicyList.findIndex(
            (item) => item.id === this.externalSystemId
          );
          if (externalSystemIndex > -1) {
            this.systemPolicyList.splice(
              externalSystemIndex,
              1,
              ...this.systemPolicyList.splice(
                0,
                1,
                this.systemPolicyList[externalSystemIndex]
              )
            );
          }
        }
        if (this.isSearchPerm) {
          this.emptyPolicyData.tipType = 'search';
        }
        this.emptyPolicyData = formatCodeData(0, this.emptyPolicyData, systemPolicyList.length === 0);
      },

      // 搜索自定义权限
      handleSystemSearch () {
        // 过滤掉搜索框的参数, 处理既有筛选系统也有输入名字、描述等仍要展示为空的情况
        const { id, description, name, system_id: systemId } = this.curSearchParams;
        const noValue = !id && !name && !description;
        // 筛选搜索的系统id
        const curSystemList = this.systemList.filter((item) => item.id === systemId && noValue);
        this.handleGetSystemData(curSystemList || []);
      },
      
      handleEmptyClear () {
        this.$emit('on-clear');
      },

      handleEmptyRefresh () {
        this.$emit('on-refresh');
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/custom-popover-confirm.css';
.my-custom-perm-policy {
  /* height: 100%; */
  .all-system-checkbox {
    padding: 0 24px 12px 24px;
  }
  /deep/ .system-render-template-item {
    background-color: #eaebf0;
    margin: 0 24px 4px 24px;
    .expand-header {
      height: 40px !important;
      line-height: 40px !important;
      padding-left: 9px !important;
      .sub-header-item {
        .sub-header-content {
          .expanded-icon {
            line-height: 40px !important;
          }
          .header-content {
            width: 100%;
            &-title {
              font-size: 12px;
              font-weight: 700;
              color: #313238;
              margin-left: 9px;
            }
            &-count {
              .count {
                color: #63656E !important;
                font-weight: 700;
              }
            }
          }
        }
        .delete-action {
          min-width: 110px;
          text-align: right;
          color: #3a84ff;
          cursor: pointer;
        }
      }
    }
    &:hover {
      background-color: #eaebf0;
    }
    &:last-child {
      margin-bottom: 0;
    }
  }
  &-empty-wrapper {
    position: absolute;
    top: 45%;
    left: 50%;
    transform: translate(-45%, -50%);
    .empty-tips {
      position: relative;
      top: -25px;
      font-size: 12px;
      color: #c4c6cc;
      text-align: center;
    }
  }
}
</style>

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
        :count="sys.count"
        :external-delete="true"
        :expanded.sync="sys.expanded"
        @on-expanded="handleExpanded(...arguments, sys)"
      >
        <div slot="headerTitle" class="single-hide header-content">
          <span class="header-content-title">{{ sys.name }}</span>
          <span class="header-content-count">
            ({{ $t(`m.common['共']`) }}
            <span class="count">{{ sys.count }}</span>
            {{ $t(`m.common['个']`) }}{{ $t(`m.perm['操作权限']`) }})
          </span>
        </div>
        <div slot="headerOperate">
          <bk-popconfirm
            trigger="click"
            :ref="`delTempConfirm_${sys.id}`"
            placement="bottom-end"
            ext-popover-cls="iam-custom-popover-confirm"
            :width="280"
            @confirm="handleDeleteAll(sys, sysIndex)"
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
          ref="customPermTable"
          class="iam-perm-edit-table"
          :key="sys.id"
          :system-id="sys.id"
          :cur-search-params="curSearchParams"
          :empty-data="emptyPolicyData"
          :is-search-perm="isSearchPerm"
          @after-delete="handleAfterDelete(...arguments, sysIndex)"
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
      list: {
        type: Array,
        default: () => []
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
      },
      totalCount: {
        type: Number
      }
    },
    data () {
      return {
        isAllSystem: false,
        isDisabledOperate: false,
        systemPolicyList: [],
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
      }
    },
    watch: {
      list: {
        handler (v) {
          this.formatSystemData(v);
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.emptyPolicyData = Object.assign({}, value);
          if (this.isSearchPerm || ['search'].includes(value.tipType)) {
            this.fetchSystemSearch();
          }
        },
        immediate: true
      },
      totalCount: {
        handler (value) {
          if (this.isSearchPerm && this.systemList.length) {
            this.$set(this.systemList[0], 'count', value);
          }
        },
        immediate: true
      }
    },
    methods: {
      async handleDelete () {},
      
      async handleDeleteAll (payload, sysIndex) {
        const { name, id } = payload;
        this.$bkInfo({
          subHeader: (
          <div class="del-actions-warn-info">
            <bk-icon type="info-circle-shape" class="warn" />
            <span>
              {this.$t(`m.dialog['确定要删除系统下的所有操作权限？']`, { value: name })}
            </span>
          </div>
        ),
          width: this.curLanguageIsCn ? 500 : 700,
          maskClose: true,
          closeIcon: false,
          confirmLoading: true,
          extCls: 'custom-perm-del-info',
          confirmFn: async () => {
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
                this.systemPolicyList.splice(sysIndex, 1);
                this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
                if (!this.systemPolicyList.length) {
                  this.handleRefreshSystem();
                  if (this.isSearchPerm) {
                    bus.$emit('on-perm-tab-count', {
                      active: 'CustomPerm',
                      count: this.systemPolicyList.length
                    });
                  }
                }
                return true;
              }
            } catch (e) {
              this.messageAdvancedError(e);
              return false;
            }
          }
        });
      },

      // 搜索自定义权限
      fetchSystemSearch () {
        // 过滤掉搜索框的参数, 处理既有筛选系统也有输入名字、描述等仍要展示为空的情况
        const { id, description, name, system_id: systemId } = this.curSearchParams;
        const noValue = !id && !name && !description;
        // 筛选搜索的系统id
        const curSystemList = this.systemList.filter((item) => item.id === systemId && noValue);
        this.formatSystemData(curSystemList || []);
      },

      handleAllSystemChange (payload) {
      },

      handleExpanded (value, payload) {},

      handleShowDelConfirm (payload) {
        this.$nextTick(() => {
          const delConfirmRef = this.$refs[`delTempConfirm_${payload.id}`];
          console.log(delConfirmRef);
          if (delConfirmRef && delConfirmRef.length > 0 && delConfirmRef[0].$refs.popover) {
            delConfirmRef[0].$refs.popover.showHandler();
          }
        });
      },

      handleAfterDelete (policyListLen, sysIndex) {
        this.$set(this.systemPolicyList[sysIndex], 'count', policyListLen);
        if (this.systemPolicyList[sysIndex].count < 1) {
          this.systemPolicyList.splice(sysIndex, 1);
        }
        if (!this.systemPolicyList.length) {
          this.handleRefreshSystem();
          if (this.isSearchPerm) {
            bus.$emit('on-perm-tab-count', {
              active: 'CustomPerm',
              count: this.systemPolicyList.length
            });
          }
        }
      },

      // 格式化系统列表数据
      formatSystemData (payload) {
        const systemPolicyList = payload.map((item) => new PermSystem(item));
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

      async handleRefreshSystem () {
        if (!this.isSearchPerm && this.curSearchParams.system_id) {
          const externalParams = {};
          if (this.externalSystemId) {
            externalParams.system_id = this.externalSystemId;
          }
          this.emptyPolicyData.tipType = '';
          const { code, data } = await this.$store.dispatch(
            'permApply/getHasPermSystem',
            externalParams
          );
          this.formatSystemData(data || []);
          this.emptyPolicyData = formatCodeData(
            code,
            this.emptyPolicyData,
            data.length === 0
          );
        } else {
          this.formatSystemData(this.systemPolicyList || []);
          this.emptyPolicyData = formatCodeData(
            0,
            this.emptyPolicyData,
            this.systemPolicyList.length === 0
          );
        }
      },

      async handleEmptyClear () {
        this.$emit('on-clear');
      },

      async handleEmptyRefresh () {
        this.$emit('on-refresh');
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/custom-popover-confirm.css';
.my-custom-perm-policy {
  height: 100%;
  .all-system-checkbox {
    padding: 0 24px 12px 24px;
  }
  .iam-perm-edit-table {
    min-height: 101px;
    .bk-table-enable-row-hover {
      tr {
        &:hover {
          background-color: #ffffff;
        }
      }
    }
    .bk-table-body tr:hover > td {
      background-color: #ffffff;
    }
    .bk-table {
      border-right: none;
      border-bottom: none;
      &-header-wrapper {
        .cell {
          padding-left: 20px !important;
        }
      }
      &-body-wrapper {
        .cell {
          padding: 20px !important;
          .view-icon {
            display: none;
            position: absolute;
            top: 50%;
            right: 10px;
            transform: translate(0, -50%);
            font-size: 18px;
            cursor: pointer;
          }
          &:hover {
            .view-icon {
              display: inline-block;
              color: #3a84ff;
            }
          }
        }
      }
      tr {
        &:hover {
          background-color: #ffffff;
        }
      }
    }
  }
  /deep/ .system-render-template-item {
    background-color: #eaebf0;
    margin: 0 24px 4px 24px;
    .expand-header {
      height: 40px !important;
      line-height: 40px !important;
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
              margin-left: 4px;
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

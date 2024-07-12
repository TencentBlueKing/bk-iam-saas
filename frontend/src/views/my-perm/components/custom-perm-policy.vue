<template>
  <div class="my-perm-custom-perm">
    <template v-if="hasPerm">
      <custom-perm-system-policy
        v-for="(sys, sysIndex) in systemPolicyList"
        :key="sys.id"
        :expanded.sync="sys.expanded"
        :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
        :class="sysIndex === systemPolicyList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
        :title="sys.name"
        :perm-length="isSearchPerm ? totalCount : sys.count"
        :one-perm="onePerm"
        :is-all-delete="true"
        @on-expanded="handleExpanded(...arguments, sys)"
        @on-delete-all="handleDeleteAll(sys, sysIndex)"
      >
        <custom-perm-table
          ref="customPermTable"
          :key="sys.id"
          :system-id="sys.id"
          :cur-search-params="curSearchParams"
          :empty-data="emptyPolicyData"
          :is-search-perm="isSearchPerm"
          @after-delete="handleAfterDelete(...arguments, sysIndex)"
        />
      </custom-perm-system-policy>
    </template>
    <template v-else>
      <div class="my-perm-custom-perm-empty-wrapper">
        444
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
  import CustomPermSystemPolicy from '@/components/custom-perm-system-policy/index.vue';
  import PermSystem from '@/model/my-perm-system';
  import CustomPermTable from './custom-perm-table.vue';

  export default {
    components: {
      CustomPermSystemPolicy,
      CustomPermTable
    },
    props: {
      systemList: {
        type: Array,
        default: () => []
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
        onePerm: 0,
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
      systemList: {
        handler (v) {
          this.formatSystemData(v);
        },
        immediate: true,
        deep: true
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
    async created () {
      await this.handleRefreshSystem();
    },
    methods: {
      // 搜索自定义权限
      fetchSystemSearch () {
        // 过滤掉搜索框的参数, 处理既有筛选系统也有输入名字、描述等仍要展示为空的情况
        const { id, description, name, system_id: systemId } = this.curSearchParams;
        const noValue = !id && !name && !description;
        // 筛选搜索的系统id
        const curSystemList = this.systemList.filter(
          (item) => item.id === systemId && noValue
        );
        this.formatSystemData(curSystemList || []);
      },

      /**
       * 展开/收起 系统下的权限列表
       *
       * @param {Boolean} value 展开收起标识
       * @param {Object} payload 当前系统
       */
      handleExpanded (value, payload) {},

      handleAfterDelete (policyListLen, sysIndex) {
        // --this.systemPolicyList[sysIndex].count;
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
              console.error(e);
              this.messageAdvancedError(e);
              return false;
            }
          }
        });
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
        this.onePerm = systemPolicyList.length;
        if (this.isSearchPerm) {
          this.emptyPolicyData.tipType = 'search';
        }
        this.emptyPolicyData = formatCodeData(0, this.emptyPolicyData, this.onePerm === 0);
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
        await this.handleRefreshSystem();
        this.$emit('on-clear');
      },

      async handleEmptyRefresh () {
        await this.handleRefreshSystem();
        this.$emit('on-refresh');
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import "@/css/mixins/custom-delete-action.css";
.my-perm-custom-perm {
  height: 100%;
  .iam-perm-ext-cls {
    margin-top: 10px;
  }
  .iam-perm-ext-reset-cls {
    margin-bottom: 20px;
  }
  .my-perm-custom-perm-empty-wrapper {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    img {
      width: 120px;
    }
    .empty-tips {
      position: relative;
      top: -25px;
      font-size: 12px;
      color: #c4c6cc;
      text-align: center;
    }
  }
  .iam-perm-edit-table {
    min-height: 101px;
    .bk-table-enable-row-hover .bk-table-body tr:hover > td {
      background-color: #fff;
    }
    .bk-table {
      border-right: none;
      border-bottom: none;
      .bk-table-header-wrapper {
        .cell {
          padding-left: 20px !important;
        }
      }
      .bk-table-body-wrapper {
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
      tr:hover {
        background-color: #fff;
      }
    }

    .iam-my-custom-perm-silder-header {
      display: flex;
      justify-content: space-between;
      .action-wrapper {
        margin-right: 30px;
        font-weight: normal;
      }
    }
  }
}
</style>

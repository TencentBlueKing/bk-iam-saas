<template>
  <smart-action class="iam-grading-update-template-wrapper">
    <render-horizontal-block :label="$t(`m.grading['更新权限模板']`)">
      <p class="title">
        {{ $t(`m.grading['操作和资源实例范围发生变更']`) }}，
        {{ $t(`m.grading['存在']`) }}
        <span class="count">{{ ' ' + updateLen + '' }}</span>
        {{ $t(`m.grading['个必须更新的权限模板']`) }}
      </p>
      <section class="template-content">
        <div class="left-wrapper">
          <bk-input
            clearable
            :placeholder="$t(`m.verify['请输入']`)"
            right-icon="bk-icon icon-search"
            v-model="searchKey"
            @enter="handleSearch">
          </bk-input>
          <div class="template-list-wrapper" v-bkloading="{ isLoading: leftLoading, opacity: 1 }">
            <template v-if="!isEmpty && !leftLoading">
              <section
                v-for="item in templateList"
                :key="item.id"
                :class="['template-item', { active: curTemplateId === item.id }]"
                @click="handleSelectTempalte(item)">
                <span class="template-name">{{ item.name }}</span>
                <span class="system-name">({{ item.system.name }})</span>
                <Icon type="error-fill" class="error-icon" v-if="item.isUpdate" />
              </section>
            </template>
            <template v-if="isEmpty && !leftLoading">
              <div class="empty-wrapper">
                <!-- <iam-svg /> -->
                <ExceptionEmpty
                  :type="emptyData.type"
                  :empty-text="emptyData.text"
                  :tip-text="emptyData.tip"
                  :tip-type="emptyData.tipType"
                  @on-clear="handleEmptyClear"
                  @on-refresh="handleEmptyRefresh"
                />
              </div>
            </template>
          </div>
        </div>
        <div class="right-wrapper" v-bkloading="{ isLoading: rightLoading, opacity: 1 }">
          <render-resource-instance-table
            :empty-data="emptyInstanceData"
            :data="policyList"
            :on-refresh="handleEmptyInstanceRefresh" />
        </div>
      </section>
    </render-horizontal-block>
    <div slot="action">
      <bk-button theme="primary" @click="handlePrevious">{{ $t(`m.common['上一步']`) }}</bk-button>
      <bk-button style="margin-left: 10px;" :loading="submitLoading" @click="handleSubmit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import GradeAggregationPolicy from '@/model/grade-aggregation-policy';
  import renderResourceInstanceTable from '../components/render-template-resource-instance-table';
  import { formatCodeData } from '@/common/util';
  export default {
    name: '',
    components: {
      renderResourceInstanceTable
    },
    data () {
      return {
        submitLoading: false,
        updateLen: 2,
        templateList: [
          {
            id: 1,
            gradingId: 10,
            name: '数据中心运维',
            system: {
              id: 'cmdb',
              name: '配置平台'
            },
            isUpdate: true
          },
          {
            id: 2,
            gradingId: 9,
            name: 'iGame运维',
            system: {
              id: 'job',
              name: '作业平台'
            },
            isUpdate: true
          },
          {
            id: 3,
            gradingId: 8,
            name: '运维组',
            system: {
              id: 'deves',
              name: '蓝盾DevOps平台'
            },
            isUpdate: false
          },
          {
            id: 4,
            gradingId: 3,
            name: '蓝鲸运维',
            system: {
              id: 'cmdb',
              name: '配置平台'
            },
            isUpdate: false
          }
        ],
        templateListBackup: [],
        searchKey: '',
        curTemplateId: 3,
        leftLoading: false,
        rightLoading: false,
        isFilter: false,
        policyList: [],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        emptyInstanceData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      isEmpty () {
        return this.templateList.length < 1;
      }
    },
    watch: {
      searchKey (newVal, oldVal) {
        if (newVal === '' && oldVal !== '' && this.isFilter) {
          this.templateList = _.cloneDeep(this.templateListBackup);
          this.isFilter = false;
        }
      }
    },
    created () {
      this.templateListBackup = _.cloneDeep(this.templateList);
    },
    methods: {
      async fetchPageData () {
        const curId = this.templateList.find(item => item.id === this.curTemplateId).gradingId;
        await this.fetchRatingManagerDetail(curId);
      },

      handlePrevious () {
        this.handleCancel();
      },

      handleEmptyInstanceRefresh () {
        this.fetchPageData();
      },

      handleSubmit () {},

      handleCancel () {
        this.$router.push({
          name: 'gradingAdminEdit',
          params: this.$route.params
        });
      },

      handleSearch () {
        if (!this.searchKey) {
          return;
        }
        this.emptyData.tipType = 'search';
        this.templateList = this.templateListBackup.filter(item => item.name.indexOf(this.searchKey) > -1);
        this.isFilter = true;
        this.curTemplateId = -1;
        if (!this.templateList.length) {
          this.emptyData = formatCodeData(0, this.emptyData);
        }
        // this.leftLoading = true
      },

      handleEmptyClear () {
        this.emptyData = formatCodeData(0, { ...this.emptyData, ...{ tipType: '' } }, this.templateListBackup.length === 0);
        this.templateList = _.cloneDeep(this.templateListBackup);
      },

      handleEmptyRefresh () {
        this.templateList = _.cloneDeep(this.templateListBackup);
      },

      async fetchRatingManagerDetail (payload) {
        this.rightLoading = true;
        try {
          const { data } = await this.$store.dispatch('role/getRatingManagerDetail', { id: payload });
          this.handleDetailData(data);
        } catch (e) {
          console.error(e);
          this.emptyInstanceData = formatCodeData(e.code || e.response.data.code, this.emptyInstanceData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.rightLoading = false;
        }
      },

      handleDetailData (payload) {
        const tempActions = [];
        payload.authorization_scopes.forEach(item => {
          item.actions.forEach(act => {
            const obj = {
                            ...act,
                            system_id: item.system.id,
                            system_name: item.system.name
            };
            tempActions.push(new GradeAggregationPolicy({
              'instance_selections': [],
              'actions': [obj]
            }, false, ''));
          });
        });
        this.policyList = _.cloneDeep(tempActions);
        this.emptyInstanceData = formatCodeData(0, this.emptyInstanceData, this.policyList.length === 0);
      },

      handleSelectTempalte ({ id, gradingId }) {
        if (this.curTemplateId === id) {
          return;
        }
        // this.rightLoading = true
        this.curTemplateId = id;
        this.fetchRatingManagerDetail(gradingId);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-grading-update-template-wrapper {
        .title {
            line-height: 20px;
            font-size: 12px;
            .count {
                font-weight: 600;
                color: #ec4545;
            }
        }
        .template-content {
            display: flex;
            justify-content: flex-start;
            margin-top: 20px;
            height: 500px;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            .left-wrapper {
                padding: 17px;
                flex: 0 0 245px;
                border-right: 1px solid #dcdee5;
                .template-list-wrapper {
                    padding-top: 17px;
                    height: calc(100% - 15px);
                    overflow-x: hidden;
                    overflow-y: auto;
                    &::-webkit-scrollbar {
                        width: 4px;
                        background-color: lighten(transparent, 80%);
                    }
                    &::-webkit-scrollbar-thumb {
                        height: 5px;
                        border-radius: 2px;
                        background-color: #e6e9ea;
                    }
                    .template-item {
                        position: relative;
                        padding: 0 10px;
                        line-height: 32px;
                        border-radius: 2px;
                        font-size: 12px;
                        cursor: pointer;
                        &:hover {
                            background: #e1ecff;
                            .template-name {
                                color: #3a84ff;
                            }
                        }
                        &.active {
                            background: #e1ecff;
                            .template-name {
                                color: #3a84ff;
                            }
                        }
                        .system-name {
                            color: #c4c6cc;
                        }
                        .error-icon {
                            position: absolute;
                            top: 9px;
                            right: 10px;
                            font-size: 14px;
                            color: #ec4545;
                        }
                    }
                    .empty-wrapper {
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        img {
                            height: 32px;
                        }
                    }
                }
            }
            .right-wrapper {
                width: calc(100% - 245px);
                overflow-y: auto;
                &::-webkit-scrollbar {
                    width: 4px;
                    background-color: lighten(transparent, 80%);
                }
                &::-webkit-scrollbar-thumb {
                    height: 5px;
                    border-radius: 2px;
                    background-color: #e6e9ea;
                }
            }
        }
    }
</style>

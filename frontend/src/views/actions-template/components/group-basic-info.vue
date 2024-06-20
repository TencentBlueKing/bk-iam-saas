<template>
  <div
    :class="[
      'group-basic-info',
      { 'group-basic-info-lang': !curLanguageIsCn }
    ]"
    v-bkloading="{ isLoading: detailLoading, opacity: 1 }"
  >
    <detail-layout mode="group-info-detail">
      <render-layout>
        <detail-item :label="`${$t(`m.userGroup['用户组名']`)}${$t(`m.common['：']`)}`">
          <div class="basic-info-value">
            <iam-edit-input
              field="name"
              :mode="'detail'"
              :value="basicInfo.name || '--'"
            />
          </div>
        </detail-item>
        <detail-item :label="`${$t(`m.actionsTemplate['用户组ID']`)}${$t(`m.common['：']`)}`">
          <span class="basic-info-value">{{ basicInfo.id || '--'}}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.common['描述']`)}${$t(`m.common['：']`)}`">
          <div class="basic-info-value">
            <iam-edit-textarea
              field="description"
              :mode="'detail'"
              :max-length="255"
              :value="basicInfo.description"
            />
          </div>
        </detail-item>
        <detail-item :label="`${$t(`m.grading['创建人']`)}${$t(`m.common['：']`)}`">
          <span class="basic-info-value">{{ basicInfo.creator || '--'}}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.common['创建时间']`)}${$t(`m.common['：']`)}`">
          <span class="basic-info-value">{{ basicInfo.created_time || '--'}}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.grading['更新人']`)}${$t(`m.common['：']`)}`">
          <span class="basic-info-value">{{ basicInfo.updater || '--'}}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.grading['更新时间']`)}${$t(`m.common['：']`)}`">
          <span class="basic-info-value">{{ basicInfo.updated_time || '--'}}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.actionsTemplate['成员']`)}${$t(`m.common['：']`)}`">
          <div class="basic-info-value">
            <div class="member-type-tab">
              <div
                v-for="item in memberTabList"
                :key="item.id"
                :class="[
                  'member-type-btn',
                  { 'is-active': tabActive === item.id }
                ]"
                @click.stop="handleTableChange(item.id)"
              >
                <span class="btn-name">{{ item.name }}</span>
                <span>{{ curDetailData.id ? `(${item.count})` : `(0)`}}</span>
              </div>
            </div>
            <div class="member-type-list" v-if="curDetailData.id">
              <div class="member-type-item" v-for="item in getMemberList()" :key="`${item.name}&${item.id}`">
                <div class="type-name">
                  <Icon :type="getMemberTypeDetail(item).icon" class="icon" />
                  <span class="name">{{ getMemberTypeDetail(item).name }}</span>
                  <span class="count" v-if="getMemberTypeDetail(item).id">
                    {{ `(${getMemberTypeDetail(item).id})`}}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </detail-item>
      </render-layout>
    </detail-layout>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import RenderLayout from '@/views/group/common/render-layout';
  import DetailLayout from '@/components/detail-layout';
  import DetailItem from '@/components/detail-layout/item';
  import IamEditInput from '@/components/iam-edit/input';
  import IamEditTextarea from '@/components/iam-edit/textarea';
  export default {
    components: {
      RenderLayout,
      DetailLayout,
      DetailItem,
      IamEditInput,
      IamEditTextarea
    },
    props: {
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        detailLoading: false,
        tabActive: 'userOrg',
        basicInfo: {},
        basicInfoBack: {
          id: 0,
          name: '',
          description: '',
          creator: '',
          updater: '',
          created_time: '',
          updated_time: '',
          members: []
        },
        memberTabList: [
          {
            name: this.$t(`m.userGroup['用户/组织']`),
            id: 'userOrg',
            list: [],
            count: 0
          },
          {
            name: this.$t(`m.memberTemplate['人员模板']`),
            id: 'memberTemplate',
            list: [],
            count: 0
          }
        ]
      };
    },
    computed: {
      ...mapGetters(['externalSystemId']),
      getMemberList () {
        return () => {
          const typeMap = {
            userOrg: () => {
              return this.memberTabList[0].list;
            },
            memberTemplate: () => {
              return this.memberTabList[1].list;
            }
          };
          if (typeMap[this.tabActive]) {
            return typeMap[this.tabActive]();
          }
        };
      },
      getMemberTypeDetail () {
        return (payload) => {
          const { name, type, id } = payload;
          const typeMap = {
            userOrg: () => {
              if (['user'].includes(type)) {
                return {
                  icon: 'personal-user',
                  name: id,
                  id: name
                };
              }
              if (['depart', 'department'].includes(type)) {
                return {
                  icon: 'organization-fill',
                  name,
                  id
                };
              }
            },
            memberTemplate: () => {
              return {
                icon: 'renyuanmuban',
                name
              };
            }
          };
          if (typeMap[this.tabActive]) {
            return typeMap[this.tabActive]();
          }
        };
      }
    },
    methods: {
      async fetchDetailInfo () {
        this.basicInfo = cloneDeep(this.basicInfoBack);
        const { id } = this.curDetailData;
        if (!id) {
          return;
        }
        this.detailLoading = true;
        try {
          const params = {
            id
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { data } = await this.$store.dispatch('userGroup/getUserGroupDetail', params);
          this.basicInfo = Object.assign({}, data);
          Promise.all([this.fetchUserOrOrgList(), this.fetchMemberTemplateList()]);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.detailLoading = false;
        }
      },

      // 获取用户组织成员数量
      async fetchUserOrOrgList () {
        let curData = this.memberTabList.find((v) => ['userOrg'].includes(v.id));
        if (!curData) {
          return;
        }
        try {
          const params = {
            id: this.curDetailData.id,
            offset: 0,
            limit: 1000
          };
          const { data } = await this.$store.dispatch('userGroup/getUserGroupMemberList', params);
          curData = Object.assign(curData, { count: data.count || 0, list: data.results || [] });
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      // 获取人员模板成员数量
      async fetchMemberTemplateList () {
        let curData = this.memberTabList.find((v) => ['memberTemplate'].includes(v.id));
        if (!curData) {
          return;
        }
        try {
          const params = {
            id: this.curDetailData.id,
            offset: 0,
            limit: 1000
          };
          const { data } = await this.$store.dispatch('memberTemplate/getGroupSubjectTemplate', params);
          curData = Object.assign(curData, { count: data.count || 0, list: data.results || [] });
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleTableChange (payload) {
        this.tabActive = payload;
        console.log(this.memberTabList);
      }
    }
  };
</script>

<style lang="postcss" scoped>
.group-basic-info {
  padding-left: 24px;
  .basic-info-value {
    width: 100%;
    margin-left: 8px;
  }
  /deep/.group-info-detail {
    width: 100%;
    .iam-render-common-layout {
      .left {
        flex: 0 0 100%;
      }
      .detail-item {
        font-size: 12px;
        line-height: 32px;
        .detail-label {
          min-width: 60px;
          text-align: right;
        }
        .detail-content {
          width: calc(100vh - 367px);
          .member-type-tab {
            position: relative;
            display: flex;
            border-radius: 2px;
            cursor: pointer;
            .member-type-btn {
              padding: 0px 12px;
              background-color: #EAEBF0;
              border: 4px solid #EAEBF0;
              line-height: 24px;
              &.is-active {
                color: #3A84FF;
                background-color: #ffffff;
              }
              .btn {
                font-size: 12px;
              }
            }
          }
          .member-type-list {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            margin-top: 10px;
            .member-type-item {
              margin-right: 4px;
              margin-bottom: 8px;
              line-height: 16px;
              .type-name {
                padding: 4px 6px;
                background-color: #f0f1f5;
                width: max-content;
                border-radius: 2px;
                .icon {
                  font-size: 14px;
                  color: #c4c6cc;
                }
                .name {
                  display: inline-block;
                  word-break: break-all;
                }
              }
            }
          }
          .iam-edit-input,
          .iam-edit-textarea {
            width: 100% !important;
            .edit-content {
              max-width: calc(100% - 16px) !important;
            }
          }
        }
      }
    }
  }
  &-lang {
    /deep/.group-info-detail {
      .iam-render-common-layout {
        .detail-item {
          .detail-label {
            min-width: 75px;
          }
        }
        .detail-content {
          width: calc(100vh - 160px);
        }
      }
    }
  }
}
</style>

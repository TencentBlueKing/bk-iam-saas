<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      :quick-close="true"
      ext-cls="resource-perm-member-detail-side"
      @update:isShow="handleCancel"
    >
      <div slot="header" class="resource-perm-member-detail-side-header">
        <span>{{ $t(`m.resourcePermiss['人员权限详情']`) }}</span>
        <span class="custom-header-divider">|</span>
        <span class="single-hide custom-header-name" v-bk-tooltips="{ content: curDetailData.name }">
          {{ curDetailData.name }}
        </span>
      </div>
      <div slot="content" class="resource-perm-member-detail-side-content">
        <div class="batch-operate">
          <bk-popover
            :content="$t(`m.userOrOrg['请先勾选用户组权限']`)"
            :disabled="!isRemoveDisabled"
          >
            <bk-button :disabled="isRemoveDisabled" class="batch-operate-remove">
              {{ $t(`m.userOrOrg['批量移出用户组']`) }}
            </bk-button>
          </bk-popover>
        </div>
        <div class="resource-perm-side-content">
          <template v-if="permData.hasPerm">
            <RenderTemplateItem
              :class="[
                'resource-perm-side-content-table',
                formatExtCls(index)
              ]"
              v-for="(item, index) in memberTempPermList"
              :key="index"
              :ref="`rTemplateItem${item.id}`"
              :mode="'detail'"
              :title="item.name"
              :count="item.list.length"
              :ext-cls="formatExtCls(index)"
              @on-expanded="handleExpanded(...arguments, item, index)"
            >
              <div v-bkloading="{ isLoading: item.loading, opacity: 1 }">
                555
              </div>
            </RenderTemplateItem>
          </template>
          <template v-else>
            <div class="perm-empty-wrapper">
              <ExceptionEmpty
                :type="emptyPermData.type"
                :empty-text="emptyPermData.text"
                :tip-text="emptyPermData.tip"
                :tip-type="emptyPermData.tipType"
                @on-clear="handleEmptyClear"
                @on-refresh="handleEmptyRefresh"
              />
            </div>
          </template>
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { formatCodeData } from '@/common/util';
  import RenderTemplateItem from './render-template-item.vue';
  import { mapGetters } from 'vuex';
  export default {
    components: {
      RenderTemplateItem
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        isShowSideSlider: false,
        isOnlyPerm: false,
        width: 960,
        initMemberTempPermList: [
          {
            id: 'personalOrDepartPerm',
            name: this.$t(`m.userOrOrg['个人用户组权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'departPerm',
            name: this.$t(`m.userOrOrg['组织用户组权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'userTempPerm',
            name: this.$t(`m.perm['直接加入人员模板的用户组权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'departTempPerm',
            name: this.$t(`m.perm['通过组织加入人员模板的用户组权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'customPerm',
            name: this.$t(`m.perm['自定义权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          }
        ],
        memberTempPermList: [],
        curSelectedGroup: [],
        curSearchParams: {},
        permData: {
          hasPerm: false
        },
        emptyPermData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemId']),
      isRemoveDisabled () {
        return !this.curSelectedGroup.length;
      },
      formatExtCls () {
        return (index) => {
          const len = this.memberTempPermList[index].pagination.count;
          if (!len) {
            return 'no-perm-item-wrapper';
          }
          return index > 0 ? 'iam-perm-ext-cls' : '';
        };
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideSlider = !!value;
          if (value) {
            this.fetchInitData();
          }
        },
        immediate: true
      }
    },
    methods: {
      // 获取个人/部门用户组
      async fetchUserGroup () {
        const { id, type } = this.curDetailData;
        const { emptyData, pagination } = this.memberTempPermList[0];
        try {
          this.memberTempPermList[0].loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserOrDepartGroupList';
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, {
              ...params,
              ...{
                subject_type: type,
                subject_id: id
              }
          });
          const totalCount = data.count || 0;
          this.memberTempPermList[0] = Object.assign(this.memberTempPermList[0], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(this.memberTempPermList[0].emptyData);
          setTimeout(() => {
            const curSelectedId = this.curSelectedGroup.map((item) => item.id);
            this.memberTempPermList[0].list.forEach((item) => {
              if (this.$refs.childPermTable && this.$refs.childPermTable.length) {
                if (curSelectedId.includes(item.id)) {
                  this.$refs.childPermTable[0].$refs.groupPermRef.toggleRowSelection(item, true);
                }
                this.$refs.childPermTable[0].fetchCustomTotal(this.curSelectedGroup);
              }
            });
          }, 0);
        } catch (e) {
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.memberTempPermList[0] = Object.assign(this.memberTempPermList[0], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          this.memberTempPermList[0].loading = false;
        }
      },

      // 获取用户所属部门用户组
      async fetchDepartGroup () {
        const { id, type } = this.curDetailData;
        const curData = this.memberTempPermList.find((item) => item.id === 'departPerm');
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const params = {
            ...this.curSearchParams,
            ...{
              subject_type: type,
              subject_id: id
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          // 'userOrOrg/getUserOrDepartGroupList',
          const { code, data } = await this.$store.dispatch(
            'userOrOrg/getUserGroupByDepartList',
            params
          );
          const totalCount = data.count || 0;
          this.memberTempPermList[1] = Object.assign(this.memberTempPermList[1], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
        } catch (e) {
          this.memberTempPermList[1] = Object.assign(this.memberTempPermList[1], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },
  
      // 用户人员模板用户组权限
      async fetchPermByTemp () {
        let curData = this.memberTempPermList.find((item) => item.id === 'userTempPerm');
        const { emptyData, pagination } = curData;
        const { id, type } = this.curDetailData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserMemberTempList';
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, {
              ...params,
              ...{
                subject_type: type,
                subject_id: id
              }
          });
          const totalCount = data.count;
          curData = Object.assign(curData, {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
          this.$nextTick(() => {
            curData.list.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          });
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },

      // 部门人员模版用户组权限
      async fetchDepartPermByTemp () {
        let curData = this.memberTempPermList.find((item) => item.id === 'departTempPerm');
        const { emptyData, pagination } = curData;
        const { id, type } = this.curDetailData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getDepartMemberTempList';
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, {
              ...params,
              ...{
                subject_type: type,
                subject_id: id
              }
          });
          const totalCount = data.count;
          curData = Object.assign(curData, {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },
      
      async fetchInitData () {
        const routeMap = {
          resourcePermiss: () => {
            const typeMap = {
              user: async () => {
                this.memberTempPermList = cloneDeep(this.initMemberTempPermList);
                this.memberTempPermList[0] = Object.assign(this.memberTempPermList[0], { name: this.$t(`m.userOrOrg['个人用户组权限']`) });
                await Promise.all([
                  this.fetchUserGroup(),
                  this.fetchDepartGroup(),
                  this.fetchPermByTemp(),
                  this.fetchDepartPermByTemp()
                ]);
                this.$set(this.permData, 'hasPerm', this.memberTempPermList.some((v) => v.pagination.count > 0));
                this.isOnlyPerm = this.memberTempPermList.filter((v) => v.pagination.count > 0).length === 1;
              }
            };
            return typeMap[this.curDetailData.type]();
          }
        };
        if (routeMap[this.$route.name]) {
          await routeMap[this.$route.name]();
        }
      },

      handleExpanded () {

      },
      
      handleCancel () {
        this.resetData();
        this.$emit('update:show', false);
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.$emit('on-refresh');
      },
  
      handleEmptyClear () {
        this.resetPagination();
        this.$emit('on-clear');
      },

      resetPagination (limit = 10) {
        this.memberTempPermList.forEach((item) => {
          item.pagination = Object.assign(item.pagination, { current: 1, limit });
        });
      },
  
      resetData () {
        this.width = 960;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.resource-perm-member-detail-side {
  &-header {
    display: flex;
    .custom-header-divider {
      margin: 0 8px;
      color: #dcdee5;
    }
    .custom-header-name {
      max-width: 700px;
      font-size: 12px;
      color: #979ba5;
      word-break: break-all;
    }
  }
  &-content {
    padding: 24px;
    box-sizing: border-box;
    .batch-operate {
      margin-bottom: 16px;
      &-remove {
        &.is-disabled {
          background-color: #ffffff;
        }
      }
    }
    /deep/ .resource-perm-side-content {
      &-table {
        margin-bottom: 16px;
        .header {
          padding-left: 16px;
        }
      }
    }
  }
}
</style>

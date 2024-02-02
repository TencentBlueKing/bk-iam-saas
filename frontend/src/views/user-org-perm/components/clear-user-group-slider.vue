<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="title"
      :width="sliderWidth"
      :quick-close="true"
      :show-mask="true"
      ext-cls="iam-clear-user-group-side"
      @update:isShow="handleCancel"
    >
      <div slot="content" class="iam-clear-user-group-side-content">
        <div class="header-alert">
          <div class="header-alert-tip">
            <Icon bk type="info-circle" class="header-alert-icon" />
            <div class="header-alert-text">
              <span class="type">{{ $t(`m.common['用户']`) }}{{ $t(`m.common['：']`) }}</span>
              <span>{{ $t(`m.userOrOrg['清空的是个人用户组权限；']`) }}</span>
              <span class="type">{{ $t(`m.common['组织']`) }}{{ $t(`m.common['：']`) }}</span>
              <span>{{ $t(`m.userOrOrg['清空的是组织用户组权限。']`) }}</span>
            </div>
          </div>
        </div>
        <div class="clear-preview">
          <div class="title">{{ $t(`m.userOrOrg['清空预览']`) }}</div>
          <div class="tab-list">
            <div
              :class="['tab-item', { 'tab-item-active': item.id === tabActive }]"
              v-for="item in tabList"
              :key="item.id"
              @click.stop="handleTabChange(item)"
            >
              <span class="name">{{ item.name }}</span>
              <span class="count">{{ item.pagination.count }}</span>
            </div>
          </div>
          <ClearUserGroupTable
            :list="selectData.list"
            :cur-type="tabActive"
            :pagination="selectData.pagination"
            @on-page-change="handlePageChange"
            @on-limit-change="handleLimitChange"
          />
        </div>
      </div>
      <div slot="footer">
        <div class="iam-clear-user-group-side-footer">
          <bk-button theme="primary" class="footer-btn" :loading="submitLoading" @click="handleSubmit">
            {{ $t(`m.common['提交']`) }}
          </bk-button>
          <bk-button theme="default" class="footer-btn" @click="handleCancel('cancel')">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import ClearUserGroupTable from './clear-user-group.table.vue';
  export default {
    components: {
      ClearUserGroupTable
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      title: {
        type: String
      },
      sliderWidth: {
        type: Number
      },
      userList: {
        type: Array,
        default: () => []
      },
      departList: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        submitLoading: false,
        isShowGroupError: false,
        selectTableList: [],
        initTabList: [
          {
            name: this.$t(`m.common['用户']`),
            id: 'user',
            count: 1000,
            list: [],
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            }
          },
          {
            name: this.$t(`m.common['组织']`),
            id: 'department',
            count: 0,
            list: [],
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            }
          }
        ],
        tabList: [],
        selectData: {
          pagination: {
            current: 1,
            limit: 10,
            count: 0,
            showTotalCount: true
          },
          list: []
        },
        tabActive: 'user'
      };
    },
    computed: {
      isShowSideSlider: {
        get () {
          return this.show;
        },
        set (newValue) {
          this.$emit('update:show', newValue);
        }
      }
    },
    watch: {
      show: {
        handler (value) {
          if (value) {
            this.tabList = cloneDeep(this.initTabList);
            this.tabList.forEach((item) => {
              const typeMap = {
                user: async () => {
                  if (this.userList.length) {
                    const list = cloneDeep(this.userList);
                    item = await this.fetchUserGroupSearch(item, list);
                  }
                  this.selectData = cloneDeep(item);
                },
                department: async () => {
                  if (this.departList.length) {
                    const list = cloneDeep(this.departList);
                    item = await this.fetchUserGroupSearch(item, list);
                  }
                }
              };
              return typeMap[item.id]();
            });
          }
        },
        deep: true
      }
    },
    methods: {
      // 获取个人/部门用户组
      async fetchUserGroupSearch (payload, list) {
        payload = Object.assign(payload, {
          list: list,
          pagination: {
            current: 1,
            limit: 10,
            count: list.length
          }
        });
        for (let i = 0; i < payload.list.length; i++) {
          const { id, type } = payload.list[i];
          try {
            const params = {
              offset: 1,
              limit: 5
            };
            if (this.externalSystemId) {
              params.system_id = this.externalSystemId;
              params.hidden = false;
            }
            const { data } = await this.$store.dispatch(
              'userOrOrg/getUserOrDepartGroupList',
              {
                ...params,
                ...{
                  subject_type: type,
                  subject_id: id
                }
              });
            this.$set(payload.list[i], 'perm_list', data.results || []);
            this.$set(payload.list[i], 'count', data.count || 0);
            return payload;
          } catch (e) {
            console.error(e);
            this.$set(payload.list[i], 'perm_list', []);
            this.$set(payload.list[i], 'count', 0);
            this.messageAdvancedError(e);
          }
        }
      },
      
      handleTabChange (payload) {
        this.tabActive = payload.id;
        this.selectData = payload;
      },

      handlePageChange (payload) {
        const typeMap = {
          user: () => {
            this.tabList[0].pagination = Object.assign(this.tabList[0].pagination, { current: payload });
          },
          department: () => {
            this.tabList[1].pagination = Object.assign(this.tabList[1].pagination, { current: payload });
          }
        };
        return typeMap[this.tabActive]();
      },

      handleLimitChange (payload) {
        const typeMap = {
          user: () => {
            this.tabList[0].pagination = Object.assign(this.tabList[0].pagination, { current: 1, limit: payload });
            this.selectData.pagination = cloneDeep(this.tabList[0].pagination);
          },
          department: () => {
            this.tabList[1].pagination = Object.assign(this.tabList[1].pagination, { current: 1, limit: payload });
            this.selectData.pagination = cloneDeep(this.tabList[1].pagination);
          }
        };
        return typeMap[this.tabActive]();
      },

      handleSubmit () {},

      handleCancel () {
        this.$emit('update:show', false);
        this.resetData();
      },

      resetData () {
        this.selectData = {};
        this.tabList = cloneDeep(this.initTabList);
        this.tabActive = 'user';
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-clear-user-group-side {
  &-content {
    padding: 24px 40px 16px 40px;
    .header-alert {
      width: 100%;
      height: 32px;
      line-height: 32px;
      background: #f0f8ff;
      border: 1px solid #c5daff;
      border-radius: 2px;
      &-tip {
        display: flex;
        align-items: center;
        padding: 0 10px;
        color: #63656e;
        font-size: 12px;
        .header-alert-icon {
          color: #3a84ff;
          font-size: 16px;
          margin-right: 8px;
        }
        .type {
          font-weight: 700;
        }
      }
    }
    .clear-preview {
      margin-top: 16px;
      .title {
        color: #313238;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
      }
      .tab-list {
        width: 100%;
        height: 44px;
        /* display: flex; */
        align-items: center;
        background-color: #f0f1f5;
        color: #313238;
        border: 1px solid #dcdee5;
        .tab-item {
          min-width: 110px;
          padding: 0 24px;
          line-height: 44px;
          font-size: 12px;
          display: inline-block;
          cursor: pointer;
          .name {
            font-size: 14px;
          }
          .count {
            background-color: #dcdee5;
            color: #63656e;
            padding: 0 8px;
            font-size: 12px;
            border-radius: 8px;
          }
          &:not(&:nth-of-type(1)) {
            border-left: 1px solid #dcdee5;
          }
          &:last-child {
            border-right: 1px solid #dcdee5;
          }
          &-active {
            background-color: #fafbfd;
            line-height: 43px;
            margin-bottom: -1px;
            position: relative;
            .name {
              color: #3a84ff;
            }
            .count {
              background-color: #e1ecff;
              color: #3a84ff;
            }
            &::after {
              content: '';
              position: absolute;
              top: 0;
              left: 0;
              width: 100%;
              height: 4px;
              background-color: #3a84ff;
            }
          }
        }
      }
    }
  }
  &-footer {
    margin-left: 40px;
    .footer-btn {
      min-width: 88px;
    }
  }
  /deep/ .bk-sideslider-footer {
    border-top: 0;
    background-color: #ffffff !important;
  }
}
</style>

<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="title"
      :width="sliderWidth"
      :quick-close="true"
      ext-cls="iam-clear-user-group-side"
      @update:isShow="handleCancel"
    >
      <div slot="content" class="iam-clear-user-group-side-content">
        <div class="clear-object">
          <div class="title">{{ $t(`m.userOrOrg['清空对象']`) }}</div>
          <RenderPermBoundary
            v-if="isHasUser"
            class="perm-boundary-item"
            :modules="['membersPerm']"
            :user-length="userList.length"
            :custom-slot-name="'operateObject'"
            :is-custom-title-style="true"
          >
            <div slot="operateObject">
              <Icon type="personal-user" class="type-icon" />
              <span>{{ $t(`m.common['已选']`) }}</span>
              <template>
                <span class="number">{{ userList.length }}</span>
                {{ $t(`m.common['个用户']`) }}
              </template>
              <span class="line">|</span>
              <span class="clear-object-tip">
                <span>{{ $t(`m.common['清空']`) }}</span>
                <span class="name">{{ $t(`m.userOrOrg['个人']`) }}</span>
                <span>{{ $t(`m.userOrOrg['用户组权限（不影响因所属组织而拥有的用户组权限）']`) }}</span>
              </span>
            </div>
            <div slot="membersPerm" class="members-boundary-detail">
              <template>
                <render-member-item mode="view" type="user" :data="userList" />
              </template>
            </div>
          </RenderPermBoundary>
          <RenderPermBoundary
            v-if="isHasDepartment"
            class="perm-boundary-item"
            :modules="['membersPerm']"
            :depart-length="departList.length"
            :custom-title="$t(`m.userOrOrg['清空对象']`)"
            :custom-slot-name="'operateObject'"
            :is-custom-title-style="true"
          >
            <div slot="operateObject">
              <Icon type="organization-fill" class="type-icon" />
              <span>{{ $t(`m.common['已选']`) }}</span>
              <template>
                <span class="number">{{ departList.length }}</span>
                {{ $t(`m.common['个组织']`) }}
              </template>
              <span class="line">|</span>
              <span class="clear-object-tip">
                <span>{{ $t(`m.common['清空']`) }}</span>
                <span class="name">{{ $t(`m.common['组织']`) }}</span>
                <span>{{ $t(`m.perm['用户组权限']`) }}</span>
              </span>
            </div>
            <div slot="membersPerm" class="members-boundary-detail">
              <template>
                <render-member-item mode="view" type="department" :data="departList" />
              </template>
            </div>
          </RenderPermBoundary>
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
  import RenderPermBoundary from '@/components/render-perm-boundary';
  import RenderMemberItem from '@/views/group/common/render-member-display';
  export default {
    components: {
      RenderPermBoundary,
      RenderMemberItem
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
        tableLoading: false,
        isShowGroupError: false,
        selectTableList: [],
        initTabList: [
          {
            name: this.$t(`m.common['用户']`),
            id: 'user',
            count: 0,
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
      },
      isHasUser () {
        return this.userList.length > 0;
      },
      isHasDepartment () {
        return this.departList.length > 0;
      }
    },
    methods: {
      async handleSubmit () {
        const params = {
          members: [...this.userList, ...this.departList].map(({ id, type }) => ({ id, type }))
        };
        try {
          const { code } = await this.$store.dispatch('userOrOrg/cleanGroupMembers', params);
          if (code === 0) {
            this.messageSuccess(this.$t(`m.info['清空用户组成功']`), 3000);
            this.$emit('on-submit', params);
            this.$emit('update:show', false);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleCancel () {
        this.$emit('update:show', false);
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
    /deep/.clear-object {
      .title {
        font-weight: 700;
        font-size: 14px;
        color: #313238;
        margin-bottom: 8px !important;
      }
      .horizontal-item {
        width: 100%;
        padding: 0;
        margin-bottom: 0;
        box-shadow: none;
        display: inline-block;
        .perm-boundary-title {
          display: none;
        }
        .render-form-item {
          margin-bottom: 12px !important;
          .iam-resource-header {
            .type-icon {
              color: #3A84FF;
            }
          }
        }
      }

      .members-boundary-detail {
        padding: 12px 36px 6px 36px;
      }

      .iam-member-display-wrapper {
        margin-left: 0;
        .label {
          display: none;
        }
      }
      .line {
        color: #dcdee5;
        padding: 0 8px;
      }
      .clear-object-tip {
        font-size: 12px;
        color: #c4c6cc;
        .name {
          color: #979ba5;
          font-weight: 700;
        }
      }
    }
  }
  &-footer {
    margin-left: 40px;
    .footer-btn {
      min-width: 88px;
      &:not(&:first-child) {
        margin-left: 8px;
      }
    }
  }
  /deep/ .bk-sideslider-footer {
    border-top: 0;
    height: 32px;
    line-height: 32px;
    background-color: #ffffff !important;
  }
}
</style>

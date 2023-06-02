<template>
  <div>
    <template v-if="isSpaceRoute">
      <div class="authorize-members-content">
        <div
          :class="[
            'members-boundary-title',
            { 'is-required': required }
          ]"
        >
          {{ $t(`m.levelSpace['最大可授权人员边界']`) }}
        </div>
        <section
          class="members-boundary-header"
          data-test-id="grading_btn_showAddMember">
          <bk-button
            theme="default"
            size="small"
            icon="plus-circle-shape"
            class="perm-members-add"
            @click.stop="handleAddMember"
          >
            {{ $t(`m.common['添加']`) }}
          </bk-button>
        </section>
        <div style="margin-top: 9px;" v-if="isAll">
          <div class="all-item">
            <span class="member-name">{{ allText }}</span>
            <span class="display-name">(All)</span>
            <Icon type="close-fill" class="remove-icon" @click="handleDelete" />
          </div>
        </div>
        <template v-else>
          <render-member-item
            v-if="isHasUser"
            :data="users"
            @on-delete="handleDeleteUser"
          />
          <render-member-item
            v-if="isHasDepartment"
            type="department"
            :data="departments"
            @on-delete="handleDeleteDepartment"
          />
        </template>
      </div>
    </template>
    <template v-if="!isSpaceRoute">
      <render-horizontal-block
        :label="renderTitle"
        :label-width="labelWidth"
        :ext-cls="extClsRouteList.includes($route.name) ? 'ext-cls-member-boundary' : ''"
        :required="required">
        <section
          class="action-wrapper"
          @click.stop="handleAddMember"
          data-test-id="grading_btn_showAddMember">
          <Icon bk type="plus-circle-shape" />
          <span>{{ renderText }}</span>
        </section>
        <Icon
          type="info-fill"
          class="info-icon"
          v-bk-tooltips.top="{ content: tips, width: 236, extCls: 'iam-tooltips-cls' }" />
        <template>
          <div style="margin-top: 9px;" v-if="isAll">
            <div class="all-item">
              <span class="member-name">{{ allText }}</span>
              <span class="display-name">(All)</span>
              <Icon type="close-fill" class="remove-icon" @click="handleDelete" />
            </div>
          </div>
          <template v-else>
            <render-member-item
              v-if="isHasUser"
              :data="users"
              @on-delete="handleDeleteUser"
            />
            <render-member-item
              v-if="isHasDepartment"
              type="department"
              :data="departments"
              @on-delete="handleDeleteDepartment"
            />
          </template>
        </template>
      </render-horizontal-block>
    </template>
  </div>
</template>
<script>
  import RenderMemberItem from '../../group/common/render-member-display';
  import { il8n } from '@/language';
  export default {
    name: '',
    components: {
      RenderMemberItem
    },
    props: {
      users: {
        type: Array,
        default: () => []
      },
      departments: {
        type: Array,
        default: () => []
      },
      renderTitle: {
        type: String,
        default: () => il8n('levelSpace', '最大可授权人员边界')
      },
      renderText: {
        type: String,
        default: () => il8n('levelSpace', '选择可授权人员边界')
      },
      allText: {
        type: String,
        default: () => il8n('common', '全员')
      },
      tips: {
        type: String,
        default: () => il8n('grading', '添加成员提示')
      },
      isAll: {
        type: Boolean,
        default: false
      },
      labelWidth: {
        type: Number
      },
      required: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        extClsRouteList: [
          'myManageSpaceCreate',
          'gradingAdminCreate',
          'gradingAdminEdit',
          'secondaryManageSpaceCreate',
          'authorBoundary',
          'authorBoundaryEditFirstLevel',
          'authorBoundaryEditSecondLevel'
        ]
      };
    },
    computed: {
      isHasUser () {
        return this.users.length > 0;
      },
      isHasDepartment () {
        return this.departments.length > 0;
      },
      isSpaceRoute () {
        return this.extClsRouteList.includes(this.$route.name);
      }
    },
    methods: {
      handleAddMember () {
        this.$emit('on-add');
      },

      handleDeleteUser (payload) {
        this.$emit('on-delete', 'user', payload);
      },

      handleDeleteDepartment (payload) {
        this.$emit('on-delete', 'department', payload);
      },

      handleDelete () {
        this.$emit('on-delete-all');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .action-wrapper {
        margin-left: 8px;
        display: inline-block;
        font-size: 14px;
        color: #3a84ff;
        cursor: pointer;
        &:hover {
            color: #699df4;
        }
        i {
            position: relative;
            top: -1px;
            left: 2px;
        }
    }
    .info-icon {
        color: #c4c6cc;
        &:hover {
            color: #3a84ff;
        }
    }
    .all-item {
        position: relative;
        display: inline-block;
        margin: 0 6px 6px 0px;
        padding: 0 10px;
        line-height: 22px;
        background: #f5f6fa;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        font-size: 14px;
        &:hover {
            .remove-icon {
                display: block;
            }
        }
        .member-name {
            display: inline-block;
            max-width: 200px;
            line-height: 17px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            vertical-align: text-top;
            .count {
                color: #c4c6cc;
            }
        }
        .display_name {
            display: inline-block;
            vertical-align: top;
        }
        .remove-icon {
            display: none;
            position: absolute;
            top: -6px;
            right: -6px;
            cursor: pointer;
        }
    }

    .ext-cls-member-boundary {
        box-shadow: none;
    }

    /deep/ .authorize-members-content {
        .perm-members-add {
            width: 88px;
            height: 32px;
            background: #f0f5ff;
            color: #3a84ff;
            border-radius: 2px;
            border: none;
            vertical-align: middle;
            .icon-plus-circle-shape {
                color: #3a84ff !important;
                font-size: 14px;
            }
            span {
                vertical-align: middle;
            }
        }
        .members-boundary-title {
            font-size: 12px;
            position: relative;
            &.is-required {
                &::after {
                    content: "*";
                    color: #ea3636;
                    height: 8px;
                    line-height: 1;
                    display: inline-block;
                    vertical-align: middle;
                    position: absolute;
                    top: 50%;
                    transform: translate(3px,-50%);
                }
            }
        }
        .members-boundary-header {
            margin: 10px 0;
        }
    }
</style>

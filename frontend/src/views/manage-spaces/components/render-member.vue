<template>
  <div>
    <div class="authorize-members-content">
      <div
        :class="[
          'members-boundary-title',
          { 'is-required': required }
        ]"
      >
        {{ $t(`m.levelSpace['最大可授权人员边界']`) }}
      </div>
      <div class="members-boundary-radio">
        <bk-radio-group v-model="radioValue" @change="handleChange">
          <bk-radio :value="true">
            {{ $t(`m.levelSpace['动态继承上级空间']`) }}
          </bk-radio>
          <bk-radio :value="false" class="pl10">
            {{ $t(`m.levelSpace['指定组织架构和人员']`) }}
          </bk-radio>
        </bk-radio-group>
      </div>
      <template v-if="!radioValue">
        <section
          class="members-boundary-header"
          data-test-id="grading_btn_showAddMember">
          <!-- <Icon bk type="plus-circle-shape" />
                <span>{{ $t(`m.levelSpace['选择可授权人员边界']`) }}</span> -->
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
        <!-- <Icon
                type="info-fill"
                class="info-icon"
                v-bk-tooltips.top="{ content: tips, width: 236, extCls: 'iam-tooltips-cls' }" /> -->
      </template>
      <div style="margin-top: 9px;" v-if="isAll">
        <div class="all-item">
          <span class="member-name">{{ $t(`m.common['全员']`) }}</span>
          <span class="display-name">(All)</span>
          <Icon type="close-fill" class="remove-icon" @click="handleDelete" />
        </div>
      </div>
      <template v-else>
        <render-member-item :data="users" @on-delete="handleDeleteUser" v-if="isHasUser" />
        <render-member-item :data="departments" type="department" v-if="isHasDepartment"
          @on-delete="handleDeleteDepartment" />
      </template>
    </div>
  </div>
</template>
<script>
  import RenderMemberItem from '@/views/group/common/render-member-display.vue';
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
      isAll: {
        type: Boolean,
        default: false
      },
      tip: {
        type: String,
        default: ''
      },
      inheritSubjectScope: {
        type: Boolean,
        default: true
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
        tips: this.tip,
        radioValue: true
      };
    },
    computed: {
      isHasUser () {
        return this.users.length > 0;
      },
      isHasDepartment () {
        return this.departments.length > 0;
      }
    },
    watch: {
      inheritSubjectScope (value) {
        this.radioValue = value;
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
      },

      handleChange () {
        this.$emit('on-change', this.radioValue);
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
        font-size: 12px;
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

    /deep/ .authorize-members-content {
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

        .members-boundary-radio {
            margin: 10px 0;
            .bk-radio-text {
                font-size: 12px;
            }
        }

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
    }
</style>

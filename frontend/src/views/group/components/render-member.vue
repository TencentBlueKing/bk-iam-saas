<template>
  <render-horizontal-block
    :label="$t(`m.userGroup['用户组成员']`)"
    ext-cls="iam-user-group-member-wrapper">
    <section class="action-wrapper" @click.stop="handleAddMember">
      <Icon bk type="plus-circle-shape" />
      <span>{{ $t(`m.userGroup['添加组成员']`) }}</span>
    </section>
    <render-member-item :data="users" @on-delete="handleDeleteUser" v-if="isHasUser" />
    <render-member-item :data="departments" type="department" v-if="isHasDepartment"
      @on-delete="handleDeleteDepartment" />
    <render-vertical-block :label="$t(`m.common['授权期限']`)" ext-cls="auth-expired-at">
      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
      <p class="expired-at-error" v-if="expiredAtError">{{ $t(`m.verify['请选择授权期限']`) }}</p>
    </render-vertical-block>
  </render-horizontal-block>
</template>
<script>
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import RenderMemberItem from '../common/render-member-display';
  export default {
    name: '',
    components: {
      IamDeadline,
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
      expiredAtError: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        expiredAt: 15552000
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
    created () {
      this.$emit('on-change', 15552000);
    },
    methods: {
      handleAddMember () {
        this.$emit('on-add');
      },

      handleDeadlineChange (payload) {
        this.expiredAt = payload;
        this.$emit('on-change', payload);
      },

      handleDeleteUser (payload) {
        this.$emit('on-delete', 'user', payload);
      },

      handleDeleteDepartment (payload) {
        this.$emit('on-delete', 'department', payload);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-user-group-member-wrapper {
        .action-wrapper {
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
        .auth-expired-at {
            margin-top: 9px;
            .label {
                margin-bottom: 9px;
                font-weight: 700;
            }
            .expired-at-error {
                margin-top: 5px;
                font-size: 12px;
                color: #ff4d4d;
            }
        }
    }
</style>

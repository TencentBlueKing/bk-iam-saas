<template>
  <div class="template-member-table">
    <member-table :id="curDetailData.id" :name="curDetailData.name" :read-only="readOnly" />
  </div>
</template>

<script>
  import _ from 'lodash';
  import MemberTable from '@/views/group/components/member-table';
  export default {
    components: {
      MemberTable
    },
    props: {
      curDetailData: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        isShowAddMemberDialog: false,
        users: [],
        departments: [],
        addMemberTitle: this.$t(`m.common['添加成员']`),
        readOnly: false
      };
    },
    methods: {
      handleMemberDelete (type, payload) {
        window.changeDialog = true;
        if (type === 'user') {
          this.users.splice(payload, 1);
        } else {
          this.departments.splice(payload, 1);
        }
        this.$set(this.formData, 'template_members', [...this.users, ...this.departments]);
      },

      handleDeleteAll () {
        this.isAll = false;
      },

      handleAddMember () {
        this.isShowAddMemberDialog = true;
      },

      handleCancelAdd () {
        this.isShowAddMemberDialog = false;
      },

      handleSubmitAdd (payload) {
        window.changeAlert = true;
        const { users, departments, isAll } = payload;
        this.isAll = isAll;
        this.users = _.cloneDeep(users);
        this.departments = _.cloneDeep(departments);
        this.$set(this.formData, 'template_members', [...this.users, ...this.departments]);
        this.isShowAddMemberDialog = false;
      }
    }
  };
</script>
<style lang="postcss" scoped>
.template-member-table {
  padding: 0 24px;
}
</style>

<template>
  <div class="template-member-table">
    <div v-if="curDetailData.readonly" class="template-member-table-tip">
      <bk-alert
        type="info"
        :title="$t(`m.memberTemplate['只读人员模板不能添加、删除、复制成员']`)"
      />
    </div>
    <MemberTable
      ref="memberTable"
      :route-mode="'memberTemplate'"
      :id="curDetailData.id"
      :name="curDetailData.name"
      :search-placeholder="placeholder"
      :read-only="curDetailData.readonly"
      :is-show-tab="false"
      :show-expired-at="false"
      :display-set="displaySet"
    />
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
        placeholder: this.$t(`m.memberTemplate['请输入用户/组织，按enter键搜索']`),
        displaySet: {
          customNameWidth: '180px'
        }
      };
    },
    methods: {
      async fetchTempMemberList () {
        // this.$refs.memberTable && this.$refs.memberTable.fetchMemberList();
      },

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
  &-tip {
    padding-bottom: 20px;
  }
}
</style>

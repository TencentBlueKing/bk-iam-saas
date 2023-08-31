<template>
  <div class="iam-user-group-set-wrapper">
    <div class="iam-user-group-set-item">
      <bk-checkbox
        v-model="formData.apply_disable"
        @change="handleChangeSet">
        {{ $t(`m.userGroupSetting['所有用户组不可被申请']`) }}
      </bk-checkbox>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'IamUserGroupSetting',
    data () {
      return {
        formData: {
          apply_disable: false
        }
      };
    },
    async created () {
      await this.getGroupConfig();
    },
    methods: {
      async getGroupConfig () {
        try {
          const { data } = await this.$store.dispatch('userGroupSetting/getUserGroupSetConfig');
          if (data) {
            this.formData = Object.assign({}, { apply_disable: data.apply_disable });
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },
      
      async handleChangeSet () {
        try {
          const { code } = await this.$store.dispatch('userGroupSetting/editUserGroupSetConfig', this.formData);
          if (code === 0) {
            this.messageSuccess(this.$t(`m.userGroupSetting['编辑用户组配置成功']`), 3000);
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-user-group-set-wrapper {
    height: 100%;
    box-sizing: border-box;
    .iam-user-group-set-item{
        padding: 20px;
        min-height: calc(100% - 50px);
        background-color: #ffffff;
        box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .1);
    }
}
</style>

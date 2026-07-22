<template>
  <div class="user-info-wrapper">
    <BkLoginUserInfo
      :userinfo="userInfo"
      :action-list="actionList"
      :render-slot="renderSlot"
    />
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  export default {
    data () {
      return {
        actionList: [
          {
            text: this.$t(`m.common['个人设置']`),
            icon: 'icon iam-icon iamcenter-personal-user',
            theme: 'primary',
            handle: () => {
              window.open(window.BK_PERSONAL_CENTER_URL);
            }
          },
          {
            text: this.$t(`m.nav['退出登录']`),
            icon: 'icon iam-icon iamcenter-logout logout-setting-icon',
            theme: 'danger',
            handle: () => {
              window.localStorage.removeItem('iam-header-title-cache');
              window.localStorage.removeItem('iam-header-name-cache');
              window.localStorage.removeItem('applyGroupList');
              window.location = `${window.LOGIN_SERVICE_URL}/?c_url=${encodeURIComponent(window.location.href)}&is_from_logout=1`;
            }
          }
        ]
      };
    },
    computed: {
      ...mapGetters(['user']),
      userInfo () {
        return {
          name: this.user.username,
          organization: this.user.tenant_id || undefined,
          timezone: this.user.timezone,
          email: ''
        };
      }
    },
    methods: {
      renderSlot (h) {
        return this.user.username;
      }
    }
  };
</script>

<style scoped>
/deep/ .logout-setting-icon {
  font-size: 20px;
}
</style>

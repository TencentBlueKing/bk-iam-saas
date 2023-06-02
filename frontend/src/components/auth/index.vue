<template>
  <div class="bk-login-dialog" v-if="isShow">
    <div class="bk-login-wrapper">
      <iframe :src="iframeSrc" scrolling="no" border="0" width="400" height="400"></iframe>
    </div>
  </div>
</template>

<script>
    /**
     * app-auth
     * @desc 统一登录
     * @example1 <app-auth type="404"></app-auth>
     */

  export default {
    name: 'app-auth',
    data () {
      const loginCallbackURL = window.SITE_URL + 'static/login_success.html?is_ajax=1';
      const iframeSrc = `${window.LOGIN_SERVICE_URL}/?app_code=1&c_url=${loginCallbackURL}`;
      return {
        iframeSrc: iframeSrc,
        isShow: false
      };
    },
    methods: {
      hideLoginModal () {
        this.isShow = false;
      },

      showLoginModal (iframeSrc) {
        const ver = +new Date();
        this.iframeSrc = iframeSrc + '&ver=' + ver;
        setTimeout(() => {
          this.isShow = true;
        }, 1000);
      }
    }
  };
</script>

<style scoped>
    @import './index';
</style>

<template>
  <!-- <div class="bk-login-dialog" v-if="isShow">
    <div class="bk-login-wrapper">
      <iframe :src="iframeSrc" scrolling="no" border="0" width="400" height="400"></iframe>
    </div>
  </div> -->
  <div></div>
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
        isShow: false,
        checkWindowTimer: null,
        loginWindow: null
      };
    },
    mounted () {
      window.addEventListener('message', this.handleMessageListener, false);
      window.addEventListener('beforeunload', () => {
        window.removeEventListener('message', this.handleMessageListener, false);
      });
    },
    destroyed () {
      window.removeEventListener('message', this.handleMessageListener, false);
    },
    methods: {
      hideLoginModal () {
        this.isShow = false;
        if (this.loginWindow) {
          this.loginWindow.close();
          this.loginWindow = null;
        }
      },

      showLoginModal (iframeSrc) {
        const ver = +new Date();
        this.iframeSrc = iframeSrc + '&ver=' + ver;
        if (this.isShow) {
          return;
        }
        // setTimeout(() => {
        //   this.isShow = true;
        // }, 1000);
        this.isShow = true;
        const width = 700;
        const height = 510;
        const { availHeight, availWidth } = window.screen;
        this.loginWindow = window.open(
          this.iframeSrc,
          '_blank',
          `width=${width},
          height=${height},
          left=${(availWidth - width) / 2},
          top=${(availHeight - height) / 2},
          channelmode=0,
          directories=0,
          fullscreen=0,
          location=0,
          menubar=0,
          resizable=0,
          scrollbars=0,
          status=0,
          titlebar=0,
          toolbar=0,
          close=0`
        );
        this.checkWinClose();
      },

      // 轮询判断是否已关闭弹框
      handleCheckWinClose () {
        this.checkWindowTimer && clearTimeout(this.checkWindowTimer);
        this.checkWindowTimer = window.setTimeout(() => {
          if (!this.loginWindow || this.loginWindow.closed) {
            this.hideLoginModal();
            clearTimeout(this.checkWindowTimer);
            return;
          }
          this.handleCheckWinClose();
        }, 300);
      },

      // 监听已登录关闭弹框
      handleMessageListener ({ data = {} }) {
        if (data === null || typeof data !== 'object' || data.target !== 'bk-login' || !this.loginWindow) return;
        this.hideLoginModal();
      }
    }
  };
</script>

<style scoped>
  @import './index';
</style>

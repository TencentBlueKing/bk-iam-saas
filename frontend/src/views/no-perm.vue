<template>
  <div class="bk-exception bk-exception-center" v-show="show">
    <img src="@/images/403.png">
    <h2 class="exception-text">{{ $t(`m.common['权限不足']`) }}</h2>
    <div class="refresh">
      <bk-button theme="default" @click="handleRefreshPage">{{ $t(`m.common['刷新页面']`) }}</bk-button>
    </div>
  </div>
</template>

<script>
    /**
     *  app-exception
     *  @desc 异常页面
     *  @param type {String} - 异常类型，有：404（找不到）、403（权限不足）、500（服务器问题）、building（建设中）
     *  @param delay {Number} - 延时显示
     *  @param text {String} - 显示的文案，默认：有：404（页面找不到了！）、403（Sorry，您的权限不足）、500（）、building(功能正在建设中···)
     *  @example1 <app-exception type="404"></app-exception>
     */
  import { mapGetters } from 'vuex';
  export default {
    name: 'no-perm',
    props: {
      type: {
        type: String,
        default: '404'
      },
      delay: {
        type: Number,
        default: 0
      },
      text: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        curRole: 'staff'
      };
    },
    computed: {
            ...mapGetters(['user'])
    },
    watch: {
      user: {
        handler (value) {
          this.curRole = value.role.type || 'staff';
        },
        immediate: true
      }
    },
    beforeRouteEnter (to, from, next) {
      window.localStorage.removeItem('iam-header-title-cache');
      window.localStorage.removeItem('iam-header-name-cache');
      next();
    },
    created () {
      setTimeout(() => {
        this.show = true;
      }, this.delay);
    },
    methods: {
      handleRefreshPage () {
        this.curRole = this.user.role.type || 'staff';
        if (this.curRole === 'staff' || this.curRole === '') {
          this.$router.push({
            name: 'myPerm'
          });
        } else {
          this.$router.push({
            name: 'permTemplate'
          });
        }
      }
    }
  };
</script>

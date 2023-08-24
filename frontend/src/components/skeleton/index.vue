<template>
  <transition name="skeleton">
    <div v-if="visiable" ref="wraper" class="iam-view-skeleton">
      <component
        :is="realCom"
        :max-width="width"
        :speed="2"
        primary-color="#EBECF3"
        secondary-color="#F6F7FB" />
    </div>
  </transition>
</template>
<script>
  import List from './list';
  const comMap = {
    list: List
  };

  export default {
    name: '',
    props: {
      type: String,
      visiable: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        width: 0
      };
    },
    computed: {
      realCom () {
        if (!comMap.hasOwnProperty(this.type)) {
          return 'div';
        }
        return comMap[this.type];
      }
    },
    mounted () {
      this.init();
      window.addEventListener('resize', this.init);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.init);
      });
    },
    methods: {
      init () {
        if (!this.$refs.wraper) {
          return;
        }
        this.width = this.$refs.wraper.getBoundingClientRect().width;
      }
    }
  };
</script>
<style lang='postcss' scoped>
    .iam-view-skeleton {
        position: absolute;
        padding: 24px;
        top: 0;
        right: 0;
        bottom: 20px;
        left: 0;
        z-index: 2001;
        width: 100%;
        min-height: calc(100vh - 61px);
        background: #f5f7fa;
        opacity: 1;
        visibility: visible;
        overflow: hidden;
    }
    .skeleton-leave-active {
        transition: visibility .7s linear, opacity .5s linear;
    }
    .skeleton-leave-to {
        opacity: 0;
        visibility: hidden;
    }
</style>

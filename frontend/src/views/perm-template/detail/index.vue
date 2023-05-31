<template>
  <div class="iam-perm-template-detail-wrapper">
    <div :style="{ paddingTop: '36px', minHeight: componentWrapperHeight + 'px' }">
      <component
        :is="curComponent"
        :id="id"
        :version="version"
        @on-back="handleBack">
      </component>
    </div>
  </div>
</template>
<script>
  import store from '@/store';
  import { bus } from '@/common/bus';
  import { buildURLParams } from '@/common/url';
  import TemplateDetail from './detail';
  import AttachGroup from './attach-group';

  export default {
    name: '',
    components: {
      TemplateDetail,
      AttachGroup
    },
    data () {
      return {
        componentWrapperHeight: 0,
        curComponent: 'TemplateDetail',
        id: '',
        version: ''
      };
    },
    beforeRouteEnter (to, from, next) {
      const nameCache = window.localStorage.getItem('iam-header-name-cache');
      window.localStorage.setItem('iam-header-title-cache', nameCache);
      store.commit('setHeaderTitle', '');
      next();
    },
    mounted () {
      this.componentWrapperHeight = window.innerHeight - 108 - 2;
      bus.$on('on-tab-change', (name) => {
        this.curComponent = name;
        window.history.replaceState({}, '', `?${buildURLParams({ tab: this.curComponent })}`);
      });
    },
    created () {
      this.id = this.$route.params.id;
      this.version = this.$route.params.version;
      const tab = this.$route.query.tab || 'TemplateDetail';
      this.curComponent = tab;
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-tab-change');
      });
    },
    methods: {
      handleBack (payload) {
        this.curComponent = 'TemplateDetail';
        if (payload) {
          this.$nextTick(() => {
            this.$bkInfo({
              title: '',
              subTitle: this.$t(`m.permTemplateDetail['同步提示']`),
              okText: this.$t(`m.permTemplateDetail['去同步']`),
              cancelText: this.$t(`m.permTemplateDetail['下次再说']`),
              confirmFn: () => {
                this.curComponent = 'AttachGroup';
                bus.$emit('on-set-tab', 'AttachGroup');
              }
            });
          });
        }
      }
    }
  };
</script>

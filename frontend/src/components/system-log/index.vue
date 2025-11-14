<template>
  <bk-dialog
    :value="value"
    ext-cls="iam-system-log-dialog"
    :show-footer="false"
    :width="1105"
    :mask-close="true"
    @after-leave="handleClose">
    <div class="log-layout">
      <div class="layout-left">
        <scroll-faker class="version-wraper">
          <div
            v-for="(log, index) in versionLogs"
            :key="log.version"
            class="flex-between log-tab"
            :class="{ active: index === activeIndex }"
            @click="handleTabChange(index)">
            <div class="log-tab-content">
              <div class="title">{{ log.version }}</div>
              <div class="date">{{ log.date }}</div>
            </div>
            <div v-if="index === 0" class="new-flag">{{ $t(`m.common['当前版本']`) }}</div>
          </div>
        </scroll-faker>
      </div>
      <div class="layout-right">
        <scroll-faker class="content-wraper">
          <div v-bk-xss-html="logContent" class="markdowm-container" />
        </scroll-faker>
        <!-- <Icon bk type="close" class="log-close" @click="handleClose" /> -->
      </div>
    </div>
  </bk-dialog>
</template>
<script>
  import { mapGetters } from 'vuex';
  import { marked } from 'marked';
  import ScrollFaker from '../scroll-faker';

  export default {
    name: 'system-version-log',
    components: {
      ScrollFaker
    },
    props: {
      value: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isShow: true,
        activeIndex: 0
      };
    },
    computed: {
            ...mapGetters(['versionLogs']),
            logContent () {
                if (this.versionLogs.length < 1) {
                    return '';
                }
                return marked(this.versionLogs[this.activeIndex].content);
            }
    },
    created () {
    },
    methods: {
      handleTabChange (index) {
        this.activeIndex = index;
      },
      handleClose () {
        this.activeIndex = 0;
        this.$emit('input', false);
        this.$emit('change', false);
      }
    }
  };
</script>
<style lang='postcss'>
    @import './index.css';
</style>

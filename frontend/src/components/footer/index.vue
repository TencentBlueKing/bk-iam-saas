<template>
  <div class="footer-content" :style="navStickStyle">
    <div class="link-container">
      <!-- <div
        v-for="(item, index) in footerList"
        :key="index + 'link'"
      >
        <a
          class="footer-link"
          :href="item.link"
          target="_blank"
        >
          {{ curLanguageIsCn ? item.text : item.text_en }}
        </a>
        <span v-if="index !== footerList.length - 1" :key="index + 'gap'" class="gap"> | </span>
      </div> -->
      <div v-bk-xss-html="contact" />
    </div>
    <div>{{ copyright }} {{ version }}</div>
  </div>
</template>
  
<script>
  import { mapGetters } from 'vuex';
  export default {
    name: 'FooterBox',
    data () {
      return {
        // footerList: [
        //   {
        //     link: window.ENABLE_ASSISTANT.toLowerCase() === 'true' ? 'wxwork://message/?username=BK助手' : 'https://wpa1.qq.com/KziXGWJs?_type=wpa&qidian=true',
        //     text: '技术支持',
        //     text_en: 'Support '
        //   },
        //   {
        //     link: 'https://bk.tencent.com/s-mart/community',
        //     text: '社区论坛',
        //     text_en: 'Forum'
        //   },
        //   {
        //     link: 'https://bk.tencent.com/index',
        //     text: '产品官网',
        //     text_en: 'Official'
        //   }
        // ],
        version: ''
      };
    },
    computed: {
      ...mapGetters(['versionLogs', 'nav-sticked', 'externalSystemId']),
      ...mapGetters('userGlobalConfig', ['globalConfig']),
      navStickStyle () {
        if (this.externalSystemId) {
          return {
            paddingLeft: '50px'
          };
        } else {
          return {
            paddingLeft: this.navStick ? '284px' : '84px'
          };
        }
      },
      contact () {
        return this.curLanguageIsCn ? this.globalConfig.footerInfoHTML : this.globalConfig.footerInfoHTMLEn;
      },
      copyright () {
        return this.globalConfig.footerCopyrightContent;
      }
    },
    created () {
      if (this.versionLogs.length) {
        this.version = this.versionLogs[0].version;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.footer-content {
  position: relative;
  left: 0;
  bottom: 50px;
  height: 50px;
  line-height: 20px;
  padding: 25px 0;
  display: flex;
  flex-flow: column;
  align-items: center;
  font-size: 12px;
  .link-container {
    display: flex;
    align-items: center;
    height: 20px;
    /deep/ .link-item {
      color: #3a84ff;
      &:hover {
        color: #699df4;
      }
      &:active {
        color: #2761dd;
      }
    }
    .gap {
      margin: -2px 4px 0 4px;
    }
  }
}
</style>

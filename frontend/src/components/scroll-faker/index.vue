<template>
  <div
    ref="scrollWraper"
    class="scroll-faker-warper"
    :style="wraperStyles">
    <div
      ref="scrollContent"
      class="scroll-faker-content"
      :style="scrollContentStyles"
      @scroll="handleContentScroll">
      <slot />
    </div>
    <!-- <div v-if="showScrollBar" class="scroll-faker-scrollbar">
            <div class="scroll-scrollbar-track" :style="scrollTrackStyles" />
        </div> -->
  </div>
</template>
<script>
  import _ from 'lodash';

  export default {
    name: 'scroll-faker',
    props: {
      height: {
        type: Number,
        default: 0
      },
      maxHeight: {
        type: Number
      },
      scrollbarColor: {
        type: String
      },
      trackColor: {
        type: String
      }
    },
    data () {
      return {
        realHeight: 0,
        contentHeight: 1,
        contentScrollHeight: 1,
        contentScrollTop: 0
      };
    },
    computed: {
      wraperStyles () {
        if (this.height < 1) {
          return {};
        }
        return {
          height: `${this.height}px`
        };
      },
      scrollContentStyles () {
        if (this.maxHeight > 0) {
          return {
            'max-height': `${this.maxHeight}px`
          };
        }
        return {};
      },
      speed () {
        return this.contentHeight / this.contentScrollHeight;
      },
      scrollTrackStyles () {
        return {
          height: `${this.contentHeight * this.speed}px`,
          top: `${this.contentScrollTop * this.speed}px`
        };
      },
      showScrollBar () {
        return this.contentScrollHeight > this.contentHeight;
      }
    },
    mounted () {
      const init = _.debounce(() => this.init(), 300);
      window.addEventListener('resize', init);
      const observer = new MutationObserver(() => {
        init();
      });
      observer.observe(this.$refs.scrollContent, {
        subtree: true,
        childList: true
      });
      this.$once('hook:beforeDestroy', () => {
        observer.takeRecords();
        observer.disconnect();
        window.removeEventListener('resize', init);
      });
      init();
    },
    methods: {
      init () {
        if (!this.$refs.scrollContent) {
          return;
        }
        this.contentHeight = this.$refs.scrollContent.getBoundingClientRect().height;
        this.contentScrollHeight = this.$refs.scrollContent.scrollHeight;
      },
      handleContentScroll (event) {
        this.contentScrollTop = event.target.scrollTop;
      }
    }
  };
</script>
<style lang='postcss'>
    .scroll-faker-warper{
        position: relative;
        height: 100%;
        /* &:hover{
            .scroll-faker-scrollbar{
                opacity: 1;
                visibility: visible;
            }
        } */
        .scroll-faker-content{
            height: 100%;
            max-height: 100%;
            min-height: 100%;
            overflow-y: auto;
            /* &::-webkit-scrollbar {
                width: 0;
            } */
            &::-webkit-scrollbar {
                width: 6px;
            }
            &::-webkit-scrollbar-thumb {
                border-radius: 3px;
                background-color: rgba(151, 155, 165, 0.8);
            }
        }
        /* .scroll-faker-scrollbar{
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            z-index: 999;
            width: 6px;
            border-radius: 3px;
            opacity: 0;
            visibility: hidden;
            transition: visibility .1s linear, opacity .15s linear;
            .scroll-scrollbar-track{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 20px;
                border-radius: 3px;
                background: rgba(151, 155, 165, 0.8);
            }
        } */
    }
</style>

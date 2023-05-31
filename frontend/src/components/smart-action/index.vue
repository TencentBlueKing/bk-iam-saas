<template>
  <div class="smart-action-wraper" ref="smartActionWraper">
    <div>
      <slot />
    </div>
    <div ref="actionPosition" :style="positionStyles" role="action-position">
      <div
        ref="dynamicPosition"
        :class="[
          'fixed',
          customClass
        ]"
        :style="{ paddingLeft: externalSystemId ? '50px' : '284px' }"
        style="margin-top: 52px;"
        role="dynamic-position"
      >
        <div :style="styles">
          <slot name="action" />
        </div>
      </div>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { bus } from '@/common/bus';
  import { mapGetters } from 'vuex';

  export default {
    props: {
      offsetTarget: {
        type: String
      },
      fill: {
        type: Number,
        default: 0
      }
    },
    data () {
      return {
        isHide: false,
        paddingLeft: 0,
        offsetLeft: 0
      };
    },
    computed: {
            ...mapGetters(['externalSystemId', 'externalSystemsLayout']),
            classes () {
                if (this.isHide) {
                    return 'fixed';
                }
                return '';
            },
            positionStyles () {
                if (this.isHide) {
                    return {
                        height: '50px',
                        marginTop: '50px'
                    };
                } else {
                    return {
                        marginTop: '52px'
                    };
                }
            },
            styles () {
                const styles = {
                    'padding-left': `${this.offsetLeft + this.fill}px`
                };
                return styles;
            },
            dymaicStyle () {
                if (this.isHide) {
                    return {
                        'padding-left': `${this.paddingLeft}px`
                    };
                }
                return {};
            },
            customClass () {
                if (this.externalSystemsLayout.addMemberBoundary.customFooterClass) {
                    const externalClass = !['addMemberBoundary'].includes(this.$route.name) ? 'external-page-fixed-custom' : 'external-dialog-fixed-custom';
                    return externalClass;
                }
                return '';
            }
    },
    mounted () {
      window.addEventListener('resize', this.smartPosition);
      const observer = new MutationObserver((payload) => {
        this.initPosition();
        this.smartPosition();
      });
      observer.observe(document.querySelector('#app'), {
        subtree: true,
        childList: true,
        attributeName: true,
        characterData: true
      });
      this.$once('hook:beforeDestroy', () => {
        observer.takeRecords();
        observer.disconnect();
        window.removeEventListener('resize', this.smartPosition);
        bus.$off('nav-resize');
      });
      bus.$on('nav-resize', () => {
        this.resetPosition();
      });
      this.initPosition();
    },
    methods: {
      initPosition () {
        if (!this.offsetTarget) {
          return;
        }
        const $target = document.querySelector(`.${this.offsetTarget}`);
        if (!$target) {
          return;
        }
        const actionPositionLeft = this.$refs.actionPosition.getBoundingClientRect().left;
        const offsetTargetLeft = $target.getBoundingClientRect().left;
        this.offsetLeft = offsetTargetLeft - actionPositionLeft;
      },
      resetPosition: _.debounce(function () {
        if (!this.$refs.actionPosition) {
          return;
        }
        const { left } = this.$refs.actionPosition.getBoundingClientRect();
        this.paddingLeft = left;
      }, 300),
      smartPosition: _.debounce(function () {
        if (!this.$refs.actionPosition) {
          return;
        }
        const windowHeight = window.innerHeight;
        const { height, top, left } = this.$refs.actionPosition.getBoundingClientRect();
        this.isHide = height + top + 20 > windowHeight;
        this.paddingLeft = left;
      }, 300)
    }
  };
</script>
<style lang='postcss' scoped>
    .smart-action-wraper {
        .fixed {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            /* z-index: 1999; */
            z-index: 1899;
            display: flex;
            align-items: center;
            height: 52px;
            background: #fff;
            box-shadow: 0px -2px 4px 0px rgba(0, 0, 0, 0.06);
        }

        .external-dialog-fixed-custom,
        .external-page-fixed-custom {
           box-shadow: none;
           border-top: 1px solid #dcdee5;
           padding-left: 0px !important;
        }

        .external-page-fixed-custom {
            padding-left: 24px !important;
        }
    }
</style>

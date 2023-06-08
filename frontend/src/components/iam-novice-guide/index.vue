<template>
  <div class="guide-contaniner" v-if="isSelectManager">
    <div :class="['iam-guide-wrapper', { 'has-animation': hasAnimation }]"
      :style="style">
      <div class="content-wrapper">
        <section class="content-shade">
          <div class="text">{{ content }}</div>
          <div class="knowed-action"
            @click.stop="handleKnowed">
            {{ $t(`m.guide['我知道了']`) }}
          </div>
        </section>
        <div :class="['triangle', direction]"></div>
        <div :class="['triangle', 'mamagerTriangle', 'left']"></div>
      </div>
    </div>
    <div class="content">
      <div class="nav">
        {{ $t(`m.nav['管理空间']`) }}
      </div>
      <div class="select">
        <div>{{ managerName }}</div>
        <Icon type="down-angle" class="select-angle" />
      </div>
    </div>
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    props: {
      content: {
        type: String,
        default: 'default'
      },
      direction: {
        type: String,
        default: 'top',
        validator: (value) => {
          return ['top', 'right', 'bottom', 'left'].includes(value);
        }
      },
      flag: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        hasAnimation: true,
        isSelectManager: true,
        managerName: this.$t(`m.myApproval['超级管理员']`)
      };
    },
    computed: {
            ...mapGetters(['noviceGuide', 'user', 'navCurRoleId', 'roleList']),
            isShow () {
                const types = [
                    'rating_manager_subject_scope',
                    'rating_manager_merge_action',
                    'rating_manager_authorization_scope'
                ];
                if (types.includes(this.type)) {
                    return ['super_manager', 'staff'].includes(this.user.role.type);
                }
                return true;
            }
    },
    watch: {
      flag: {
        handler (value) {
          this.managerName = (this.roleList.length
            && this.roleList.find(e => e.id === this.navCurRoleId)
            && this.roleList.find(e => e.id === this.navCurRoleId).name) || this.$t(`m.myApproval['超级管理员']`);
          this.isSelectManager = value;
        },
        immediate: true,
        deep: true
      }
    },
    created () {
      // 动画显示5秒后关闭
      this.timer = setTimeout(() => {
        this.hasAnimation = false;
        clearTimeout(this.timer);
      }, 5000);
    },
    methods: {
      async handleKnowed () {
        this.$store.commit('updateSelectManager', false);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    $cubic-bezier: cubic-bezier(0.4, 0, 0.2, 1);
    $duration: 0.3s;
    @keyframes float {
        50% {
            transform: translate(10px, 0);
        }
    }
    .guide-contaniner{
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        z-index: 100000;
        background: rgba(0,0,0,.6);
        .iam-guide-wrapper {
            position: absolute;
            width: 240px;
            border-radius: 2px;
            box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, .1);
            transition: left $duration $cubic-bezier;
            z-index: 10;
            top: 58px;
            left: 305px;
            &.has-animation {
                animation: float 1s ease-out infinite;
            }
            .content-wrapper {
                position: relative;
                background: #699df4;
            }
            .content-shade {
                padding: 14px 16px;
                background: #699df4;
            }
            .text {
                line-height: 20px;
                font-size: 12px;
                color: #fff;
                font-weight: normal;
                word-break: break-all;
            }
            .knowed-action {
                position: relative;
                left: 155px;
                margin-top: 5px;
                width: 60px;
                line-height: 20px;
                background: #fff;
                border-radius: 12px;
                font-size: 12px;
                color: #3a84ff;
                text-align: center;
                cursor: pointer;
                &:hover {
                    background: #e1ecff;
                }
            }
            .triangle {
                position: absolute;
                width: 10px;
                height: 10px;
                background: #699df4;
                transform: rotate(45deg);
                z-index: -1;
                &.top {
                    top: -4px;
                    left: 105px;
                    border-bottom: none;
                    border-right: none;
                }
                &.right {
                    top: 50%;
                    transform: rotate(45deg) translateY(-50%);
                    right: -1px;
                    border-bottom: none;
                    border-left: none;
                }
                &.bottom {
                    bottom: -4px;
                    left: 105px;
                    border-left: none;
                    border-top: none;
                }
                &.left {
                    top: 50%;
                    transform: rotate(45deg) translateY(-50%);
                    left: -8px;
                    border-top: none;
                    border-right: none;
                }
            }

            .mamagerTriangle {
                &.left {
                    top: 21%;
                    transform: rotate(45deg) translateY(-50%);
                    left: -8px;
                    border-top: none;
                    border-right: none;
                }
            }
        }

        .content{
            width: 100%;
            .nav{
                padding: 0 20px;
                font-size: 14px;
                width: 100px;
                position: absolute;
                left: 370px;
                top: 16px;
                color: #FFFFFF;
            }
            .select{
                position: absolute;
                background: #374357;
                width: 240px;
                margin: 10px auto;
                color: #FFF;
                font-size: 12px;
                height: 30px;
                line-height: 30px;
                top: 50px;
                left: 9px;
                padding-left: 10px;
                .select-angle{
                    font-size: 18px;
                    margin: 0 2px;
                    position: absolute;
                    color: #FFFFFF;
                    top: 6px;
                    left: 215px;
                }
            }
        }
    }
</style>

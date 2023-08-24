<template>
  <div class="iam-perm-apply-entrance-wrapper">
    <div class="apply-way-wrapper">
      <div v-for="(item, index) in applyList"
        :key="index"
        :class="['apply-way-item', { 'set-margin-left': index !== 0 }]">
        <p class="way-item-title">{{ item.title }}</p>
        <p class="way-item-sub-title">{{ item.subTitle }}</p>
        <div class="way-item-action">
          <bk-button theme="primary" @click="handleToApply(item.router)">
            {{ $t(`m.applyEntrance['立刻申请']`) }}
          </bk-button>
        </div>
        <div class="way-separator"></div>
        <label class="way-label">{{ $t(`m.applyEntrance['场景应用']`) }}：</label>
        <div class="way-tips-wrapper">
          <p
            v-for="(tip, tipIndex) in item.tips"
            :key="tip">
            {{ (tipIndex + 1) + '. ' + tip }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    name: '',
    data () {
      return {
        applyList: [
          {
            router: 'applyJoinUserGroup',
            title: this.$t(`m.applyEntrance['申请加入用户组']`),
            subTitle: this.$t(`m.applyEntrance['申请加入用户组标题']`),
            tips: [this.$t(`m.applyEntrance['申请加入用户组场景1']`), this.$t(`m.applyEntrance['申请加入用户组场景2']`)]
          },
          {
            router: 'applyCustomPerm',
            title: this.$t(`m.applyEntrance['申请自定义权限']`),
            subTitle: this.$t(`m.applyEntrance['申请自定义权限标题']`),
            tips: [this.$t(`m.applyEntrance['申请自定义权限场景1']`), this.$t(`m.applyEntrance['申请自定义权限场景2']`)]
          }
        ]
      };
    },
    methods: {
      handleToApply (payload) {
        this.$router.push({
          name: payload
        });
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-perm-apply-entrance-wrapper {
        .apply-way-wrapper {
            margin-top: 50px;
            display: flex;
            justify-content: center;
            .apply-way-item {
                padding: 50px 40px 0 40px;
                flex: 0 0 514px;
                height: 400px;
                background: #fff;
                border-radius: 2px;
                box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .1);
                &.set-margin-left {
                    margin-left: 40px;
                }
                .way-item-title {
                    margin-bottom: 32px;
                    font-size: 20px;
                    text-align: center;
                }
                .way-item-sub-title {
                    margin-bottom: 21px;
                    font-size: 14px;
                }
                .way-item-action {
                    margin-bottom: 33px;
                    text-align: center;
                }
                .way-separator {
                    margin-bottom: 9px;
                    width: 100%;
                    height: 1px;
                    background: #e7e8ed;
                }
                .way-label {
                    display: block;
                    margin-bottom: 8px;
                }
                .way-tips-wrapper {
                    font-size: 12px;
                    p {
                        line-height: 20px;
                    }
                }
            }
        }
    }
</style>

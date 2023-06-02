<template>
  <div class="iam-system-access-optimize-wrapper">
    <div class="inner">
      <bk-steps class="system-access-step" ref="systemAccessStep" direction="vertical"
        :steps="controllableSteps.steps"
        :controllable="controllableSteps.controllable"
        :cur-step.sync="controllableSteps.curStep"
        :before-change="beforeStepChanged"
        @step-changed="stepChanged">
      </bk-steps>
      <smart-action class="content-wrapper">
        <div class="complete-wrapper">
          <div class="success-msg-wrapper">
            <Icon type="check-fill" class="success-icon"></Icon>
            <div class="success-msg">{{ $t(`m.access['建模完成']`) }}</div>
          </div>
          <div class="help-wrapper">
            <div class="info">
              {{ $t(`m.access['请根据开发语言选择接口实现方式']`) }}
            </div>
            <div class="block-wrapper">
              <div class="block-item">
                <div class="block-title">{{ $t(`m.access['SDK鉴权 (Python/Go )']`) }}</div>
                <div class="block-content">
                  <div class="language">Python SDK</div>
                  <!-- <div class="time">2021-03-23发布</div> -->
                  <bk-link class="link" theme="primary" href="https://github.com/TencentBlueKing/iam-python-sdk" target="_blank">{{ $t(`m.access['访问']`) }}</bk-link>
                </div>
              </div>
              <div class="block-item">
                <div class="block-title"></div>
                <div class="block-content">
                  <div class="language">GO SDK</div>
                  <!-- <div class="time">2021-03-23发布</div> -->
                  <bk-link class="link" theme="primary" href="https://github.com/TencentBlueKing/iam-go-sdk" target="_blank">{{ $t(`m.access['访问']`) }}</bk-link>
                </div>
              </div>
              <div class="block-item special">
                <div class="block-title">{{ $t(`m.access['使用API鉴权(其他)']`) }}</div>
                <div class="block-content">
                  <div class="language"></div>
                  <div class="time"></div>
                  <bk-link class="link" theme="primary" href="https://bk.tencent.com/docs/document/6.0/160/8456" target="_blank">{{ $t(`m.access['查看API鉴权接口']`) }}</bk-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div slot="action">
          <bk-button theme="primary" type="button" @click="goList">
            {{ $t(`m.access['完成']`) }}
          </bk-button>
          <bk-button style="margin-left: 10px;" :loading="downloadLoading" @click="handleDownload"
            v-bk-tooltips.right="'下载完成后请通过migration进行模型注册'">{{ $t(`m.access['下载权限模型配置']`) }}
          </bk-button>
        </div>
      </smart-action>
    </div>
  </div>
</template>
<script>
  import { saveAs } from '@/common/file-saver';
  import beforeStepChangedMixin from '../common/before-stepchange';

  export default {
    mixins: [beforeStepChangedMixin],
    data () {
      return {
        modelingId: '',
        downloadLoading: false,

        controllableSteps: {
          controllable: true,
          steps: [
            { title: this.$t(`m.access['注册系统']`), icon: 1 },
            { title: this.$t(`m.access['注册操作']`), icon: 2 },
            { title: this.$t(`m.access['体验优化']`), icon: 3 },
            { title: this.$t(`m.access['完成']`), icon: 4 }
          ],
          curStep: 4
        }
      };
    },
    mounted () {
      const stepNode = this.$refs.systemAccessStep.$el;
      if (stepNode) {
        const children = Array.from(stepNode.querySelectorAll('.bk-step') || []);
        children.forEach(child => {
          child.classList.remove('current');
        });
        children[3].classList.add('current');
      }
    },
    methods: {
      stepChanged (index) {
      },
      async fetchPageData () {
        const modelingId = this.$route.params.id;
        if (modelingId === null || modelingId === undefined || modelingId === '') {
          return;
        }

        this.modelingId = modelingId;
      },

      goList () {
        this.$router.push({
          name: 'systemAccess'
        });
      },

      async handleDownload () {
        try {
          const res = await this.$store.dispatch('access/downloadJSON', {
            id: this.modelingId,
            data: {
              type: 'migrate'
            }
          });
          if (res.code) {
            this.messageError(this.$t(`m.access['下载权限模型配置失败']`), 1000);
            return;
          }
          const content = JSON.stringify(res.data, null, 2);
          const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
          saveAs(blob, 'config.json');
          this.messageSuccess(this.$t(`m.access['下载权限模型配置成功']`), 1000);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.downloadLoading = false;
        }
      }
    }
  };
</script>
<style lang="postcss" scoped>
    @import './index.css';
</style>

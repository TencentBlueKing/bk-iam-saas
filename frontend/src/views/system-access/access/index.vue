<template>
  <div class="iam-system-access-join-wrapper">
    <div class="inner">
      <bk-steps class="system-access-step" ref="systemAccessStep" direction="vertical"
        :steps="controllableSteps.steps"
        :controllable="controllableSteps.controllable"
        :cur-step.sync="controllableSteps.curStep"
        :before-change="beforeStepChanged"
        @step-changed="stepChanged">
      </bk-steps>
      <smart-action class="base-info-wrapper">
        <render-horizontal-block :label="$t(`m.access['基础信息']`)">
          <section ref="basicInfoContentRef">
            <basic-info :info-data="modelingSystemData" ref="basicInfoRef"
              @on-change="handleBasicInfoChange" />
          </section>
        </render-horizontal-block>
        <!-- <render-horizontal-block :label="$t(`m.common['描述']`)">
                    <bk-form class="desc-form" :model="formData" form-type="vertical">
                        <iam-form-item :label="$t(`m.access['系统中文描述']`)">
                            <bk-input
                                type="textarea"
                                v-model="form"
                                :maxlength="100"
                                :placeholder="$t(`m.verify['请输入系统中文描述']`)">
                            </bk-input>
                        </iam-form-item>
                        <iam-form-item :label="$t(`m.access['系统英文描述']`)">
                            <bk-input
                                type="textarea"
                                v-model="descEn"
                                :maxlength="100"
                                :placeholder="$t(`m.verify['请输入系统英文描述']`)">
                            </bk-input>
                        </iam-form-item>
                    </bk-form>
                </render-horizontal-block> -->

        <div slot="action">
          <bk-button theme="primary" type="button" :loading="submitLoading"
            @click="handleSubmit('systemAccessRegistry')">
            {{ $t(`m.common['下一步']`) }}
          </bk-button>
          <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
        </div>
      </smart-action>
    </div>
  </div>
</template>
<script>
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import BasicInfo from './basic-info';
  import beforeStepChangedMixin from '../common/before-stepchange';

  export default {
    name: '',
    components: {
      BasicInfo
    },
    mixins: [beforeStepChangedMixin],
    data () {
      return {
        modelingId: '',
        modelingSystemData: null,
        formData: {
          id: '',
          name: '',
          name_en: '',
          host: '',
          auth: 'basic',
          healthz: '',
          description: '',
          description_en: ''
        },

        submitLoading: false,

        controllableSteps: {
          controllable: true,
          steps: [
            { title: this.$t(`m.access['注册系统']`), icon: 1 },
            { title: this.$t(`m.access['注册操作']`), icon: 2 },
            { title: this.$t(`m.access['体验优化']`), icon: 3 },
            { title: this.$t(`m.access['完成']`), icon: 4 }
          ],
          curStep: 1
        }
      };
    },
    methods: {
      async fetchPageData () {
        const modelingId = this.$route.params.id;
        if (modelingId === null || modelingId === undefined || modelingId === '') {
          return;
        }

        this.modelingId = modelingId;

        // 编辑
        await this.fetchModeling();
      },

      async fetchModeling () {
        try {
          const res = await this.$store.dispatch('access/getModeling', { id: this.modelingId });
          const systemData = (res.data || {}).system;
          this.modelingSystemData = Object.assign({}, systemData || {});
          this.fillFormData();
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      fillFormData () {
        if (Object.keys(this.modelingSystemData).length) {
          this.formData.id = this.modelingSystemData.id;
          this.formData.name = this.modelingSystemData.name;
          this.formData.name_en = this.modelingSystemData.name_en;
          this.formData.host = this.modelingSystemData.provider_config.host;
          this.formData.auth = this.modelingSystemData.provider_config.auth;
          this.formData.healthz = this.modelingSystemData.provider_config.healthz;
          this.formData.description = this.modelingSystemData.description;
          this.formData.description_en = this.modelingSystemData.description_en;
        }
      },

      handleBasicInfoChange (value) {
        window.changeDialog = true;
        this.formData = Object.assign({}, value);
      },

      async handleSubmit (routerName) {
        const infoFlag = await this.$refs.basicInfoRef.handleValidator();
        if (infoFlag) {
          this.scrollToLocation(this.$refs.basicInfoContentRef);
          return;
        }

        let url = '';
        let params = {};
        if (this.modelingId) {
          url = 'access/updateModeling';
          params = {
            id: this.modelingId,
            data: {
              type: 'system',
              data: {
                id: this.formData.id,
                name: this.formData.name,
                name_en: this.formData.name_en,
                description: this.formData.description,
                description_en: this.formData.description_en,
                provider_config: {
                  host: this.formData.host,
                  auth: this.formData.auth,
                  healthz: this.formData.healthz
                }
              }
            }
          };
        } else {
          url = 'access/createModeling';
          params = {
            id: this.formData.id,
            name: this.formData.name,
            name_en: this.formData.name_en,
            description: this.formData.description,
            description_en: this.formData.description_en,
            provider_config: {
              host: this.formData.host,
              auth: this.formData.auth,
              healthz: this.formData.healthz
            }
          };
        }

        window.changeDialog = false;
        this.submitLoading = true;
        try {
          const res = await this.$store.dispatch(url, params);
          // this.messageSuccess(this.$t(`m.access['新建系统成功']`), 1000)
          this.$router.push({
            name: routerName,
            params: {
              id: this.modelingId || res.data.id
            }
          });
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
          this.submitLoading = false;
        }
      },

      handleCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          this.$router.push({
            name: 'systemAccess'
          });
        }, _ => _);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    @import './index.css';
</style>

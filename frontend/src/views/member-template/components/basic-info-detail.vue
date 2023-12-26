<template>
  <div class="member-template-basic-info"
    v-bkloading="{ isLoading: detailLoading, opacity: 1 }"
  >
    <detail-layout mode="member-template-detail">
      <render-layout>
        <detail-item :label="`${$t(`m.memberTemplate['模板名称']`)}: `">
          <div class="basic-info-value">
            <iam-edit-input
              field="name"
              :mode="formatEdit"
              :placeholder="$t(`m.memberTemplate['请输入模板名称']`)"
              :rules="rules"
              :value="basicInfo.name"
              :remote-hander="handleChangeInfo"
            />
          </div>
        </detail-item>
        <detail-item :label="`${$t(`m.memberTemplate['模板ID']`)}: `">
          <span class="basic-info-value">{{ basicInfo.id }}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.common['创建时间']`)}: `">
          <span class="basic-info-value">{{ basicInfo.created_time }}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.memberTemplate['模板描述']`)}: `">
          <div class="basic-info-value">
            <iam-edit-textarea
              field="description"
              width="600px"
              :mode="formatEdit"
              :placeholder="$t(`m.memberTemplate['请输入模板描述']`)"
              :max-length="255"
              :value="basicInfo.description"
              :remote-hander="handleChangeInfo"
            />
          </div>
        </detail-item>
      </render-layout>
    </detail-layout>
  </div>
</template>

<script>
  import { bus } from '@/common/bus';
  import { isEmojiCharacter } from '@/common/util';
  import RenderLayout from '@/views/group/common/render-layout';
  import DetailLayout from '@/components/detail-layout';
  import DetailItem from '@/components/detail-layout/item';
  import IamEditInput from '@/components/iam-edit/input';
  import IamEditTextarea from '@/components/iam-edit/textarea';
  export default {
    components: {
      RenderLayout,
      DetailLayout,
      DetailItem,
      IamEditInput,
      IamEditTextarea
    },
    props: {
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        detailLoading: false,
        basicInfo: {
          id: 0,
          name: '',
          created_time: '',
          description: ''
        },
        rules: [
          {
            required: true,
            message: this.$t(`m.verify['模板名称必填, 不允许输入表情字符']`),
            trigger: 'blur',
            validator: (value) => {
              return !isEmojiCharacter(value);
            }
          }
        ]
      };
    },
    computed: {
      formatEdit () {
        return this.curDetailData.readonly ? 'detail' : 'edit';
      }
    },
    methods: {
      async fetchDetailInfo () {
        this.detailLoading = true;
        try {
          const { id } = this.curDetailData;
          const { data } = await this.$store.dispatch('memberTemplate/subjectTemplateDetail', { id });
          this.basicInfo = Object.assign(this.basicInfo, data);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.detailLoading = false;
        }
      },

      async handleChangeInfo (payload) {
        const { id, name, description } = this.basicInfo;
        const params = {
          name,
          description,
          id,
        ...payload
        };
        try {
          await this.$store.dispatch('memberTemplate/updateSubjectTemplate', params);
          this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
          const { name, description } = params;
          this.basicInfo = Object.assign(this.basicInfo, {
            name,
            description
          });
          bus.$emit('on-info-change', { id, name, description });
        } catch (e) {
          console.warn('error');
          this.messageAdvancedError(e);
        }
      }
    }
  };
</script>

<style lang="postcss" scoped>
.member-template-basic-info {
  padding-left: 40px;
  .basic-info-value {
    margin-left: 15px;
  }
}
</style>

<template>
  <div class="member-template-basic-info">
    <detail-layout mode="member-template-detail">
      <render-layout>
        <detail-item :label="`${$t(`m.memberTemplate['模板名称']`)}: `">
          <iam-edit-input
            field="name"
            :placeholder="$t(`m.memberTemplate['请输入模板名称']`)"
            :rules="rules"
            :value="basicInfo.name"
            :remote-hander="handleChangeInfo"
          />
        </detail-item>
        <detail-item :label="`${$t(`m.memberTemplate['模板ID']`)}: `">{{
          basicInfo.id
        }}</detail-item>
        <detail-item :label="`${$t(`m.common['创建时间']`)}: `">{{
          basicInfo.created_time
        }}</detail-item>
        <detail-item :label="`${$t(`m.memberTemplate['模板描述']`)}: `">
          <iam-edit-textarea
            field="description"
            width="600px"
            :placeholder="$t(`m.memberTemplate['请输入模板描述']`)"
            :value="basicInfo.description"
            :remote-hander="handleChangeInfo"
          />
        </detail-item>
      </render-layout>
    </detail-layout>
  </div>
</template>

<script>
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
    data () {
      return {
        basicInfo: {
          id: 0,
          name: '',
          created_time: '',
          description: ''
        },
        rules: [
          {
            required: true,
            message: this.$t(`m.verify['请填写名称']`),
            trigger: 'blur'
          }
        ]
      };
    },
    methods: {
      async fetchDetailInfo () {
        this.basicInfo = Object.assign(this.basicInfo, {});
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
          await this.$store.dispatch('role/updateRatingManager', params);
          this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
          const { name, description } = params;
          this.basicInfo = Object.assign(this.basicInfo, {
            name,
            description
          });
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
}
</style>

<template>
  <div class="iam-grading-admin-basic-info-wrapper">
    <detail-layout mode="see">
      <render-layout>
        <detail-item :label="`${$t(`m.levelSpace['名称']`)}：`">
          <iam-edit-input
            field="name"
            :mode="mode"
            :placeholder="$t(`m.verify['请填写名称']`)"
            :rules="rules"
            :value="formData.name"
            :remote-hander="handleUpdateRatingManager" />
        </detail-item>
        <detail-item :label="`${$t(`m.levelSpace['管理员']`)}：`">
          <iam-edit-member
            field="members"
            :value="formData.members"
            @on-change="handleUpdateMembers"
            :remote-hander="handleUpdateRatingManager" />
        </detail-item>
        <detail-item :label="`${$t(`m.common['描述']`)}：`">
          <iam-edit-textarea
            field="description"
            :mode="mode"
            width="600px"
            :max-length="100"
            :value="formData.description"
            :remote-hander="handleUpdateRatingManager" />
        </detail-item>
      </render-layout>
    </detail-layout>
  </div>
</template>
<script>
  import DetailLayout from '@/components/detail-layout';
  import DetailItem from '@/components/detail-layout/item';
  import IamEditInput from '@/components/iam-edit/input';
  import IamEditTextarea from '@/components/iam-edit/textarea';
  import RenderLayout from '@/views/group/common/render-layout';
  import IamEditMember from './iam-edit-member';
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    components: {
      DetailLayout,
      DetailItem,
      IamEditInput,
      IamEditTextarea,
      RenderLayout,
      IamEditMember
    },
    props: {
      data: {
        type: Object,
        default () {
          return {};
        }
      },
      id: {
        type: [String, Number],
        default: ''
      },
      mode: {
        type: String,
        default: 'detail'
      }
    },
    data () {
      return {
        formData: {
          name: '',
          description: '',
          members: [],
          sync_perm: false
        }
      };
    },
    computed: {
            ...mapGetters(['user', 'roleList'])
    },
    watch: {
      data: {
        handler (value) {
          if (Object.keys(value).length) {
            this.formData = Object.assign({}, value);
            this.$store.commit('setHeaderTitle', this.formData.name);
          }
        },
        immediate: true
      }
    },
    created () {
      this.rules = [
        {
          required: true,
          message: this.$t(`m.verify['请填写名称']`),
          trigger: 'blur'
        },
        {
          validator: (value) => {
            return value.length <= 32;
          },
          message: this.$t(`m.verify['名称最长不超过32个字符']`),
          trigger: 'blur'
        },
        {
          validator: (value) => {
            return /^[^\s]*$/g.test(value);
          },
          message: this.$t(`m.verify['名称不允许空格']`),
          trigger: 'blur'
        }
      ];
    },
    methods: {
      handleUpdateRatingManager (payload) {
        const { name, members, description, sync_perm } = this.formData;
        const { type, id } = this.user.role;
        const params = {
          name,
          description,
          members,
          sync_perm,
                    ...payload,
          id: this.id
        };
        const url = ['subset_manager'].includes(type) ? 'spaceManage/updateSecondManagerManager' : 'role/updateRatingManager';
        return this.$store.dispatch(url, params)
          .then(async () => {
            this.messageSuccess(this.$t(`m.info['编辑成功']`), 2000);
            const { name, description, members } = params;
            // this.formData.name = params.name;
            // this.formData.description = params.description;
            // this.formData.members = [...params.members];
            this.formData = Object.assign(this.formData, {
              name,
              description,
              members,
              sync_perm
            });
            const headerTitle = params.name;
            this.$store.commit('setHeaderTitle', headerTitle);
            await this.$store.dispatch('roleList');
            const ExitManager = this.roleList.find(item => !item.is_member && item.id === id);
            if (ExitManager) {
              this.handleExitPermManage();
            }
          }, async (e) => {
            console.warn('error');
            const { code, response } = e;
            if ((response && response.status && [401, 404].includes(response.status))
              || [1902000].includes(code)) {
              this.handleExitPermManage();
            } else {
              this.bkMessageInstance = this.$bkMessage({
                limit: 1,
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
            }
          });
      },

      handleUpdateMembers (payload) {
        this.handleUpdateRatingManager(payload);
      },
            
      // 退出已有二级成员的一级管理空间
      async handleExitPermManage () {
        await this.$store.dispatch('role/updateCurrentRole', { id: 0 });
        await this.$store.dispatch('userInfo');
        this.$store.commit('updateIndex', 0);
        window.localStorage.setItem('index', 0);
        this.messageSuccess(this.$t(`m.info['您已退出当前管理员授权范围']`), 2000);
        this.$router.push({
          name: 'myManageSpace'
        });
      }
    }
  };
</script>
<style lang="postcss">
    .iam-grading-admin-basic-info-wrapper {
        position: relative;
        top: -6px;
    }
</style>

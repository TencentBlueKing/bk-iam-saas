<template>
  <div class="iam-user-group-detail" v-bkloading="{ isLoading, opacity: 1 }">
    <template v-if="!isLoading">
      <render-horizontal-block :label="$t(`m.common['基本信息']`)" ext-cls="basic-info-wrapper">
        <detail-layout mode="see">
          <render-layout>
            <detail-item
              :label="$t(`m.userGroupDetail['用户组名']`)"
              v-if="!externalSystemsLayout.userGroup.groupDetail.hideGroupName">
              <iam-edit-input
                field="name"
                :placeholder="$t(`m.verify['用户组名输入提示']`)"
                :rules="rules"
                :value="basicInfo.name"
                :remote-hander="handleUpdateGroup" />
            </detail-item>
            <detail-item :label="$t(`m.userGroupDetail['ID']`)">{{ basicInfo.id }}</detail-item>
            <detail-item :label="$t(`m.userGroupDetail['创建时间']`)">{{ basicInfo.created_time }}</detail-item>
            <detail-item :label="$t(`m.userGroupDetail['描述']`)">
              <template v-if="externalSystemsLayout.userGroup.groupDetail.hideGroupDescEdit">
                <div
                  :title="basicInfo.description"
                  class="single-hide"
                  style="max-width: 600px;">
                  {{ basicInfo.description }}
                </div>
              </template>
              <template v-else>
                <iam-edit-textarea
                  field="description"
                  width="600px"
                  :placeholder="$t(`m.verify['请输入']`)"
                  :rules="descRules"
                  :value="basicInfo.description"
                  :remote-hander="handleUpdateGroup" />
              </template>
            </detail-item>
          </render-layout>
        </detail-layout>
      </render-horizontal-block>
      <render-horizontal-block ext-cls="user-group-member" :label="$t(`m.userGroup['用户组成员']`)">
        <member-table
          :id="groupId"
          :name="basicInfo.name"
          :read-only="readOnly"
          :data="memberList"
          :count="pagination.count" />
      </render-horizontal-block>
    </template>
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';
  import DetailLayout from '@/components/detail-layout';
  import DetailItem from '@/components/detail-layout/item';
  import IamEditInput from '@/components/iam-edit/input';
  import IamEditTextarea from '@/components/iam-edit/textarea';
  import RenderLayout from '../common/render-layout';
  import MemberTable from '../components/member-table';
    
  export default {
    name: '',
    provide: function () {
      return {
        getGroupAttributes: () => this.groupAttributes
      };
    },
    components: {
      DetailLayout,
      DetailItem,
      IamEditInput,
      IamEditTextarea,
      RenderLayout,
      MemberTable
    },
    props: {
      id: {
        type: [String, Number],
        default: ''
      },
      type: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        isLoading: false,
        basicInfo: {
          name: '',
          id: '',
          created_time: '',
          description: ''
        },
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        groupAttributes: {
          source_type: '',
          source_from_role: false
        },
        memberList: [],
        groupId: '',
        readOnly: false // 当前用户组是否可编辑成员
      };
    },
    computed: {
            ...mapGetters(['externalSystemsLayout'])
    },
    watch: {
      id: {
        handler (value) {
          this.groupId = value;
          window.parent.postMessage({ type: 'IAM', data: { tab: 'group_detail' }, code: 'change_group_detail_tab' }, '*');
          this.handleInit(value);
        },
        immediate: true
      }
    },
    created () {
      this.rules = [
        {
          required: true,
          message: this.$t(`m.verify['用户组名必填']`),
          trigger: 'blur'
        },
        // {
        //     validator: (value) => {
        //         const reg = /^[^\s]*$/g
        //         return reg.test(value)
        //     },
        //     message: this.$t(`m.verify['用户组名不允许空格']`),
        //     trigger: 'blur'
        // },
        {
          validator: (value) => {
            return value.length <= 32;
          },
          message: this.$t(`m.verify['用户组名最长不超过32个字符']`),
          trigger: 'blur'
        },
        {
          validator: (value) => {
            return value.length >= 5;
          },
          message: this.$t(`m.verify['用户组名最短不少于5个字符']`),
          trigger: 'blur'
        }
      ];
      this.descRules = [
        {
          required: false,
          message: this.$t(`m.verify['请输入']`),
          trigger: 'blur'
        }
        // {
        //     validator: (value) => {
        //         return value.length >= 10;
        //     },
        //     message: this.$t(`m.verify['描述最短不少于10个字符']`),
        //     trigger: 'blur'
        // }
      ];
    },
    methods: {
      async handleInit (payload) {
        this.isLoading = true;
        this.$emit('on-init', true);
        if (this.$parent.fetchDetail) {
          try {
            const { data } = await this.$parent.fetchDetail(payload);
            const { id, name, created_time, description, readonly, attributes } = data;
            this.basicInfo = Object.assign({}, {
              id,
              name,
              created_time,
              description
            });
            this.readOnly = readonly;
            this.groupAttributes = Object.assign(this.groupAttributes, attributes);
            // this.pagination.count = data.count || 0;
            // this.memberList.splice(0, this.memberList.length, ...(data.results || []));
            window.localStorage.setItem('iam-header-title-cache', name);
            window.localStorage.setItem('iam-header-name-cache', name);
            this.$store.commit('setHeaderTitle', name);
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
            this.isLoading = false;
            this.$emit('on-init', false);
          }
        }
      },
            
      fetchMemberList (payload) {
        const params = {
          id: payload,
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1)
        };
        return this.$store.dispatch('userGroup/getUserGroupMemberList', params);
      },

      handleUpdateGroup (payload) {
        const { name, description } = this.basicInfo;
        const params = {
          name: name.trim(),
          description,
                    ...payload,
          id: this.groupId
        };
        return this.$store.dispatch('userGroup/editUserGroup', params)
          .then(() => {
            this.messageSuccess(this.$t(`m.info['编辑成功']`), 2000);
            this.basicInfo.name = params.name;
            this.basicInfo.description = params.description;
            const headerTitle = `${this.basicInfo.name}(#${this.id})`;
            window.localStorage.setItem('iam-header-title-cache', headerTitle);
            this.$store.commit('setHeaderTitle', headerTitle);
          }, (e) => {
            console.warn('error');
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText
            });
          });
      }
    }
  };
</script>
<style lang="postcss">
    .iam-user-group-detail {
        position: relative;
        min-height: calc(100vh - 210px);
        .user-group-member {
            margin-bottom: 0 !important;
        }
        .basic-info-wrapper {
            .content {
                position: relative;
                top: -6px;
            }
        }
    }
</style>

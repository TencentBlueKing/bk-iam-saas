<template>
  <div class="iam-grading-admin-detail-wrapper">
    <p class="edit-action">
      {{curRoleType === 'staff' ? $t(`m.levelSpace['如需编辑授权边界的内容请点击']`) : $t(`m.grading['如需编辑管理空间的内容请点击']`)}}
      <bk-button
        theme="primary"
        text
        size="small"
        @click="handleEdit">
        {{ $t(`m.common['编辑']`) }}
      </bk-button>
    </p>
    <div class="detail-content-wrapper">
      <render-horizontal-block :label="$t(`m.common['基本信息']`)">
        <basic-info
          :data="formData"
          ref="basicInfoRef"
          :id="$route.params.id"
          @on-change="handleBasicInfoChange" />
      </render-horizontal-block>

      <!-- <p class="tips">{{ infoText }}</p> -->
      <!-- <render-perm
                :title="$t(`m.levelSpace['最大可授权操作和资源边界']`)"
                :perm-length="policyList.length"
                :expanded.sync="curExpanded"
                ext-cls="iam-grade-detail-panel-cls">
                <render-detail-table :actions="policyList" />
            </render-perm>

            <render-horizontal-block
                :label="$t(`m.levelSpace['最大可授权人员边界']`)"
                :label-width="renderLabelWidth('member')"
            >
                <template v-if="isAll">
                    <span class="all-item">{{ $t(`m.common['全员']`) }}(All)</span>
                </template>
                <template v-else>
                    <p class="member-info">
                        <template v-if="users.length > 0">
                            {{ $t(`m.common['共']`) }} <span class="count">
                                {{ users.length }}</span>
                                 {{ $t(`m.common['个用户']`) }}
                        </template>
                        <template v-if="departments.length > 0">
                            <template v-if="users.length > 0">，</template>
                            <span class="count">{{ departments.length }}</span> {{ $t(`m.common['个组织']`) }}
                        </template>
                    </p>
                    <render-member-item :data="users" v-if="isHasUser" mode="view" />
                    <render-member-item :data="departments" type="department" mode="view" v-if="isHasDepartment" />
                </template>
            </render-horizontal-block> -->
      <RenderPermBoundary
        :title="$t(`m.nav['授权边界']`)"
        :modules="['resourcePerm', 'membersPerm']"
        :resource-title="$t(`m.levelSpace['最大可授权操作和资源边界']`)"
        :members-title="$t(`m.levelSpace['最大可授权人员边界']`)"
        :perm-length="policyList.length"
        :user-length="users.length"
        :depart-length="departments.length"
        @on-expanded="handleExpanded"
        ext-cls="iam-grade-detail-panel-cls"
      >
        <div
          slot="resourcePerm"
          class="resources-boundary-detail"
        >
          <render-detail-table :actions="policyList" />
        </div>
        <div
          slot="membersPerm"
          class="members-boundary-detail"
        >
          <template>
            <render-member-item
              :data="users"
              mode="view"
              v-if="isHasUser"
            />
            <render-member-item
              mode="view"
              type="department"
              :data="departments"
              v-if="isHasDepartment" />
          </template>
        </div>
      </RenderPermBoundary>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import store from '@/store';
  // import RenderPerm from '@/components/render-perm';
  import RenderPermBoundary from '@/components/render-perm-boundary';
  import basicInfo from '../components/basic-info-detail';
  import RenderMemberItem from '../../group/common/render-member-display';
  import renderDetailTable from '../components/render-instance-detail-table';
  import { renderLabelWidth } from '@/common/util';
  export default {
    name: '',
    components: {
      // RenderPerm,
      RenderPermBoundary,
      basicInfo,
      RenderMemberItem,
      renderDetailTable
    },
    data () {
      return {
        renderLabelWidth,
        formData: {
          name: '',
          description: '',
          members: []
        },
        users: [],
        departments: [],
        infoText: this.$t(`m.grading['选择提示']`),
        policyList: [],
        curExpanded: false,
        isAll: false
      };
    },
    beforeRouteEnter (to, from, next) {
      store.commit('setHeaderTitle', '');
      next();
    },
    computed: {
            ...mapGetters(['user']),
            isHasUser () {
                return this.users.length > 0;
            },
            isHasDepartment () {
                return this.departments.length > 0;
            },
            curRoleType () {
                return this.user.role.type;
            }
    },
    methods: {
      /**
       * @description: fetchPageData 进入页面时在路由文件中统一请求 @/router/index.js
       * @param {*}
       * @return {*}
       */
      async fetchPageData () {
        await this.fetchRatingManagerDetail();
      },

      async fetchRatingManagerDetail () {
        try {
          const res = await this.$store.dispatch('role/getRatingManagerDetail', { id: this.$route.params.id });
          this.getDetailData(res.data);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      getDetailData (payload) {
        const { name, description, members, authorization_scopes } = payload;
        const authorizationScopes = [];
        authorization_scopes.forEach(item => {
          authorizationScopes.push({
            actions: item.actions,
            system_id: item.system.id
          });
        });
        this.formData = Object.assign({}, {
          name,
          description: description || '--',
          members
        });
        this.$store.commit('setHeaderTitle', name);
        const departments = [];
        const users = [];
        payload.subject_scopes.forEach(item => {
          if (item.type === 'department') {
            departments.push({
              name: item.name,
              count: item.member_count,
              fullName: item.full_name,
              full_name: item.full_name || item.fullName
            });
          }
          if (item.type === 'user') {
            users.push({
              name: item.name,
              username: item.id,
              full_name: item.full_name || item.fullName
            });
          }
          if (item.id === '*' && item.type === '*') {
            departments.push({
              name: this.$t(`m.common['全员']`),
              count: 'All',
              full_name: `${this.$t(`m.common['全员']`)}(All)`
            });
          }
        });

        this.isAll = payload.subject_scopes.some(item => item.id === '*' && item.type === '*');

        this.users.splice(0, this.users.length, ...users);
        this.departments.splice(0, this.departments.length, ...departments);

        const tempActions = [];
        payload.authorization_scopes.forEach(item => {
          item.actions.forEach(act => {
            const obj = {
                            ...act,
                            system_id: item.system.id,
                            system_name: item.system.name
            };
            tempActions.push(obj);
          });
        });
        this.policyList = _.cloneDeep(tempActions);
      },

      handleEdit () {
        this.$router.push({
          name: 'gradingAdminEdit',
          params: {
            id: this.$route.params.id
          }
        });
      },

      handleBasicInfoChange (field, data) {
        this.formData[field] = data;
      }
    }
  };
</script>
<style lang="postcss">
    .iam-grading-admin-detail-wrapper {
        padding-top: 10px;
        .edit-action {
            font-size: 12px;
        }

        .iam-grade-detail-panel-cls {
            margin-bottom: 16px;
        }

        .detail-content-wrapper {
            margin-top: 13px;
            .tips {
                line-height: 20px;
                font-size: 12px;
            }
            .member-info {
                margin-left: 10px;
                margin-bottom: 9px;
                font-size: 14px;
                color: #979ba5;
                .count {
                    font-weight: 600;
                }
            }
        }
        /* .horizontal-item .label {
            width: 126px;
        } */
        /* .horizontal-item .content {
            margin-left: 42px;
        } */
       /* .horizontal-item .content .member-item {
            margin-left: -42px;
        } */
    }
</style>

<template>
  <div class="iam-grading-admin-detail-wrapper" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <p class="edit-action" v-show="curRoleType !== 'subset_manager' && curRoleType !== 'staff'">
      {{ $t(`m.levelSpace['如需编辑授权边界的内容请点击']`) }}
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
          :id="id"
          @on-change="handleBasicInfoChange" />
      </render-horizontal-block>

      <render-perm
        :title="$t(`m.levelSpace['最大可授权操作和资源边界']`)"
        :perm-length="policyList.length"
        :expanded.sync="curExpanded"
        ext-cls="iam-grade-detail-panel-cls">
        <render-detail-table :actions="policyList" />
      </render-perm>

      <render-perm
        :title="$t(`m.levelSpace['最大可授权人员边界']`)">
        <template v-if="isAll">
          <span class="all-item">{{ $t(`m.common['全员']`) }}(All)</span>
        </template>
        <template v-else>
          <p class="member-info">
            <!-- eslint-disable max-len -->
            <template v-if="users.length > 0">
              {{ $t(`m.common['共']`) }} <span class="count">{{ users.length }}</span> {{ $t(`m.common['个用户']`) }}
            </template>
            <template v-if="departments.length > 0">
              <template v-if="users.length > 0">{{ $t(`m.common['，']`) }}</template>
              <span class="count">{{ departments.length }}</span> {{ $t(`m.common['个组织']`) }}
            </template>
          </p>
          <render-member-item :data="users" v-if="isHasUser" mode="view" />
          <render-member-item :data="departments" type="department" mode="view" v-if="isHasDepartment" />
        </template>
      </render-perm>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import BasicInfo from '@/views/manage-spaces/components/basic-info-detail';
  import RenderDetailTable from '@/views/manage-spaces/components/render-instance-detail-table';
  import RenderPerm from '@/components/render-perm';
  import RenderMemberItem from '@/views/group/common/render-member-display';
  export default {
    components: {
      BasicInfo,
      RenderPerm,
      RenderMemberItem,
      RenderDetailTable
    },
    data () {
      return {
        users: [],
        departments: [],
        policyList: [],
        infoText: this.$t(`m.grading['选择提示']`),
        curExpanded: false,
        isAll: false,
        loading: false,
        id: 0
      };
    },
    computed: {
            ...mapGetters([
                'user'
            ]),
            isHasUser () {
                return this.users.length > 0;
            },
            isHasDepartment () {
                return this.departments.length > 0;
            },
            curRoleId () {
                return this.user.role.id;
            },
            curRoleType () {
                return this.user.role.type;
            }
    },
    watch: {
      '$route': {
        handler (value) {
          this.fetchRatingManagerDetail();
        },
        immediate: true
      }
    },
    methods: {
      async fetchRatingManagerDetail () {
        this.id = this.$route.params.id;
        if (this.curRoleId || this.id) {
          try {
            this.loading = true;
            const fetchUrl = (this.curRoleType === 'subset_manager' || this.curRoleType === 'staff') ? 'spaceManage/getSecondManagerDetail' : 'role/getRatingManagerDetail';
            const res = await this.$store.dispatch(fetchUrl, { id: this.curRoleId || this.id });
            this.getDetailData(res.data);
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          } finally {
            this.loading = false;
          }
        }
      },

      getDetailData (payload) {
        const { name, description, members, authorization_scopes } = payload;
        const authorizationScopes = [];
        const tempActions = [];
        const departments = [];
        const users = [];
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
        payload.subject_scopes.forEach(item => {
          if (item.type === 'department') {
            departments.push({
              name: item.name,
              count: item.member_count,
              fullName: item.full_name
            });
          }
          if (item.type === 'user') {
            users.push({
              name: item.name,
              username: item.id
            });
          }
        });
        this.isAll = payload.subject_scopes.some(item => item.id === '*' && item.type === '*');
        this.users.splice(0, this.users.length, ...users);
        this.departments.splice(0, this.departments.length, ...departments);
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
          name: this.curRoleType === 'subset_manager' ? 'authorBoundaryEditSecondLevel' : 'authorBoundaryEditFirstLevel',
          params: {
            id: this.curRoleId
          }
        });
      },

      handleBasicInfoChange (field, data) {
        this.formData[field] = data;
      }
    }
  };
</script>

<style lang="postcss" scoped>
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

        .all-item {
            font-size: 12px;
            margin-left: 10px;
            color: #979ba5;
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

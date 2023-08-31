<template>
  <div class="iam-perm-renewal-table-wrapper" v-bkloading="{ isLoading: loading || isLoading, opacity: 1 }">
    <bk-table
      v-show="!loading"
      :data="tableList"
      size="small"
      ref="permTableRef"
      ext-cls="perm-renewal-table"
      :outer-border="false"
      :header-border="false"
      :max-height="500"
      :pagination="pagination"
      @page-change="pageChange"
      @page-limit-change="limitChange"
      @select="handlerChange"
      @select-all="handlerAllChange">
      <bk-table-column type="selection" align="center" :selectable="getIsSelect"></bk-table-column>
      <template v-for="item in tableProps">
        <bk-table-column
          v-if="item.prop === 'system'"
          :filters="systemFilter"
          :filter-method="systemFilterMethod"
          :filter-multiple="false"
          :key="item.prop"
          :label="item.label"
          :prop="item.prop">
          <template slot-scope="{ row }">
            <span :title="row.system ? row.system.name || '' : ''">
              {{ row.system ? row.system.name || '' : '' }}
            </span>
          </template>
        </bk-table-column>
        <template v-else-if="item.prop === 'name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span
                class="renewal-user-group-name"
                :title="row.name"
                @click="handleViewDetail(row)"
              >
                {{ row.name || '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'role.name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span
                :title="row.role && row.role.name ? row.role.name : ''"
              >
                {{ row.role ? row.role.name : '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'role_members'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="300">
            <template slot-scope="{ row, $index }">
              <template v-if="row.role_members && row.role_members.length">
                <iam-edit-member-selector
                  mode="detail"
                  field="members"
                  width="200"
                  :placeholder="$t(`m.verify['请输入']`)"
                  :value="row.role_members"
                  :index="$index"
                />
              </template>
              <template v-else>--</template>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'action'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span>{{ row.action ? row.action.name || '' : '' }}</span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'policy'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
          >
            <template slot-scope="{ row }">
              <template v-if="row.policy.resource_groups && row.policy.resource_groups.length">
                <div
                  v-for="(_, _index) in row.policy.resource_groups"
                  :key="_.id"
                  class="related-resource-perm"
                  :class="
                    row.policy.resource_groups === 1 || _index === row.policy.resource_groups.length - 1
                      ? ''
                      : 'related-resource-perm-border'
                  "
                >
                  <p
                    class="related-resource-perm-item"
                    v-for="related in _.related_resource_types"
                    :key="related.type"
                  >
                    <render-resource-popover
                      :key="related.type"
                      :data="related.condition"
                      :value="`${related.name}: ${related.value}`"
                      :max-width="380"
                      @on-view="handleViewResource(_, row.policy)"
                    />
                  </p>
                  <Icon
                    v-if="isShowPreview(row.policy)"
                    type="detail-new"
                    class="view-icon"
                    :title="$t(`m.perm['查看实例资源权限组']`)"
                    @click.stop="handleViewResource(_, row.policy)"
                  />
                </div>
              </template>
              <template v-else>
                <span>{{ $t(`m.common['无需关联实例']`) }}{{ policyIndex}}</span>
              </template>
            </template>
          </bk-table-column>
        </template>
        <template v-else>
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <render-expire-display
                v-if="item.prop === 'expired_at'"
                :selected="currentSelectList.map(v => v.id).includes(row.id)"
                :renewal-time="renewalTime"
                :cur-time="row.expired_at" />
              <span v-else :title="row[item.prop] || ''">{{ row[item.prop] || '--'}}</span>
            </template>
          </bk-table-column>
        </template>
      </template>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyRenewalData.type"
          :empty-text="emptyRenewalData.text"
          :tip-text="emptyRenewalData.tip"
          :tip-type="emptyRenewalData.tipType"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>

    <bk-sideslider
      :is-show.sync="isShowSideSlider"
      :width="sliderWidth"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      >
      <div slot="header" class="iam-my-custom-perm-silder-header">
        <span>{{ sideSliderTitle }}</span>
      </div>
      <div slot="content">
        <RenderDetail
          ref="detailComRef"
          :data="previewData"
        />
      </div>
    </bk-sideslider>

    <render-perm-side-slider
      :show="isShowPermSideSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      :show-member="false"
      @animation-end="handleDetailAnimationEnd"
    />
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import RenderExpireDisplay from '@/components/render-renewal-dialog/display';
  import RenderResourcePopover from '../components/prem-view-resource-popover';
  import RenderDetail from './render-detail';
  import RenderPermSideSlider from '@/views/perm/components/render-group-perm-sideslider';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import PermPolicy from '@/model/my-perm-policy';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { formatCodeData } from '@/common/util';

  // 过期时间的天数区间
  const EXPIRED_DISTRICT = 15;

  export default {
    name: '',
    components: {
      RenderExpireDisplay,
      RenderDetail,
      RenderResourcePopover,
      RenderPermSideSlider,
      IamEditMemberSelector
    },
    props: {
      type: {
        type: String,
        default: 'group'
      },
      renewalTime: {
        type: Number,
        default: 15552000
      },
      data: {
        type: Array,
        default: () => []
      },
      loading: {
        type: Boolean,
        default: false
      },
      count: {
        type: Number,
        default: () => 0
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: '',
            text: '',
            tip: '',
            tipType: ''
          };
        }
      }
    },
    data () {
      return {
        tableList: [],
        allData: [],
        currentSelectList: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        tableProps: [],
        systemFilter: [],
        isLoading: false,
        emptyRenewalData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        isShowSideSlider: false,
        isShowPermSideSlider: false,
        sideSliderTitle: '',
        curGroupName: '',
        curGroupId: -1,
        previewData: [],
        sliderWidth: 960
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isShowPreview () {
        return (payload) => {
          return payload.policy_id;
        };
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      type: {
        handler (newValue, oldValue) {
          this.tableProps = this.getTableProps(newValue);
          if (oldValue && oldValue !== newValue) {
            this.pagination = Object.assign(this.pagination, {
              current: 1,
              limit: 10
            });
          }
        },
        immediate: true
      },
      currentSelectList: {
        handler (value) {
          const getTimestamp = payload => {
            if (this.renewalTime === PERMANENT_TIMESTAMP) {
              return this.renewalTime;
            }
            if (payload < this.user.timestamp) {
              return this.user.timestamp + this.renewalTime;
            }
            return payload + this.renewalTime;
          };
          const templateList = value.map(item => {
            return {
              ...item,
              expired_at: getTimestamp(item.expired_at)
            };
          });
          this.$emit('on-select', this.type, templateList);
        },
        immediate: true,
        deep: true
      },
      renewalTime (value) {
        const getTimestamp = payload => {
          if (value === PERMANENT_TIMESTAMP) {
            return value;
          }
          if (payload < this.user.timestamp) {
            return this.user.timestamp + value;
          }
          return payload + value;
        };
        const templateList = this.currentSelectList.map(item => {
          return {
            ...item,
            expired_at: getTimestamp(item.expired_at)
          };
        });
        this.$emit('on-select', this.type, templateList);
      },
      data: {
        handler (value) {
          this.allData = _.cloneDeep(value);
          this.pagination = Object.assign(this.pagination, { count: this.count });
          const data = this.getCurPageData();
          this.tableList.splice(0, this.tableList.length, ...data);
          // this.currentSelectList = this.tableList.filter(item =>
          //     this.getDays(item.expired_at) < EXPIRED_DISTRICT);
          // if (this.type === 'custom') {
          //     this.tableList.forEach(item => {
          //         if (!this.systemFilter.find(subItem => subItem.value === item.system.id)) {
          //             this.systemFilter.push({
          //                 text: item.system.name,
          //                 value: item.system.id
          //             });
          //         }
          //     });
          // }
          this.$nextTick(() => {
            const tableItem = {
              group: () => {
                this.currentSelectList = this.tableList.filter(item =>
                  this.getDays(item.expired_at) < EXPIRED_DISTRICT);
                this.tableList.forEach(item => {
                  if (item.role_members && item.role_members.length) {
                    item.role_members = item.role_members.map(v => {
                      return {
                        username: v,
                        readonly: false
                      };
                    });
                  }
                  if (this.currentSelectList.map(_ => _.id).includes(item.id)) {
                    this.$refs.permTableRef
                      && this.$refs.permTableRef.toggleRowSelection(item, true);
                  }
                });
              },
              custom: () => {
                this.currentSelectList = this.allData.filter(item =>
                  this.getDays(item.expired_at) < EXPIRED_DISTRICT);
                this.allData.forEach(item => {
                  if (!this.systemFilter.find(subItem => subItem.value === item.system.id)) {
                    this.systemFilter.push({
                      text: item.system.name,
                      value: item.system.id
                    });
                  }
                  if (this.currentSelectList.map(_ => _.id).includes(item.id)) {
                    this.$refs.permTableRef
                      && this.$refs.permTableRef.toggleRowSelection(item, true);
                  }
                  item.policy = new PermPolicy(item.policy);
                });
              }
            };
            return tableItem[this.type] ? tableItem[this.type]() : tableItem['group']();
          });
        },
        immediate: true
      },
      count: {
        handler (value) {
          this.pagination.count = value;
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.emptyRenewalData = value;
        },
        immediate: true
      }
    },
    methods: {
      getDays (payload) {
        const dif = payload - this.user.timestamp;
        if (dif < 1) {
          return 0;
        }
        return Math.ceil(dif / (24 * 3600));
      },

      getIsSelect () {
        return this.tableList.length > 0;
      },

      getTableProps (payload) {
        if (payload === 'group') {
          return [
            { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
            { label: this.$t(`m.common['描述']`), prop: 'description' },
            { label: this.$t(`m.grading['管理空间']`), prop: 'role.name' },
            { label: this.$t(`m.levelSpace['管理员']`), prop: 'role_members' },
            { label: this.$t(`m.common['有效期']`), prop: 'expired_at' }
          ];
        }
        return [
          { label: this.$t(`m.common['操作']`), prop: 'action' },
          { label: this.$t(`m.common['资源实例']`), prop: 'policy' },
          { label: this.$t(`m.common['所属系统']`), prop: 'system' },
          { label: this.$t(`m.common['有效期']`), prop: 'expired_at' }
        ];
      },

      systemFilterMethod (value, row, column) {
        const property = column.property;
        return row[property].id === value;
      },

      pageChange (page = 1) {
        this.pagination = Object.assign(
          this.pagination,
          {
            current: page
          }
        );
        this.fetchTableData();
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(
          this.pagination,
          {
            current: 1,
            limit: currentLimit
          }
        );
        this.fetchTableData();
      },

      handlerAllChange (selection) {
        const tabItem = {
          group: () => {
            this.currentSelectList = [...selection];
          },
          custom: () => {
            // 直接点全选按钮切换数量为当前页条数，处理点击其他页面数据再点全选数量不对等问题
            if (selection.length === this.tableList.length || selection.length === this.allData.length) {
              this.currentSelectList = [...this.allData];
              this.currentSelectList.forEach(item => {
                this.$refs.permTableRef
                  && this.$refs.permTableRef.toggleRowSelection(item, true);
              });
            } else {
              this.currentSelectList = [];
              this.$refs.permTableRef.clearSelection();
            }
          }
        };
        return tabItem[this.type] ? tabItem[this.type]() : tabItem['group']();
      },

      handlerChange (selection, row) {
        this.currentSelectList = [...selection];
      },

      handleViewDetail (payload) {
        this.curGroupName = payload.name;
        this.curGroupId = payload.id;
        this.isShowPermSideSlider = true;
      },

      handleViewResource (groupItem, payload) {
        const params = [];
        if (groupItem.related_resource_types.length) {
          groupItem.related_resource_types.forEach(item => {
            const { name, type, condition } = item;
            params.push({
              name: type,
              label: this.$t(`m.info['tab操作实例']`, { value: name }),
              tabType: 'resource',
              data: condition,
              systemId: item.system_id,
              resource_group_id: groupItem.id
            });
          });
        }
        this.previewData = _.cloneDeep(params);
        this.sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowSideSlider = true;
      },

      handleAnimationEnd () {
        this.sideSliderTitle = '';
        this.previewData = [];
      },

      getCurPageData (page = 1) {
        let startIndex = (page - 1) * this.pagination.limit;
        let endIndex = page * this.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.allData.length) {
          endIndex = this.allData.length;
        }
        return this.allData.slice(startIndex, endIndex);
      },

      async fetchTableData () {
        this.isLoading = true;
        try {
          const { current, limit } = this.pagination;
          const tabItem = {
            group: async () => {
              const userGroupParams = {
                page_size: limit,
                page: current
              };
              if (this.externalSystemId) {
                userGroupParams.system_id = this.externalSystemId;
              }
              const { code, data } = await this.$store.dispatch('renewal/getExpireSoonGroupWithUser', userGroupParams);
              this.tableList = data.results || [];
              this.tableList.forEach(item => {
                if (item.role_members && item.role_members.length) {
                  item.role_members = item.role_members.map(v => {
                    return {
                      username: v,
                      readonly: false
                    };
                  });
                }
              });
              this.pagination = Object.assign(this.pagination, { count: data.count });
              this.emptyRenewalData
                = formatCodeData(code, this.emptyRenewalData, this.tableList.length === 0);
            },
            custom: () => {
              this.tableList = this.getCurPageData(current);
              this.$nextTick(() => {
                this.allData.forEach(item => {
                  if (this.currentSelectList.map(_ => _.id).includes(item.id)) {
                    this.$refs.permTableRef
                      && this.$refs.permTableRef.toggleRowSelection(item, true);
                  }
                });
              });
            }
          };
          return tabItem[this.type]();
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyRenewalData = formatCodeData(code, this.emptyRenewalData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      handleDetailAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSideSlider = false;
      },

      handleEmptyRefresh () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
        this.fetchTableData();
      }
    }
  };
</script>

<style lang="postcss">
    .iam-perm-renewal-table-wrapper {
        min-height: 200px;
        .perm-renewal-table {
            margin-top: 16px;
            border: none;
        }
        .related-resource-perm {
            position: relative;
            &-item {
                padding: 20px 0;
            }
            .view-icon {
                display: none;
                position: absolute;
                top: 50%;
                right: 40px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .view-icon {
                    display: inline-block;
                    color: #3a84ff;
                }
            }
            .effect-icon {
                display: none;
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .effect-icon {
                    display: inline-block;
                    color: #3a84ff;
                }
            }
            .effect-icon-disabled{
                display: none;
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .effect-icon-disabled {
                    display: inline-block;
                    color: #dcdee5;
                }
            }
            &-border{
              border-bottom: 1px solid #dfe0e5;
            }
        }

        .renewal-user-group-name {
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
        }
    }
</style>

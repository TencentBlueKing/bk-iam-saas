<template>
  <div class="iam-transfer-group-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
    v-bkloading="{ isLoading, opacity: 1 }">
    <template v-if="!isLoading && !isEmpty">
      <div class="transfer-group-content" ref="transferGroupContent">
        <div class="header" @click="handleGroupExpanded">
          <Icon bk class="expanded-icon" :type="groupExpanded ? 'down-shape' : 'right-shape'" />
          <label class="title"> {{$t(`m.permTransfer['用户组权限交接']`)}} </label>
          <div class="sub-title" v-if="groupNotTransferCount > 0">
            <i class="iam-icon iamcenter-warning-fill not-transfer-icon"></i>
            {{$t(`m.permTransfer['无法交接用户组：']`)}}{{groupNotTransferCount}}{{$t(`m.common['个']`)}}
            <span class="reason">{{$t(`m.permTransfer['（通过组织加入、已过期的组无法交接）']`)}}</span>
          </div>
        </div>
        <div class="content" v-if="groupExpanded">
          <div class="slot-content">
            <bk-table
              :style="{ maxHeight: groupShowAll ? 'none' : '254px' }"
              border
              ref="groupTableRef"
              :data="groupList"
              size="small"
              :class="{ 'set-border': isLoading }"
              :header-cell-class-name="getCellClass"
              :cell-class-name="getCellClass"
              :pagination="pagination"
              @select="handleSelect"
              @select-all="handleSelectAll"
              @page-change="handlePageChange"
              @page-limit-change="handleLimitChange">
              <bk-table-column type="selection" align="center" :selectable="row => !row.canNotTransfer">
              </bk-table-column>
              <bk-table-column :label="$t(`m.userGroup['用户组名']`)" width="300">
                <template slot-scope="{ row }">
                  <span :style="{ color: row.canNotTransfer ? '#c4c6cc' : '' }">
                    {{row.name}}
                    <i class="iam-icon iamcenter-warning-fill not-transfer-icon"
                      v-if="row.canNotTransfer"></i>
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.approvalProcess['来源']`)" width="300">
                <template slot-scope="{ row }">
                  <span :style="{ color: row.canNotTransfer ? '#c4c6cc' : '' }"
                    :title="row.role && row.role.name ? row.role.name : ''">
                    {{ row.role ? row.role.name : '--' }}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.perm['加入方式']`)" width="350">
                <template slot-scope="{ row }">
                  <span :style="{ color: row.canNotTransfer ? '#c4c6cc' : '' }"
                    v-if="row.department_id === 0">{{ $t(`m.perm['直接加入']`) }}</span>
                  <span :style="{ color: row.canNotTransfer ? '#c4c6cc' : '' }"
                    v-else :title="`${$t(`m.perm['通过组织加入']`)}${$t(`m.common['：']`)}${row.department_name}`">
                    {{ $t(`m.perm['通过组织加入']`) }}: {{ row.department_name }}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.common['有效期']`)" width="220">
                <template slot-scope="{ row }">
                  <span>{{row.expired_at_display}}</span>
                </template>
              </bk-table-column>
            </bk-table>
          </div>
          <p class="expand-action" @click="handleGroupShowAll" v-if="groupList.length > 5">
            <Icon :type="groupShowAll ? 'up-angle' : 'down-angle'" />
            <template v-if="!groupShowAll">{{ $t(`m.common['点击展开']`) }}</template>
            <template v-else>{{ $t(`m.common['点击收起']`) }}</template>
          </p>
        </div>
      </div>
    </template>
    <div v-if="!isLoading && isEmpty" style="height: 60px;">
      <div class="empty-wrapper">
        <!-- <iam-svg />
                <p class="text">{{ $t(`m.common['暂无数据']`) }}</p> -->
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-refresh="handleEmptyRefresh"
        />
      </div>
    </div>
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';
  import { formatCodeData, xssFilter } from '@/common/util';

  export default {
    name: '',
    components: {
    },
    data () {
      return {
        isEmpty: false,
        isLoading: false,
        groupList: [],
        groupExpanded: true,
        groupShowAll: false,
        groupNotTransferCount: 0,
        isSelectAllChecked: false,
        groupSelectData: [],
        pageContainer: null,
        pagination: {
          current: 1,
          limit: 10,
          count: 0
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['user', 'externalSystemId'])
    },
    mounted () {
      this.pageContainer = document.querySelector('.main-scroller');
      this.fetchData();
    },
    methods: {
      async fetchData () {
        this.isLoading = true;
        try {
          const { current, limit } = this.pagination;
          const userGroupParams = {
            page_size: limit,
            page: current
          };
          if (this.externalSystemId) {
            userGroupParams.system_id = this.externalSystemId;
          }
          const { code, data } = await this.$store.dispatch('perm/getPersonalGroups', userGroupParams);
          const groupList = data.results || [];
          this.pagination.count = data.count || 0;
          this.groupList.splice(0, this.groupList.length, ...groupList);
          this.isEmpty = groupList.length < 1;
          this.emptyData = formatCodeData(code, this.emptyData, this.isEmpty);
          this.handleGetCheckData();
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      handleGetCheckData () {
        const selectGroup = this.groupSelectData.length
          ? this.groupSelectData.map(item => String(item.id)) : [];
        this.groupList.forEach(item => {
          if (String(item.department_id) !== '0' || item.expired_at < this.user.timestamp) {
            this.groupNotTransferCount += 1;
            item.canNotTransfer = true;
          }
          setTimeout(() => {
            if (selectGroup.includes(String(item.id))) {
              this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
            }
            if (this.groupSelectData.length < 1) {
              this.$refs.groupTableRef && this.$refs.groupTableRef.clearSelection();
            }
          }, 0);
        });
        this.fetchSelectedGroupCount();
      },

      handleEmptyRefresh () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
        this.fetchData();
      },

      handleGroupExpanded () {
        this.groupExpanded = !this.groupExpanded;
        if (this.groupExpanded) {
          this.handleGetCheckData();
        }
      },

      handleGroupShowAll () {
        this.groupShowAll = !this.groupShowAll;
        if (!this.groupShowAll) {
          setTimeout(() => {
            const top = this.$refs.transferGroupContent.getBoundingClientRect().top
              + this.pageContainer.scrollTop;

            this.pageContainer.scrollTo({
              top: top - 61, // 减去顶导的高度 61
              behavior: 'smooth'
            });
            // this.$refs.transferGroupContent.scrollIntoView({
            //     behavior: 'smooth'
            // })
          }, 10);
        }
      },

      fetchSelectedGroupCount () {
        setTimeout(() => {
          const paginationWrapper = this.$refs.groupTableRef.$refs.paginationWrapper;
          if (paginationWrapper && paginationWrapper.getElementsByClassName('bk-page-selection-count')) {
            const selectCount = paginationWrapper.getElementsByClassName('bk-page-selection-count');
            if (selectCount.length && selectCount[0].children && selectCount[0].children.length) {
              selectCount[0].children[0].innerHTML = xssFilter(this.groupSelectData.length);
            }
          }
        }, 0);
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.groupSelectData.push(row);
            } else {
              this.groupSelectData = this.groupSelectData.filter((item) => item.id !== row.id);
            }
            this.fetchSelectedGroupCount();
          },
          all: () => {
            const validGroupList = payload.filter(item => !item.canNotTransfer);
            const selectGroups = this.groupSelectData.filter((item) =>
              !this.groupList.map((v) => v.id).includes(item.id));
            this.groupSelectData = [...selectGroups, ...validGroupList];
            this.fetchSelectedGroupCount();
          }
        };
        return typeMap[type]();
      },

      handleSelectAll (selection) {
        // this.isSelectAllChecked = !!selection.length;
        this.fetchSelectedGroups('all', selection);
        this.$emit('group-selection-change', this.groupSelectData);
      },

      handleSelect (selection, row) {
        // const validGroupList = this.groupList.filter(item => !item.canNotTransfer);
        // this.isSelectAllChecked = selection.length === validGroupList.length;
        this.fetchSelectedGroups('multiple', selection, row);
        this.$emit('group-selection-change', this.groupSelectData);
      },

      handlePageChange (page) {
        this.pagination = Object.assign(this.pagination, { current: page });
        this.fetchData();
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.fetchData();
        // this.isSearchSystem ? this.fetchSearchUserGroup() : this.fetchUserGroupList(true);
      },

      /**
       * getCellClass
       */
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 0) {
          return 'checkbox-cell-wrapper';
        }
        return '';
      }
    }
  };
</script>
<style lang="postcss">
    @import './group.css';
</style>

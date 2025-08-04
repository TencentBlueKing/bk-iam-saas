<template>
  <div class="iam-transfer-manager-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
    v-bkloading="{ isLoading, opacity: 1 }">
    <template v-if="!isLoading && !isEmpty">
      <div class="transfer-manager-content" ref="transferManagerContent">
        <div class="header" @click="handleRateExpanded">
          <Icon bk class="expanded-icon" :type="rateExpanded ? 'down-shape' : 'right-shape'" />
          <label class="title">{{$t(`m.permTransfer['管理员交接']`)}}</label>
        </div>
        <div class="content" v-if="rateExpanded">
          <div class="slot-content">
            <bk-table
              ref="manageTableRef"
              :style="{ maxHeight: managerShowAll ? 'none' : '254px' }"
              border
              :data="managerList"
              size="small"
              :class="['manager-table', { 'set-border': isLoading }]"
              :header-cell-class-name="getCellClass"
              :cell-class-name="getCellClass"
              :pagination="pagination"
              @select="handleSelect"
              @select-all="handleSelectAll"
              @page-change="handlePageChange"
              @page-limit-change="handleLimitChange">
              <bk-table-column type="selection" align="center">
              </bk-table-column>
              <bk-table-column :label="$t(`m.permTransfer['管理员名称']`)" width="300">
                <template slot-scope="{ row }">
                  {{row.name}}
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.common['类型']`)" width="300">
                <template slot-scope="{ row }">
                  <template v-if="row.type === 'super_manager'">
                    {{$t(`m.myApproval['超级管理员']`)}}
                  </template>
                  <template v-else-if="row.type === 'system_manager'">
                    {{$t(`m.nav['系统管理员']`)}}
                  </template>
                  <template v-else-if="row.type === 'rating_manager'">
                    {{$t(`m.userGroup['管理空间']`)}}
                  </template>
                  <template v-else>--</template>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.common['描述']`)" width="300">
                <template slot-scope="{ row }">
                  {{row.description || '--'}}
                </template>
              </bk-table-column>
              <template slot="empty">
                <ExceptionEmpty
                  :type="emptyData.type"
                  :empty-text="emptyData.text"
                  :tip-text="emptyData.tip"
                  :tip-type="emptyData.tipType"
                  @on-refresh="handleEmptyRefresh"
                />
              </template>
            </bk-table>
          </div>
          <p class="expand-action" @click="handleManagerShowAll" v-if="managerList.length > 5">
            <Icon :type="managerShowAll ? 'up-angle' : 'down-angle'" />
            <template v-if="!managerShowAll">{{ $t(`m.common['点击展开']`) }}</template>
            <template v-else>{{ $t(`m.common['点击收起']`) }}</template>
          </p>
        </div>
      </div>
    </template>
    <!-- <template v-if="!isLoading && isEmpty">
            <div class="empty-wrapper">
                <iam-svg />
                <p class="text">{{ $t(`m.common['暂无数据']`) }}</p>
            </div>
        </template> -->
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
        managerList: [],
        rateExpanded: true,
        managerShowAll: false,
        isSelectAllChecked: false,
        managerSelectData: [],
        pageContainer: null,
        pagination: {
          current: 1,
          limit: 20,
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
      ...mapGetters(['roleCount'])
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
          const params = {
            limit,
            offset: (current - 1) * limit
          };
          const res = await this.$store.dispatch('roleList', params);
          this.pagination.count = this.roleCount || 0;
          const managerList = res || [];
          this.managerList.splice(0, this.managerList.length, ...managerList);
          this.isEmpty = managerList.length < 1;
          this.emptyData = formatCodeData(0, this.emptyData, this.isEmpty);
          this.handleGetCheckData();
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      handleGetCheckData () {
        const selectGroup = this.managerSelectData.length
          ? this.managerSelectData.map(item => String(item.id)) : [];
        setTimeout(() => {
          this.managerList.forEach(item => {
            if (selectGroup.includes(String(item.id))) {
              this.$refs.manageTableRef && this.$refs.manageTableRef.toggleRowSelection(item, true);
            }
            if (this.managerSelectData.length < 1) {
              this.$refs.manageTableRef && this.$refs.manageTableRef.clearSelection();
            }
          });
        }, 0);
        this.fetchSelectedGroupCount();
      },

      handleRateExpanded () {
        this.rateExpanded = !this.rateExpanded;
        if (this.rateExpanded) {
          this.handleGetCheckData();
        }
      },

      handleManagerShowAll () {
        this.managerShowAll = !this.managerShowAll;
        if (!this.managerShowAll) {
          setTimeout(() => {
            const top = this.$refs.transferManagerContent.getBoundingClientRect().top
              + this.pageContainer.scrollTop;

            this.pageContainer.scrollTo({
              top: top - 61, // 减去顶导的高度 61
              behavior: 'smooth'
            });
            // this.$refs.transferManagerContent.scrollIntoView({
            //     behavior: 'smooth'
            // })
          }, 10);
        }
      },

      fetchSelectedGroupCount () {
        setTimeout(() => {
          const paginationWrapper = this.$refs.manageTableRef.$refs.paginationWrapper;
          const selectCount = paginationWrapper.getElementsByClassName('bk-page-selection-count');
          if (selectCount.length && selectCount[0].children && selectCount[0].children.length) {
            selectCount[0].children[0].innerHTML = xssFilter(this.managerSelectData.length);
          }
        }, 0);
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.managerSelectData.push(row);
            } else {
              this.managerSelectData = this.managerSelectData.filter((item) => item.id !== row.id);
            }
            this.fetchSelectedGroupCount();
          },
          all: () => {
            const selectGroups = this.managerSelectData.filter((item) =>
              !this.managerList.map((v) => v.id).includes(item.id));
            this.managerSelectData = [...selectGroups, ...payload];
            this.fetchSelectedGroupCount();
          }
        };
        return typeMap[type]();
      },

      handleSelectAll (selection) {
        this.fetchSelectedGroups('all', selection);
        this.$emit('manager-selection-change', this.managerSelectData);
      },

      handleSelect (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
        this.$emit('manager-selection-change', this.managerSelectData);
      },

      handlePageChange (page) {
        this.pagination = Object.assign(this.pagination, { current: page });
        this.fetchData();
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.fetchData();
      },

      handleEmptyRefresh () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 20 });
        this.fetchData();
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
    @import './manager.css';
</style>

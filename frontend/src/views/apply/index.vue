<template>
  <layout
    :external-left-layout-height="externalSystemsLayout.myApply.leftLayoutHeight"
    :external-right-layout-height="externalSystemsLayout.myApply.rightLayoutHeight"
  >
    <left-layout
      :data="applyList"
      :filter-active="filterActive"
      :current-active="currentActive"
      :filter-data="filterData"
      :is-loading="isApplyLoading"
      :can-scroll-load="canScrollLoad"
      :empty-data="emptyData"
      @on-change="handleChange"
      @on-filter-change="handleFilterChange"
      @on-load="handleLoadMore" />
    <div slot="right">
      <component
        :key="comKey"
        :is="curCom"
        :params="currentApplyData"
        :loading="cancelLoading"
        @on-cancel="handleCancel">
      </component>
    </div>
  </layout>
</template>
<script>
  import Layout from './common/render-page-layout';
  import LeftLayout from './components/left';
  import RenderDetail from './components/apply-detail';
  import RenderGroupDetail from './components/apply-group-detail';
  import RenderRatingManager from './components/apply-create-rate-manager-detail';
  import { mapGetters } from 'vuex';
  import { formatCodeData } from '@/common/util';

  const COM_MAP = new Map([
    [['grant_action', 'renew_action', 'grant_temporary_action'], 'RenderDetail'],
    [['join_group', 'renew_group'], 'RenderGroupDetail'],
    [['create_rating_manager'], 'RenderRatingManager'],
    [['update_rating_manager'], 'RenderRatingManager']
  ]);
    
  export default {
    name: '',
    components: {
      Layout,
      LeftLayout,
      RenderDetail,
      RenderGroupDetail,
      RenderRatingManager
    },
    data () {
      return {
        applyList: [],
        // 默认显示3天内的单据
        filterActive: '',
        currentActive: -1,
        filterData: {
          3: this.$t(`m.myApply['3天']`),
          7: this.$t(`m.myApply['一周']`),
          30: this.$t(`m.myApply['一个月']`),
          '': this.$t(`m.common['全部']`)
        },
        isLoading: false,
        isApplyLoading: false,
        pagination: {
          current: 1,
          totalPage: 1,
          limit: 15
        },
        currentBackup: 1,
        searchParams: {
          start_time: '',
          end_time: ''
        },
        currentApplyData: {},
        cancelLoading: false,
        comKey: -1,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['externalSystemId', 'externalSystemsLayout']),
            curCom () {
                let com = '';
                for (const [key, value] of this.comMap.entries()) {
                    if (Object.keys(this.currentApplyData).length && key.includes(this.currentApplyData.type)) { // 根据后台返回值渲染动态组件
                        com = value;
                        break;
                    }
                }
                return com;
            },
            canScrollLoad () {
                return this.pagination.totalPage > this.currentBackup;
            },
            listHeight () {
                // 可视化高度减去面包屑和导航栏高度，再减去固定标题的两个边框像素
                return window.innerHeight - 51 - 51 - 2;
            }
    },
    created () {
      this.comMap = COM_MAP;
      this.pagination.limit = Math.ceil(this.listHeight / 79);
    },
    methods: {
      async fetchPageData () {
        await this.fetchApplyList();
        this.fetchUrlParams();
      },

      async fetchApplyList (isLoading = false, isScrollLoad = false) {
        this.isApplyLoading = isLoading;
        const { current, limit } = this.pagination;
        const params = {
                    ...this.searchParams,
                    period: this.filterActive,
                    limit,
                    offset: limit * (current - 1)
        };
        if (!isScrollLoad) {
          this.applyList.splice(0, this.applyList.length, ...[]);
        }
        if (this.externalSystemId) {
          params.hidden = false;
          params.source_system_id = this.externalSystemId;
        }
        try {
          const { code, data } = await this.$store.dispatch('myApply/getApplyList', params);
          if (!isScrollLoad) {
            this.applyList = [...data.results];
            if (this.applyList.length < 1) {
              this.currentApplyData = {};
            } else {
              this.currentApplyData = this.applyList[0];
            }
            this.pagination.totalPage = Math.ceil(data.count / limit);
          } else {
            this.currentBackup++;
            (data.results || []).forEach(item => {
              item.is_read = false;
            });
            this.applyList.push(...data.results);
          }
          this.emptyData = formatCodeData(code, this.emptyData, this.applyList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.applyList = [];
          this.messageAdvancedError(e);
        } finally {
          this.isApplyLoading = false;
        }
      },

      fetchUrlParams () {
        if (this.externalSystemsLayout.myApply.externalSystemParams) {
          const query = this.$route.query;
          if (Object.keys(query).length && query.hasOwnProperty('id')) {
            this.currentApplyData = this.applyList.find(item => item.id === +query.id) || {};
            if (Object.keys(this.currentApplyData).length) {
              this.currentActive = this.currentApplyData.id;
            }
          }
        }
      },

      handleLoadMore () {
        this.pagination.current++;
        this.fetchApplyList(false, true);
      },

      handleChange (payload) {
        this.comKey = +new Date();
        this.currentApplyData = payload;
        this.currentActive = payload.id;
      },

      handleFilterChange (payload) {
        this.filterActive = payload;
        this.pagination.current = 1;
        this.currentBackup = 1;
        this.fetchApplyList(true);
      },

      async handleCancel () {
        this.cancelLoading = true;
        try {
          const params = {
            id: this.currentApplyData.id
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          await this.$store.dispatch('myApply/applyCancel', params);
          this.pagination.current = 1;
          this.currentBackup = 1;
          this.applyList.splice(0, this.applyList.length, ...[]);
          await this.fetchApplyList(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.cancelLoading = false;
        }
      }
    }
  };
</script>

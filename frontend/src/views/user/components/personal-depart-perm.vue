<template>
  <div class="iam-depart-perm-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
    <div class="iam-depart-perm-list" v-if="!pageLoading">
      <bk-table
        :data="curPageData"
        :size="'small'"
        :pagination="pageConf"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange">
        <bk-table-column :label="$t(`m.perm['组织名']`)">
          <template slot-scope="{ row }">
            <span class="org-full-name" :title="row.full_name.replace(/\//g, ' / ')"
              @click="goDetail(row)">{{ row.full_name.replace(/\//g, ' / ') }}</span>
          </template>
        </bk-table-column>
      </bk-table>
    </div>

    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :title="permSidesilderTitle"
      :depart-id="curDepartId"
      @animation-end="handleAnimationEnd" />
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';
  import RenderPermSideslider from '../../perm/components/render-depart-perm-sideslider';

  export default {
    name: '',
    components: {
      RenderPermSideslider
    },
    props: {
      data: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        dataList: [],
        pageConf: {
          current: 1,
          count: 0,
          limit: 10
          // limitList: [5, 10, 20, 50]
        },
        curPageData: [],

        isShowPermSidesilder: false,
        curDepartId: '',
        permSidesilderTitle: '',

        pageLoading: false,
        tableLoading: false
      };
    },
    computed: {
            ...mapGetters(['user'])
    },
    async created () {
      await this.fetchPermOrgs();
    },
    methods: {
      /**
       * 获取权限模板列表
       */
      async fetchPermOrgs () {
        this.pageLoading = true;
        const { type } = this.data;
        try {
          const res = await this.$store.dispatch('perm/getPermOrgs', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id
          });
          this.dataList.splice(0, this.dataList.length, ...(res.data || []));
          this.initPageConf();
          this.curPageData = this.getDataByPage(this.pageConf.current);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.pageLoading = false;
        }
      },

      handleAnimationEnd () {
        this.permSidesilderTitle = '';
        this.curDepartId = '';
        this.isShowPermSidesilder = false;
      },

      /**
       * 初始化弹层翻页条
       */
      initPageConf () {
        this.pageConf.current = 1;
        const total = this.dataList.length;
        this.pageConf.count = total;
      },

      /**
       * 翻页回调
       *
       * @param {number} page 当前页
       */
      handlePageChange (page = 1) {
        this.pageConf.current = page;
        const data = this.getDataByPage(page);
        this.curPageData.splice(0, this.curPageData.length, ...data);
      },

      /**
       * 获取当前这一页的数据
       *
       * @param {number} page 当前页
       *
       * @return {Array} 当前页数据
       */
      getDataByPage (page) {
        if (!page) {
          this.pageConf.current = page = 1;
        }
        let startIndex = (page - 1) * this.pageConf.limit;
        let endIndex = page * this.pageConf.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.dataList.length) {
          endIndex = this.dataList.length;
        }
        return this.dataList.slice(startIndex, endIndex);
      },

      /**
       * 每页显示多少条变化的回调
       *
       * @param {number} currentLimit 变化后每页多少条的数量
       * @param {number} prevLimit 变化前每页多少条的数量
       */
      handlePageLimitChange (currentLimit, prevLimit) {
        this.pageConf.limit = currentLimit;
        this.pageConf.current = 1;
        this.handlePageChange(this.pageConf.current);
      },

      /**
       * 跳转到 org-perm 详情
       *
       * @param {Object} row 当前行对象
       */
      goDetail (row) {
        this.curDepartId = row.id;
        this.permSidesilderTitle = `${this.$t(`m.common['组织']`)}${this.$t(`m.common['【']`)}${row.full_name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的权限']`)}`;
        this.isShowPermSidesilder = true;
      }
    }
  };
</script>
<style lang="postcss">
    .iam-depart-perm-wrapper {
        height: calc(100vh - 204px);
        .iam-perm-ext-cls {
            margin-top: 10px;
        }
        .bk-table {
            border-right: none;
            border-bottom: none;
            .org-full-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>

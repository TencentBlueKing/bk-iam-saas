<template>
  <div class="my-perm-group-perm" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
    <bk-table
      data-test-id="myPerm_table_group"
      :data="curPageData"
      :size="'small'"
      :pagination="pageConf"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <!-- 用户组名 -->
      <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
        <template slot-scope="{ row }">
          <span class="user-group-name" :title="row.name" @click="goDetail(row)">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <!-- 描述 -->
      <bk-table-column :label="$t(`m.common['描述']`)">
        <template slot-scope="{ row }">
          <span :title="row.description !== '' ? row.description : ''">
            {{ row.description !== '' ? row.description : '--'}}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.grading['管理空间']`)">
        <template slot-scope="{ row }">
          <span
            :title="row.role && row.role.name ? row.role.name : ''"
          >
            {{ row.role ? row.role.name : '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.levelSpace['管理员']`)" width="300">
        <template slot-scope="{ row, $index }">
          <iam-edit-member-selector
            mode="detail"
            field="role_members"
            width="300"
            :placeholder="$t(`m.verify['请输入']`)"
            :value="row.role_members"
            :index="$index"
          />
        </template>
      </bk-table-column>
      <!-- 加入用户组时间 -->
      <bk-table-column :label="$t(`m.perm['加入用户组的时间']`)" width="160">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time.replace(/T/, ' ') }}</span>
        </template>
      </bk-table-column>
      <!-- 加入方式 -->
      <bk-table-column :label="$t(`m.perm['加入方式']`)">
        <template slot-scope="props">
          <span v-if="props.row.department_id === 0">{{ $t(`m.perm['直接加入']`) }}</span>
          <span v-else :title="`${$t(`m.perm['通过组织加入']`)}：${props.row.department_name}`">
            {{ $t(`m.perm['通过组织加入']`) }}：{{ props.row.department_name }}
          </span>
        </template>
      </bk-table-column>
      <!-- 有效期 -->
      <bk-table-column :label="$t(`m.common['有效期']`)" prop="expired_at_display"></bk-table-column>
      <!-- 操作 -->
      <bk-table-column :label="$t(`m.common['操作']`)" width="200">
        <template slot-scope="props">
          <bk-button disabled text v-if="props.row.department_id !== 0">
            <span :title="$t(`m.perm['通过组织加入的组无法退出']`)">{{ $t(`m.common['退出']`) }}</span>
          </bk-button>
          <bk-button v-else class="mr10" theme="primary" text @click="showQuitTemplates(props.row)">
            {{ $t(`m.common['退出']`) }}
          </bk-button>
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

    <delete-dialog
      :show.sync="deleteDialogConf.visiable"
      :loading="deleteDialogConf.loading"
      :title="$t(`m.dialog['确认退出']`)"
      :sub-title="deleteDialogConf.msg"
      @on-after-leave="afterLeaveDelete"
      @on-cancel="cancelDelete"
      @on-sumbit="confirmDelete" />

    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd" />
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';
  import { formatCodeData } from '@/common/util';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';

  export default {
    name: '',
    components: {
      DeleteDialog,
      RenderPermSideslider,
      IamEditMemberSelector
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
        },
        curPageData: [],
        deleteDialogConf: {
          visiable: false,
          loading: false,
          row: {},
          msg: ''
        },

        isShowPermSidesilder: false,
        curGroupName: '',
        curGroupId: '',
        sliderLoading: false,
        curRoleId: -1,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['user'])
    },
    async created () {
      await this.fetchSystems();
    },
    methods: {
      async fetchSystems () {
        this.pageLoading = true;
        const { type } = this.data;
        try {
          const { code, data } = await this.$store.dispatch('perm/getDepartPermGroups', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id
          });
          this.dataList = data || [];
          this.pageConf.count = this.dataList.length;
          this.curPageData = this.getDataByPage(this.pageConf.current);
          this.curPageData.forEach(item => {
            if (item.role_members && item.role_members.length) {
              item.role_members = item.role_members.map(v => {
                return {
                  username: v,
                  readonly: false
                };
              });
            }
          });
          this.emptyData = formatCodeData(code, this.emptyData, this.dataList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.pageLoading = false;
        }
      },

      handleEmptyRefresh () {
        this.pageConf = Object.assign(
          {},
          {
            current: 1,
            count: 0,
            limit: 10
          });
        this.fetchSystems();
      },

      handleEmptySliderRefresh () {
        this.fetchRoles(this.curRoleId);
      },

      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
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
       * 跳转到 group-perm 详情
       *
       * @param {Object} row 当前行对象
       */
      goDetail (row) {
        this.curGroupName = row.name;
        this.curGroupId = row.id;
        this.isShowPermSidesilder = true;
        // this.$router.push({
        //     name: 'groupPermDetail',
        //     params: Object.assign({}, { id: row.id, name: row.name }, this.$route.params),
        //     query: this.$route.query
        // })
      },

      /**
       * 显示脱离模板弹框
       *
       * @param {Object} row 当前行对象
       */
      showQuitTemplates (row) {
        this.deleteDialogConf.visiable = true;
        this.deleteDialogConf.row = Object.assign({}, row);
        this.deleteDialogConf.msg = `${this.$t(`m.common['退出']`)}${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['将不再继承该组的权限']`)}${this.$t(`m.common['。']`)}`;
      },

      /**
       * 脱离模板确认函数
       */
      async confirmDelete () {
        this.deleteDialogConf.loading = true;
        try {
          await this.$store.dispatch('perm/quitGroupPerm', {
            type: 'group',
            id: this.deleteDialogConf.row.id
          });
          this.cancelDelete();
          this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
          this.$emit('refresh');
        } catch (e) {
          this.deleteDialogConf.loading = false;
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      /**
       * 脱离模板取消函数
       */
      cancelDelete () {
        this.deleteDialogConf.visiable = false;
      },

      /**
       * 脱离模板 afterLeave 函数
       */
      afterLeaveDelete () {
        this.deleteDialogConf.row = Object.assign({}, {});
        this.deleteDialogConf.msg = '';
        this.deleteDialogConf.loading = false;
      }
    }
  };
</script>
<style lang="postcss" scoped>
  @import '@/views/perm/department-group-perm/index.css';
</style>

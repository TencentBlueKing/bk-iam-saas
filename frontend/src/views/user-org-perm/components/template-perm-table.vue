<template>
  <div class="my-perm-group-perm">
    <bk-table
      ref="groupPermTableRef"
      size="small"
      :data="list"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: isLoading, opacity: 1 }"
    >
      <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
        <template slot-scope="{ row }">
          <span class="user-group-name" :title="row.name" @click="handleViewDetail(row)">
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)">
        <template slot-scope="{ row }">
          <span :title="row.description || ''">
            {{ row.description || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.grading['管理空间']`)">
        <template slot-scope="{ row }">
          <span :title="row.role && row.role.name ? row.role.name : ''">
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
      <bk-table-column :label="$t(`m.perm['加入用户组的时间']`)" width="160">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time.replace(/T/, ' ') }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.perm['加入方式']`)">
        <template slot-scope="{ row }">
          <span :title="`${$t(`m.perm['通过人员模板加入']`)}: ${row.template_name}`">
            {{ $t(`m.perm['通过人员模板加入']`) }}: {{ row.template_name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['有效期']`)" prop="expired_at_display" />
      <bk-table-column :label="$t(`m.common['操作-table']`)">
        <template>
          <bk-button
            class="mr10"
            theme="primary"
            text
            :disabled="true"
          >
            {{ $t(`m.common['退出']`) }}
          </bk-button>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="tableEmptyData.type"
          :empty-text="tableEmptyData.text"
          :tip-text="tableEmptyData.tip"
          :tip-type="tableEmptyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>
  
    <!-- <RenderGroupPermSideSlider
      :show="isShowPermSideSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd"
    /> -->
  </div>
</template>
  
  <script>
  // import RenderGroupPermSideSlider from '../components/render-group-perm-sideslider';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  export default {
    components: {
      IamEditMemberSelector
      // RenderGroupPermSideSlider
    },
    props: {
      mode: {
        type: String
      },
      isLoading: {
        type: Boolean,
        default: false
      },
      list: {
        type: Array,
        default: () => []
      },
      pagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            limit: 10,
            count: 0,
            showTotalCount: true
          };
        }
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
        isShowPermSideSlider: false,
        curGroupName: '',
        curGroupId: '',
        tableEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    watch: {
      emptyData: {
        handler (value) {
          this.tableEmptyData = Object.assign({}, value);
        },
        immediate: true
      }
    },
    methods: {
      handleViewDetail ({ id, name }) {
        this.curGroupName = name;
        this.curGroupId = id;
        this.isShowPermSideSlider = true;
      },
        
      handlePageChange (page) {
        this.$emit('on-page-change', page);
      },
  
      handleLimitChange (limit) {
        this.$emit('on-limit-change', limit);
      },
  
      handleEmptyClear () {
        this.$emit('on-clear');
      },
  
      handleEmptyRefresh () {
        this.$emit('on-refresh');
      },
  
      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSideSlider = false;
      }
    }
  };
  </script>
  
  <style lang="postcss" scoped>
  @import '@/views/perm/group-perm/index.css';
  </style>

<template>
  <bk-dialog
    v-model="isShowDialog"
    width="480"
    :title="$t(`m.userGroup['分配至']`)"
    :mask-close="false"
    header-position="left"
    ext-cls="iam-distribute-dialog"
    @after-leave="handleAfterLeave"
  >
    <div>
      <div class="title">{{ $t(`m.nav['二级管理空间']`) }}</div>
      <bk-select
        v-model="curGradeManager"
        ref="gradeManagerSelectRef"
        style="width: 430px"
        :placeholder="placeholder"
        :search-placeholder="$t(`m.info['搜索关键字']`)"
        :popover-min-width="430"
        :multiple="false"
        :loading="selectLoading"
        searchable
        :allow-enter="false"
        :remote-method="handleRemoteValue"
        @toggle="handleToggle(...arguments, $index, row)"
      >
        <bk-option v-for="option in gradeManagerList" :key="option.id" :id="option.id" :name="option.name">
          <div class="manage-space" v-if="option.id !== ''">
            <div class="single-hide manage-space-name" :title="option.name">
              {{ option.name }}
            </div>
            <div class="single-hide manage-space-members" :title="getMembersDisplay(option)">
              {{ getMembersDisplay(option) }}
            </div>
          </div>
          <template v-else>
            <div v-bkloading="{ isLoading: true, size: 'mini' }"></div>
          </template>
        </bk-option>
      </bk-select>
      <p class="warn-tips" v-if="isShowWarnMessage">
        <Icon type="info-new" />
        {{ warnMessage }}
      </p>
    </div>
    <template slot="footer">
      <div>
        <bk-button theme="primary" :disabled="disabled" :loading="loading" @click="handleSubmit">
          {{ $t(`m.common['确定']`) }}
        </bk-button>
        <bk-button @click="handleCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </template>
  </bk-dialog>
</template>
<script>
  import _ from 'lodash';

  const LOADING_ITEM = {
    id: '',
    name: ''
  };

  export default {
    name: '',
    props: {
      show: {
        type: Boolean,
        default: false
      },
      groupIds: {
        type: Array,
        default: () => []
      },
      distributeDetail: {
        type: Object,
        default: null
      }
    },
    data () {
      return {
        isShowDialog: false,
        curGradeManager: '',
        gradeManagerList: [],
        pagination: {
          totalPage: 1,
          limit: 10,
          current: 1
        },
        selectLoading: false,
        searchValue: '',
        isShowWarnMessage: false,
        warnMessage: '',
        loading: false,
        placeholder: this.$t(`m.verify['请选择管理空间']`)
      };
    },
    computed: {
      disabled () {
        return this.curGradeManager === '';
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowDialog = !!value;
          if (this.isShowDialog) {
            this.fetchInit();
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchData (isLoading = false, isScrollRemote = false) {
        this.selectLoading = isLoading;
        const params = {
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1),
          name: this.searchValue
        };
        try {
          const { data } = await this.$store.dispatch('spaceManage/getSecondManager', params);
          if (isScrollRemote) {
            const len = this.gradeManagerList.length;
            this.gradeManagerList.splice(len - 1, 0, ...data.results);
          } else {
            this.pagination.totalPage = Math.ceil(data.count / this.pagination.limit);
            if (this.pagination.totalPage > 1) {
              data.results.push(LOADING_ITEM);
            }
            this.gradeManagerList.splice(0, this.gradeManagerList.length, ...(data.results || []));
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.selectLoading = false;
        }
      },

      async fetchInit () {
        await this.fetchData(true);
        this.curGradeManager = this.gradeManagerList.length ? this.gradeManagerList[0].id : '';
      },

      handleToggle (val, index, payload) {
        const curOptionDom = this.$refs.gradeManagerSelectRef.$refs.optionList;
        curOptionDom.addEventListener('scroll', this.handleScroll);
        if (!val) {
          curOptionDom.removeEventListener('scroll', this.handleScroll);
          this.searchValue = '';
        }
      },

      async handleScroll (event) {
        if (event.target.scrollTop + event.target.offsetHeight >= event.target.scrollHeight) {
          ++this.pagination.current;
          if (this.pagination.current > this.pagination.totalPage) {
            this.pagination.current = this.pagination.totalPage;
            const loadItemIndex = this.gradeManagerList.findIndex((item) => item.id === '' && item.name === '');
            // 删除loading项
            if (loadItemIndex !== -1) {
              this.gradeManagerList = _.cloneDeep(this.gradeManagerList.slice(0, loadItemIndex));
            }
            return;
          }
          await this.fetchData(false, true);
          event.target.scrollTo(0, event.target.scrollTop - 10);
        }
      },

      async handleRemoteValue (val) {
        this.searchValue = val;
        this.pagination.current = 1;
        this.pagination.totalPage = 0;
        const loadItemIndex = this.gradeManagerList.findIndex((item) => item.id === '' && item.name === '');
        // 删除loading项
        if (loadItemIndex !== -1) {
          this.gradeManagerList = _.cloneDeep(this.gradeManagerList.slice(0, loadItemIndex));
        }
        await this.fetchData();
      },

      resetData () {
        this.pagination = _.assign(
          {},
          {
            totalPage: 1,
            limit: 10,
            current: 1
          }
        );
        this.curGradeManager = '';
        this.isShowWarnMessage = false;
        this.warnMessage = '';
      },

      getMembersDisplay (payload) {
        const members = payload.members.map(item => item.username);
        return `${this.$t(`m.common['管理员']`)}: ${members.join(',')}`;
      },

      async handleSubmit () {
        const params = {
          id: this.distributeDetail.id,
          subset_manager_id: this.curGradeManager
        };
        try {
          this.loading = true;
          await this.$store.dispatch('userGroup/userGroupDistribute', params);
          this.messageSuccess(this.$t(`m.info['分配成功']`), 3000);
          this.$emit('on-success');
        } catch (e) {
          console.error(e);
          const message = e.message || e.data.msg || e.statusText;
          if (e.code === 1902418) {
            this.isShowWarnMessage = true;
            this.warnMessage = message;
          } else {
            this.messageAdvancedError(e);
          }
        } finally {
          this.loading = false;
        }
      },

      handleCancel () {
        this.$emit('update:show', false);
      },

      handleAfterLeave () {
        this.resetData();
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
      }
    }
  };
</script>
<style lang="postcss">
.iam-distribute-dialog {
  .title {
    margin-bottom: 5px;
  }

  .warn-tips {
    margin-top: 5px;
    line-height: 18px;
    font-size: 12px;
    color: #FF9C01;

    i {
      position: relative;
      top: -1px;
      font-size: 14px;
    }
  }
}

.manage-space {
    line-height: 20px;
    &-name {
      position: relative;
      top: 2px;
      max-width: 390px;
      word-break: break-all;
    }
  
    &-members {
      position: relative;
      top: -2px;
      max-width: 390px;
      color: #c4c6cc;
    }
  }
</style>

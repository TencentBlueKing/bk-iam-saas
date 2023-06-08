<template>
  <div class="iam-depart-perm-wrapper" v-if="isShowPage">
    <div class="header">
      <template v-if="isDepart">
        <span class="display-name">{{ curData.name }}</span>
        <!-- <span class="count">({{ curData.count }})</span> -->
      </template>
      <template v-else>
        <span class="display-name">{{ curData.username }}</span>
        <span class="name" v-if="isExistName">({{ curData.name }})</span>
      </template>
    </div>
    <div class="table-list-wrapper">
      <bk-tab
        :active.sync="active"
        type="unborder-card"
        ext-cls="iam-user-tab-cls"
        @tab-change="handleTabChange">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index">
        </bk-tab-panel>
        <component
          :key="componentsKey"
          :is="curCom"
          :data="curData"
          @on-init="handleComInit">
        </component>
      </bk-tab>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import JoinedUserGroup from './joined-user-group';
  export default {
    name: '',
    components: {
      JoinedUserGroup
    },
    props: {
      params: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        curData: {},
        panels: [
          { name: 'group', label: this.$t(`m.perm['加入的用户组']`) }
        ],
        active: 'group',
        componentsKey: -1,
        curCom: 'JoinedUserGroup'
      };
    },
    computed: {
      /**
       * isDepart
       */
      isDepart () {
        return this.curData.type === 'depart';
      },
      /**
       * isExistName
       */
      isExistName () {
        return this.curData.type === 'user' && this.curData.name !== '';
      },
      /**
       * isShowPage
       */
      isShowPage () {
        return Object.keys(this.params).length > 0;
      }
    },
    watch: {
      /**
       * params
       */
      params: {
        handler (value) {
          if (Object.keys(value).length > 0) {
            // this.active = 'perm'
            // this.curCom = 'DepartPerm'
            this.active = 'group';
            this.curCom = 'JoinedUserGroup';
            this.componentsKey = +new Date();
            this.curData = _.cloneDeep(value);
          }
        },
        immediate: true
      },
      /**
       * active
       */
      active (value) {
        this.curCom = value === 'perm' ? 'DepartPerm' : 'JoinedUserGroup';
        this.componentsKey = +new Date();
      }
    },
    methods: {
      /**
       * handleComInit
       */
      handleComInit (payload) {
        this.$emit('on-init', payload);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-depart-perm-wrapper {
        .header {
            .display-name {
                font-size: 16px;
                color: #313238;
            }
            .count,
            .name {
                font-size: 16px;
                color: #c4c6cc;
            }
        }
        .table-list-wrapper {
            margin-top: 20px;
            .iam-user-tab-cls {
                .bk-tab-section {
                    padding: 20px 0 0 0;
                }
            }
        }
    }
</style>

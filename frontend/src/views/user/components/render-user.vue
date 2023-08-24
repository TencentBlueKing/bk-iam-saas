<template>
  <div class="iam-personal-user-perm-wrapper" v-if="isShowPage">
    <div class="header">
      <span class="display-name">{{ curData.username }}</span>
      <span class="name" v-if="isExistName">({{ curData.name }})</span>
    </div>
    <div class="table-list-wrapper">
      <bk-tab
        :active.sync="active"
        type="unborder-card"
        ext-cls="iam-user-tab-cls">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index">
        </bk-tab-panel>
        <component
          :key="componentsKey"
          :is="curCom"
          :data="curData">
        </component>
      </bk-tab>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import CustomPerm from './custom-perm';
  import GroupPerm from './group-perm';
  import TeporaryCustomPerm from './teporary-custom-perm';
  import DepartmentGroupPerm from './department-group-perm';
  export default {
    name: '',
    components: {
      CustomPerm,
      GroupPerm,
      TeporaryCustomPerm,
      DepartmentGroupPerm
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
          { name: 'groupPerm', label: this.$t(`m.perm['用户组权限']`) },
          { name: 'departmentGroupPerm', label: this.$t(`m.perm['所属组织用户组权限']`) },
          { name: 'customPerm', label: this.$t(`m.perm['自定义权限']`) }
          // { name: 'teporaryCustomPerm', label: this.$t(`m.myApply['临时权限']`) }
        ],
        active: 'groupPerm',
        componentsKey: -1,
        curCom: 'GroupPerm'
      };
    },
    computed: {
      /**
       * isExistName
       */
      isExistName () {
        return this.curData.name !== '';
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
            this.active = 'groupPerm';
            this.curCom = 'GroupPerm';
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
        const comMap = {
          'customPerm': 'CustomPerm',
          'groupPerm': 'GroupPerm',
          'teporaryCustomPerm': 'TeporaryCustomPerm',
          'departmentGroupPerm': 'DepartmentGroupPerm'
        };
        this.curCom = comMap[value];
        this.componentsKey = +new Date();
      }
    },
    methods: {}
  };
</script>
<style lang="postcss">
    .iam-personal-user-perm-wrapper {
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

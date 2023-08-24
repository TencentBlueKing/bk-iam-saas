<template>
  <div>
    <render-horizontal-block
      :label="$t(`m.nav['授权边界']`)"
      :required="false"
    >
      <div class="render-perm-boundary">
        <div v-if="modules.includes('resourcePerm')"
          class="render-form-item"
        >
          <div class="perm-boundary-title">
            {{ $t(`m.levelSpace["${BOUNDARY_KEYS_ENUM['resourcePerm'].title}"]`) }}:
          </div>
          <div :class="[
                 'iam-resource-expand'
               ]"
            @click.stop="handleExpanded('resourcePerm')">
            <div class="iam-resource-header flex-between">
              <div class="iam-resource-header-left">
                <Icon bk
                  :type="BOUNDARY_KEYS_ENUM['resourcePerm'].isExpanded ? 'down-shape' : 'right-shape'"
                />
                <div class="iam-resource-header-left-title">
                  <span>{{ $t(`m.common['共']`) }}</span>
                  <span class="number">{{ permLength }}</span>
                  <span>{{ $t(`m.common['个']`) }}{{ $t(`m.perm['操作权限']`) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="content" v-if="BOUNDARY_KEYS_ENUM['resourcePerm'].isExpanded">
            <div class="slot-content">
              <slot name="resourcePerm" />
            </div>
          </div>
        </div>
        <div v-if="modules.includes('membersPerm')"
          class="render-form-item">
          <div class="perm-boundary-title">
            {{ $t(`m.levelSpace["${BOUNDARY_KEYS_ENUM['membersPerm'].title}"]`) }}:
          </div>
          <div :class="[
                 'iam-resource-expand'
               ]"
            @click.stop="handleExpanded('membersPerm')">
            <div class="iam-resource-header">
              <div class="iam-resource-header-left">
                <Icon bk
                  :type="BOUNDARY_KEYS_ENUM['membersPerm'].isExpanded ? 'down-shape' : 'right-shape'"
                />
                <div class="iam-resource-header-left-title"
                  v-if="userLength > 0 || departLength > 0">
                  <template v-if="userLength > 0">
                    {{ $t(`m.common['共']`) }}
                    <span class="number">{{ userLength }}</span>
                    {{ $t(`m.common['个用户']`) }}
                  </template>
                  <template v-if="userLength && departLength">
                    {{ $t(`m.common['，']`) }}
                  </template>
                  <template v-if="departLength > 0">
                    {{ $t(`m.common['共']`) }}
                    <span class="number">{{ departLength }}</span>
                    {{ $t(`m.common['个组织']`) }}
                  </template>
                </div>
              </div>
            </div>
          </div>
          <div class="content" v-if="BOUNDARY_KEYS_ENUM['membersPerm'].isExpanded">
            <div class="slot-content">
              <slot name="membersPerm" />
            </div>
          </div>
        </div>
      </div>
    </render-horizontal-block>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { BOUNDARY_KEYS_ENUM } from '@/common/constants';
  export default {
    name: '',
    props: {
      modules: {
        type: Array,
        default: () => []
      },
      expanded: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      permLength: {
        type: Number,
        default: 0
      },
      userLength: {
        type: Number,
        default: 0
      },
      departLength: {
        type: Number,
        default: 0
      },
      extCls: {
        type: String,
        default: ''
      },
      canDelete: {
        type: Boolean,
        default: false
      },
      resourceTitle: {
        type: String
      },
      membersTitle: {
        type: String
      }
    },
    data () {
      return {
        isExpanded: this.expanded,
        BOUNDARY_KEYS_ENUM: _.cloneDeep(BOUNDARY_KEYS_ENUM)
      };
    },
    computed: {
      isShowDelete () {
        return this.canDelete && !this.isExpanded;
      }
    },
    watch: {
      expanded (value) {
        this.isExpanded = !!value;
      }
    },
    methods: {
      handleExpanded (payload) {
        this.BOUNDARY_KEYS_ENUM[payload].isExpanded = !this.BOUNDARY_KEYS_ENUM[payload].isExpanded;
        this.$emit('on-expanded', payload, this.BOUNDARY_KEYS_ENUM[payload].isExpanded);
      }
    }
  };
</script>

<style lang="postcss">
.render-perm-boundary {
    .members-boundary-detail {
        border: 1px solid #DCDEE5;
        border-top: 0;
        padding: 15px;
    }
}

</style>

<style lang="postcss" scoped>
@import '@/css/mixins/space-resource-instance-table.css';
/deep/ .render-perm-boundary {
  .bk-table {
    margin-top: 0;
    border-top: 0;
  }

  .render-form-item {
    margin-bottom: 24px;
  }

  .perm-boundary-title {
    font-size: 12px;
    margin-bottom: 10px;
  }

    .iam-resource-expand {
        background-color: #F5F7FA;
        .iam-resource-header-left {
            padding: 0 10px !important;
            display: flex;
            align-items: center;
            &-title {
                margin-left: 5px;
            }
        }

    }

    .member-boundary-detail {
        border: 1px solid #DCDEE5;
        border-top: 0;
    }
}
</style>

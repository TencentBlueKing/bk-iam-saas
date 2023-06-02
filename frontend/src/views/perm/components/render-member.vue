<template>
  <div class="iam-member-display-wrapper">
    <label class="label">
      <Icon :type="icon" class="icon" />
      <span class="name">{{ title }}</span>
    </label>
    <div class="content">
      <!-- eslint-disable max-len -->
      <div v-for="(item, index) in data"
        :key="index"
        class="member-item"
        :title="isDepartment ? item.full_name || item.name : !!item.name ? `${item.id}(${item.name})` : item.id">
        <span class="member-name">
          {{ isDepartment ? item.name : item.id }}
        </span>
        <template v-if="!isDepartment && item.name !== ''">
          <span class="name">({{ item.name }})</span>
        </template>
        <template v-if="isDepartment">
          <span class="count">({{ item.member_count }})</span>
        </template>
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      data: {
        type: Array,
        default: () => []
      },
      // user：用户，department：组织
      type: {
        type: String,
        default: 'user'
      }
    },
    computed: {
      icon () {
        return this.type === 'user' ? 'personal-user' : 'organization-fill';
      },
      title () {
        return this.type === 'user' ? this.$t(`m.common['用户']`) : this.$t(`m.common['组织']`);
      },
      isDepartment () {
        return this.type === 'department';
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-member-display-wrapper {
        color: #63656e;
        .label {
            display: inline-block;
            margin-bottom: 9px;
            font-size: 12px;
            .icon {
                display: inline-block;
                color: #3a84ff;
                vertical-align: middle;
            }
            .name {
                display: inline-block;
                font-weight: 700;
                vertical-align: middle;
            }
        }
        .content {
            .member-item {
                position: relative;
                display: inline-block;
                margin: 0 6px 6px 0;
                padding: 0 10px;
                line-height: 22px;
                background: #f5f6fa;
                border: 1px solid #dcdee5;
                border-radius: 2px;
                font-size: 12px;
                &:hover {
                    .remove-icon {
                        display: block;
                    }
                }
                .member-name {
                    display: inline-block;
                    max-width: 200px;
                    line-height: 17px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    vertical-align: text-top;
                }
                .name {
                    display: inline-block;
                    vertical-align: top;
                }
                .count {
                    display: inline-block;
                    color: #c4c6cc;
                    vertical-align: top;
                }
            }
        }
    }
</style>

<template>
  <div class="iam-member-display-wrapper">
    <label class="label">
      <Icon :type="icon" class="icon" />
      <span class="name">{{ title }}</span>
    </label>
    <div class="content">
      <div
        v-for="(item, index) in data"
        :key="index"
        class="member-item"
      >
        <!-- 单独处理没有username和count的页面业务 -->
        <template>
          <template v-if="isCustomRoute">
            <div class="member-name">
              <IamUserDisplayName :user-id="formatCustomTypeName(item)" :display-value="[nameType(item)]" />
            </div>
          </template>
          <template v-else>
            <div class="member-name">
              <IamUserDisplayName
                :user-id="formatCustomTypeName(item)"
                :display-value="[nameType(item)]"
              />
            </div>
            <template v-if="isHasDepartCount && item.count">
              <span class="count">({{ item.count }})</span>
            </template>
            <!-- <template v-if="!isHasDepartCount && !isTemplate && item.name !== ''">
              <span class="display_name">({{ item.name }})</span>
            </template> -->
          </template>
        </template>
        <template v-if="isTemplate">
          <span class="display_name">{{ item.name }}</span>
        </template>
        <Icon type="close-fill" class="remove-icon" v-if="isEdit" @click="handleDelete(index)" />
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
      },
      mode: {
        type: String,
        default: 'edit'
      }
    },
    computed: {
      isCustomRoute () {
        return ['userOrgPerm'].includes(this.$route.name);
      },
      icon () {
        if (this.type === 'user') {
          return 'personal-user';
        }
        if (this.type === 'template') {
          return 'renyuanmuban';
        }
        return 'organization-fill';
      },
      title () {
        if (this.type === 'user') {
          return this.$t(`m.common['用户']`);
        }
        if (this.type === 'template') {
          return this.$t(`m.memberTemplate['人员模板']`);
        }
        return this.$t(`m.common['组织']`);
      },
      isDepartment () {
        return this.type === 'department';
      },
      isTemplate () {
        return this.type === 'template';
      },
      isHasDepartCount () {
        return this.isDepartment && window.ENABLE_ORGANIZATION_COUNT.toLowerCase() === 'true';
      },
      isEdit () {
        return this.mode === 'edit';
      },
      nameType () {
        return (payload) => {
          const { name, type, id, username, full_name: fullName } = payload;
          const typeMap = {
            user: () => {
              const curName = username || id;
              return fullName || curName;
            },
            department: () => {
              // return fullName || payload.fullName || (username ? `${username}(${name})` : name);
              return fullName || username || name;
            },
            depart: () => {
              return fullName || username || name;
            },
            template: () => {
              return name;
            }
          };
          return typeMap[type] ? typeMap[type]() : typeMap['user']();
        };
      },
      formatCustomTypeName () {
        return (payload) => {
          const { name, type, username } = payload;
          const typeMap = {
            user: () => {
              return username || name;
            },
            department: () => {
              return username || name;
            }
          };
          return typeMap[type] ? typeMap[type]() : typeMap['user']();
        };
      }
    },
    methods: {
      handleDelete (payload) {
        this.$emit('on-delete', payload);
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
            min-width: 120px;
            width: 130px;
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
                    .count {
                        color: #c4c6cc;
                    }
                }
                .count,
                .display_name {
                    display: inline-block;
                    vertical-align: top;
                }
                .remove-icon {
                    display: none;
                    position: absolute;
                    top: -6px;
                    right: -6px;
                    cursor: pointer;
                }
            }
        }
    }
</style>

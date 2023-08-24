<template>
  <div class="iam-member-display-wrapper">
    <label class="label">
      <Icon :type="icon" class="icon" />
      <span class="name">{{ title }}</span>
    </label>
    <div class="content">
      <div v-for="(item, index) in data"
        :key="index"
        class="member-item"
        :title="getTitle(item)">
        <span class="member-name">
          {{ isDepartment ? item.name : item.id }}
        </span>
        <template v-if="isDepartment">
          <span class="count">({{ item.member_count }})</span>
        </template>
        <template v-if="!isDepartment && item.name !== ''">
          <span class="display_name">({{ item.name }})</span>
        </template>
        <Icon
          type="close-fill"
          class="remove-icon"
          v-if="isEdit"
          @click="handleDelete(index)" />
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
      /**
       * icon
       */
      icon () {
        return this.type === 'user' ? 'personal-user' : 'organization-fill';
      },
      /**
       * title
       */
      title () {
        return this.type === 'user' ? this.$t(`m.common['用户']`) : this.$t(`m.common['组织']`);
      },

      /**
       * isDepartment
       */
      isDepartment () {
        return this.type === 'department' && window.ENABLE_ORGANIZATION_COUNT.toLowerCase() === 'true';
      },

      /**
       * isEdit
       */
      isEdit () {
        return this.mode === 'edit';
      }
    },
    methods: {
      /**
       * getTitle
       */
      getTitle (payload) {
        if (this.isDepartment) {
          return payload.full_name !== '' ? payload.full_name : payload.name;
        }
        return payload.name !== '' ? `${payload.id}(${payload.name})` : payload.id;
      },

      /**
       * handleDelete
       */
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

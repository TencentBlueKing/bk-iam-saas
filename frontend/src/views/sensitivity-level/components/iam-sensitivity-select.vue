<template>
  <div class="iam-select-property" :style="styles">
    <template v-if="!isEditable">
      <div class="edit-wrapper">
        <div class="edit-content">
          <slot>
            <template v-if="displayValue.length">
              <bk-tag
                type="filled"
                :ext-cls="formatTagCustomClass(item)"
                v-for="item in displayValue"
                :key="item.id"
                :theme="item.theme"
              >
                {{ $t(`m.sensitivityLevel['${item.name}']`) }}
              </bk-tag>
            </template>
            <template v-else> -- </template>
          </slot>
        </div>
        <div class="edit-action-box" v-if="isEditMode">
          <Icon
            type="edit-fill"
            class="edit-action"
            v-if="!isLoading"
            @click.self.stop="handleEdit"
          />
          <Icon type="loading-circle" class="edit-loading" v-if="isLoading" />
        </div>
      </div>
    </template>
    <template v-else>
      <bk-select
        ref="sensitivityLevelSelect"
        v-model="multipleValue"
        :searchable="false"
        :multiple="isMultiple"
        :display-tag="isMultiple"
        :clearable="false"
        :show-select-all="false"
        @toggle="handleToggle"
        @change="handleChange"
      >
        <bk-option
          v-for="item in sensitivityLevelDataList"
          :key="item.id"
          :id="item.id"
          :name="$t(`m.sensitivityLevel['${item.name}']`)"
          :disabled="item.disabled"
        >
          <bk-tag type="filled" :ext-cls="formatTagCustomClass(item)" :theme="item.theme">
            {{ $t(`m.sensitivityLevel['${item.name}']`) }}
          </bk-tag>
        </bk-option>
      </bk-select>
    </template>
  </div>
</template>

<script>
  import _ from 'lodash';
  import il8n from '@/language';

  export default {
    name: 'iam-sensitivity-level-select',
    props: {
      selectedValue: {
        type: [Array, String],
        default: () => []
      },
      list: {
        type: Array,
        default: () => []
      },
      width: {
        type: String,
        default: 'auto'
      },
      placeholder: {
        type: String,
        default: il8n('verify', '请选择')
      },
      mode: {
        type: String,
        default: 'edit',
        validator: function (value) {
          return ['detail', 'edit'].includes(value);
        }
      },
      index: {
        type: Number,
        default: 0
      },
      attributes: {
        type: Object
      },
      isMultiple: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isEditable: false,
        isLoading: false,
        isShowError: '',
        displayValue: [],
        multipleValue: [],
        sensitivityLevelData: {
          sensitivity_level: 'all'
        },
        sensitivityLevelDataList: []
      };
    },
    computed: {
      styles () {
        return {
          width: this.width
        };
      },
      isEditMode () {
        return this.mode === 'edit';
      },
      formatTagCustomClass () {
        return (payload) => {
          return ['L5'].includes(payload.id)
            ? 'sensitivity-level-select-tag sensitivity-level-select-tag-custom'
            : 'sensitivity-level-select-tag';
        };
      }
    },
    watch: {
      attributes: {
        handler (value) {
          this.sensitivityLevelData = Object.assign({}, value);
        },
        immediate: true
      },
      selectedValue: {
        handler (value) {
          if (_.isArray(value)) {
            this.multipleValue = _.cloneDeep(value);
            this.displayValue = _.cloneDeep(
              this.list.filter((item) => value.includes(item.id))
            );
          } else {
            this.multipleValue = _.cloneDeep([value]);
            this.displayValue = _.cloneDeep(
              this.list.filter((item) => [value].includes(item.id))
            );
          }
        },
        immediate: true
      },
      list: {
        handler (value) {
          value.forEach((item) => {
            item.disabled = this.sensitivityLevelData[item.id];
          });
          this.sensitivityLevelDataList = [...value];
        },
        immediate: true
      }
    },
    mounted () {
      window.addEventListener('keydown', this.handleKeydown);
    },
    beforeDestroy () {
      window.removeEventListener('keydown', this.handleKeydown);
    },
    methods: {
      handleToggle (payload) {
        if (!payload) {
          this.isEditable = false;
          if (JSON.stringify(this.multipleValue) !== JSON.stringify(this.value)) {
            this.$emit('on-change', this.multipleValue, this.index);
          }
        }
      },
      handleChange (newValue, oldValue) {
        // 过滤掉disabled的数据
        const list = this.list.filter(
          (item) =>
            item.disabled && oldValue.includes(item.id) && !newValue.includes(item.id)
        );
        if (list.length) {
          this.multipleValue = this.multipleValue.concat([...list.map((item) => item.id)]);
          const nameList = list.map((item) =>
            this.$t(`m.sensitivityLevel['${item.name}']`)
          );
          const textValue = this.$t(`m.info['当前敏感等级为只读操作']`, {
            value: nameList
          });
          this.messageWarn(textValue, 3000);
        }
      },
      handleKeydown (event) {
        if (event.keyCode === 13 && this.isEditable) {
          this.handleToggle(false);
        }
      },
      handleEdit () {
        this.isEditable = true;
        this.$nextTick(() => {
          this.$refs.sensitivityLevelSelect && this.$refs.sensitivityLevelSelect.show();
        });
      }
    }
  };
</script>

<style lang="postcss" scoped>
@keyframes textarea-edit-loading {
  to {
    transform: rotateZ(360deg);
  }
}
.iam-select-property {
  position: relative;
  .edit-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    &:hover {
      .edit-action {
        display: block;
      }
    }
  }
  .edit-content {
    flex: 0 0 auto;
    max-width: calc(100% - 25px);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .edit-action-box {
    display: flex;
    align-items: center;
    margin-right: auto;
    font-size: 16px;
    .edit-action {
      padding: 6px 15px 6px 2px;
      cursor: pointer;
      display: none;
      &:hover {
        color: #3a84ff;
      }
    }
    .edit-loading {
      position: absolute;
      top: 8px;
      margin-left: 2px;
      animation: "textarea-edit-loading" 1s linear infinite;
    }
  }
  .edit-select {
    width: 100%;
  }
}
</style>

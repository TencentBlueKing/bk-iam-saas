<template>
  <div class="iam-edit-select" :style="styles" v-bk-clickoutside="handleClickoutside">
    <template v-if="!isEditable">
      <div class="edit-wraper">
        <div class="edit-content">
          <slot v-bind:value="newVal">{{ displayValue }}</slot>
        </div>
        <div class="edit-action-box">
          <Icon
            type="edit-fill"
            class="edit-action"
            v-if="!isLoading"
            @click.self.stop="handleEdit" />
          <Icon
            type="loading-circle"
            class="edit-loading"
            v-if="isLoading" />
        </div>
      </div>
    </template>
    <template v-else>
      <bk-select
        v-model="newVal"
        :clearable="false"
        searchable
        ref="select"
        @selected="handleSelected">
        <bk-option v-for="option in list"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
    </template>
  </div>
</template>
<script>
  export default {
    name: 'iam-edit-select',
    props: {
      field: {
        type: String,
        required: true
      },
      value: {
        type: String,
        default: ''
      },
      width: {
        type: String,
        default: 'auto'
      },
      remoteHander: {
        type: Function,
        default: () => Promise.resolve()
      },
      rules: {
        type: Array,
        default: () => []
      },
      list: {
        type: Array,
        required: true
      }
    },
    data () {
      return {
        newVal: this.value,
        isEditable: false,
        isLoading: false
      };
    },
    computed: {
      styles () {
        return {
          width: this.width
        };
      },
      displayValue () {
        return this.list.find(item => item.id === this.newVal).name;
      }
    },
    watch: {
      value (val) {
        this.newVal = val;
      }
    },
    methods: {
      handleClickoutside () {
        // console.warn(arguments[0]['target']['className'])
        const classList = ['bk-option-name', 'bk-option-content-default', 'bk-select-search-input', 'bk-option-content', 'bk-options bk-options-single'];
        if (classList.includes(arguments[0]['target']['className'])) {
          return;
        }
        this.isEditable = false;
      },
      handleEdit () {
        document.body.click();
        this.isEditable = true;
        this.$nextTick(() => {
          this.$refs.select.show();
        });
      },
      handleSelected () {
        if (!this.isEditable) return;
        this.triggerChange();
      },
      hideEdit (event) {
        if (event.path && event.path.length > 0) {
          for (let i = 0; i < event.path.length; i++) {
            const target = event.path[i];
            if (target.className === 'iam-edit-select') {
              return;
            }
          }
        }
        this.isEditable = false;
      },
      triggerChange () {
        this.isEditable = false;
        if (this.newVal === this.value) {
          return;
        }
        this.isLoading = true;
        this.remoteHander({
          [this.field]: this.newVal
        }).then(() => {
          this.$emit('on-change', {
            [this.field]: this.newVal
          });
          this.messageSuccess('编辑成功');
        }).finally(() => {
          this.isLoading = false;
        });
      }
    }
  };
</script>
<style lang="postcss">
    @keyframes textarea-edit-loading {
        to {
            transform: rotateZ(360deg)
        }
    }
</style>
<style lang='postcss' scoped>
    .iam-edit-select {
        position: relative;
        .edit-wraper {
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
                animation: 'textarea-edit-loading' 1s linear infinite;
            }
        }
        .edit-input {
            width: 100%;
        }
    }
</style>

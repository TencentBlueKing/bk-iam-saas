<template>
  <div class="iam-common-used-action-wrapper">
    <label class="title">{{ $t(`m.common['推荐权限']`) }}：</label>
    <section
      v-for="(item, index) in tagList"
      :key="item.$id"
      :class="[
        'tag-item',
        { 'is-active': active.includes(item.$id) && item.allCheck },
        { 'is-hover': item.hover ? item.hover.$id === item.$id : false }
      ]"
      :title="item.name"
      @click.stop="handleSelectTag(item, index)"
      @mouseenter="handleMouseEnter($event, item, index)"
      @mouseleave="handleMouseLeave($event, item, index)">
      <span class="text">{{ item.name }}</span>
      <Icon
        type="close-fill"
        class="remove-icon"
        v-if="item.id !== 0 && isEditMode"
        @click.stop="handleDelete(item.id, item.$id, index)" />
    </section>
    <template v-if="isEditMode && !isDisabled">
      <bk-button
        text
        theme="primary"
        icon="plus"
        size="small"
        ext-cls="iam-action-add-tag-cls"
        :title="tips"
        :disabled="isDisabled"
        v-if="!isEdit"
        @click="handleAddTag">{{ $t(`m.permApply['保存为常用操作']`) }}
      </bk-button>
      <div class="tag-edit" v-else>
        <bk-input
          clearable
          ref="input"
          v-model="tagName"
          style="flex: 0 0 212px;"
          @blur="handleBlur"
          @enter="handleEnter">
        </bk-input>
        <div class="action-item" @click.stop="handeSave">
          <Icon type="check-small" />
        </div>
        <div class="action-item" @click.stop="handeCancel">
          <Icon type="close-small" />
        </div>
      </div>
    </template>
  </div>
</template>
<script>
  import _ from 'lodash';
  export default {
    name: '',
    props: {
      curSelectActions: {
        type: Array,
        default: []
      },
      systemId: {
        type: String,
        default: ''
      },
      data: {
        type: Array,
        default: () => []
      },
      mode: {
        type: String,
        default: 'edit'
      },
      tagActionList: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        isEdit: false,
        tagName: '',
        active: [],
        hoverList: [],
        tagList: []
      };
    },
    computed: {
      tips () {
        return this.isDisabled ? this.$t(`m.permApply['请先勾选一些操作']`) : this.$t(`m.permApply['保存为常用操作提示']`);
      },
      isDisabled () {
        return this.curSelectActions.length < 1;
      },
      isEditMode () {
        return this.mode === 'edit';
      }
    },
    watch: {
      systemId () {
        this.active = [];
        this.hoverList = [];
        this.isEdit = false;
        this.tagName = '';
      },
      data: {
        handler (value) {
          this.tagList = _.cloneDeep(value);
        },
        immediate: true
      },
      tagActionList: {
        handler (value) {
          this.active = [];
          this.tagList.map(e => {
            const allCheck = e.action_ids.every(id => value.includes(id));
            this.$set(e, 'allCheck', allCheck);
            this.$set(e, 'isCheck', allCheck);
            if (!e.allCheck) {
              this.$set(e, 'active', []);
            } else {
              this.$set(e, 'active', [e.$id]);
            }
            if (e.active.length) {
              const active = e.active;
              this.active.push(...active);
            }
            return e;
          });
        },
        immediate: true
      }
    },
    methods: {
      handleSelectTag ({ $id, allCheck, active }, index) { // allCheck
        let flag = !allCheck;
        this.active.push(active);
        if (this.active.includes($id)) {
          this.active = [...this.active.filter(_ => _ !== $id)];
        } else {
          this.active.push($id);
          flag = true;
        }
        this.tagList[index].isCheck = !this.tagList[index].isCheck;
        const isCheck = this.tagList[index].isCheck;
        if (isCheck) {
          this.active.push($id);
        } else {
          this.active = [...this.active.filter(_ => _ !== $id)];
        }
        let curActions = this.tagList.find(_ => _.$id === $id).action_ids;
        const tempActions = [];
        this.tagList.forEach((item, index) => {
          if (item.$id !== $id && this.active.includes(item.$id)) {
            if (!flag) {
              const existActionIds = curActions.filter(v => item.action_ids.includes(v));
              tempActions.push(...existActionIds);
            } else {
              tempActions.push(...item.action_ids);
            }
          }
        });
        curActions = !flag
          ? [...curActions.filter(item => !tempActions.includes(item))]
          : [...new Set(curActions.concat(tempActions))];
        this.$emit('on-change', flag, curActions);
      },

      handleMouseEnter (e, payload, index) {
        const { $id } = payload;
        const curActions = this.tagList.find(_ => _.$id === $id).action_ids;
        const tempActions = [];
        this.tagList.forEach((item) => {
          if (item.$id !== $id && this.active.includes(item.$id)) {
            tempActions.push(...item.action_ids);
          }
        });
        const result = [...new Set(curActions.concat(tempActions))];
        const backData = { $id, index, actions: result };
        this.$set(payload, 'hover', backData);
        this.$emit('on-mouse-enter', backData);
      },

      handleMouseLeave (e, payload, index) {
        const { $id } = payload;
        const curActions = this.tagList.find(_ => _.$id === $id).action_ids;
        const tempActions = [];
        this.tagList.forEach((item) => {
          if (item.$id !== $id && this.active.includes(item.$id)) {
            const existActionIds = curActions.filter(v => item.action_ids.includes(v));
            tempActions.push(...existActionIds);
          }
        });
        const result = [...curActions.filter(item => !tempActions.includes(item))];
        const backData = { $id, index, actions: result };
        this.$delete(payload, 'hover', backData);
        this.$emit('on-mouse-leave', backData);
      },

      handleAddTag () {
        this.isEdit = true;
        this.$nextTick(() => {
          this.$refs.input.focus();
        });
      },

      handleBlur () {
        if (this.tagName === '') {
          this.isEdit = false;
        }
      },

      handleReset () {
        this.isEdit = false;
        this.tagName = '';
      },

      handleSetSelectData (payload) {
        this.active = this.active.filter(item => item !== payload);
      },

      handleSetActive (payload) {
        this.active.splice(0, this.active.length, ...[payload]);
      },

      handleEnter () {
        this.handeSave();
      },

      handleDelete (id, $id, index) {
        this.$emit('on-delete', id, $id, index);
      },

      handeSave () {
        if (this.tagName === '') {
          this.isEdit = false;
          return;
        }
        this.$emit('on-add', { actions: this.curSelectActions, name: this.tagName });
        this.handleReset();
      },

      handeCancel () {
        this.handleReset();
      }
    }
  };
</script>
<style lang="postcss">
    .iam-common-used-action-wrapper {
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        /* height: 40px; */
        .title {
            line-height: 32px;
            font-size: 12px;
            color: #313238;
            font-weight: bold;
        }
        .tag-item {
            position: relative;
            margin: 0 8px 8px 0;
            padding: 0 10px;
            height: 32px;
            line-height: 30px;
            background: #f0f1f5;
            border: 1px solid #f0f1f5;
            border-radius: 2px;
            &:hover {
                .remove-icon {
                    display: inline-block;
                }
            }
            &.is-hover {
                background: #eff5fe;
                border-color: #3a84ff;
            }
            &.is-active {
                background: #eff5fe;
                border-color: #3a84ff;
            }
            .text {
                display: inline-block;
                max-width: 130px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                font-size: 12px;
                cursor: pointer;
            }
            .remove-icon {
                display: none;
                position: absolute;
                top: -6px;
                right: -6px;
                background-color: #fff;
                border-radius: 50%;
                cursor: pointer;
            }
        }
        .iam-action-add-tag-cls {
            padding: 0;
            height: 32px;
            i.bk-icon {
                transform: translateY(-1px);
            }
            span {
                padding-bottom: 3px;
                border-bottom: 1px dashed #dcdee5;
            }
        }
        .tag-edit {
            display: flex;
            justify-content: flex-start;
            .action-item {
                margin-left: 2px;
                flex: 0 0 32px;
                height: 32px;
                line-height: 32px;
                background: #fff;
                border: 1px solid #c4c6cc;
                border-radius: 2px;
                text-align: center;
                cursor: pointer;
                i {
                    font-size: 24px;
                }
            }
            .control-icon {
                top: 17px !important;
            }
        }
    }
</style>

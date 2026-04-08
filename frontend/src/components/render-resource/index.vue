<template>
  <!-- eslint-disable max-len -->
  <div :class="['iam-resource-instance',
                { instance: type === 'instance' },
                { property: type === 'property' },
                { edit: currentMode === 'edit' },
                { 'is-not-expanded': !isExpanded },
                { 'is-group-instance': isInstanceByGroup },
                { 'is-group-property': isProPertyByGroup },
                { 'is-instance-hover': isInstanceHover },
                { 'normal': !isDisabled },
                { 'disabled': isDisabled },
                { 'is-show-order-number': needOrder }]"
    @mouseover="handleMouseenter"
    @mouseleave="handleMouseleave">
    <div
      :class="['header', { 'set-header-style': isExpanded && !isEdit }, { 'set-border-bottom': isExpanded && isEdit }]"
      @click="handleExpanded">
      <div class="info">
        <p>
          <span v-bk-xss-html="displayTitle" />
          <iam-svg name="icon-new" ext-cls="new-icon" v-if="isNew && curLanguageIsCn" />
          <iam-svg name="icon-new-en" ext-cls="new-icon" v-if="isNew && !curLanguageIsCn" />
        </p>
        <template>
          <template v-if="isEdit">
            <p v-bk-xss-html="subTitle" />
          </template>
          <template v-else>
            <p v-if="!isExpanded" v-bk-xss-html="subTitle" />
          </template>
        </template>
      </div>
      <div class="expand-action">
        <Icon :type="isExpanded ? 'down-angle' : 'up-angle'" />
        <Icon :type="isExpanded ? 'up-angle' : 'down-angle'" />
      </div>
    </div>
    <div
      :class="['content',
               { 'set-instance-style': isInstanceEdit },
               { 'set-property-style': isPropertyEdit }]" v-show="isExpanded">
      <slot />
    </div>
    <div :class="['add-instance-action', { 'is-bottom': type === 'instance' }, { 'is-top': type === 'property' }]" v-if="isShowEditAction" @click="handleAdd">
      {{ operateTitle }}
    </div>
    <div class="delete-action" v-if="isShowClearAction" @click="handleDelete">
      <Icon type="close-small" />
    </div>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      // edit: 编辑模式 '': 展示模式
      mode: {
        type: String,
        default: ''
      },
      // instance: 实例 property: 属性
      type: {
        type: String,
        default: 'instance'
      },
      expanded: {
        type: Boolean,
        default: false
      },
      subTitle: {
        type: String,
        default: ''
      },
      // 是否是一个分组: 一个分组既有实例也有属性
      isGroup: {
        type: Boolean,
        default: false
      },
      hovering: {
        type: Boolean,
        default: false
      },
      disabled: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      isNew: {
        type: Boolean,
        default: false
      },
      number: {
        type: Number,
        default: 0
      },
      needOrder: {
        type: Boolean,
        default: false
      },
      selectionMode: {
        type: String,
        default: 'all'
      },
      canDelete: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        isExpanded: this.expanded,
        currentMode: this.mode,
        isHovering: this.hovering,
        isDisabled: this.disabled
      };
    },
    computed: {
      isEdit () {
        return this.currentMode === 'edit';
      },
      isInstanceEdit () {
        return this.currentMode === 'edit' && this.type === 'instance';
      },
      isPropertyEdit () {
        return this.currentMode === 'edit' && this.type === 'property';
      },
      isShowClearAction () {
        return this.currentMode === 'edit' && this.canDelete;
      },
      isShowEditAction () {
        return this.currentMode === 'edit' && !this.isGroup && this.selectionMode === 'all';
      },
      operateTitle () {
        return this.type === 'instance' ? this.$t(`m.resource['添加属性选择']`) : this.$t(`m.resource['添加拓扑实例']`);
      },
      isInstanceByGroup () {
        return this.isGroup && this.type === 'instance';
      },
      isProPertyByGroup () {
        return this.isGroup && this.type === 'property';
      },
      isInstanceHover () {
        return this.isGroup && this.type === 'property' && this.isHovering;
      },
      displayTitle () {
        if (this.type === 'instance') {
          return this.title || `${this.$t(`m.resource['拓扑实例']`)}: `;
        }
        return this.title || `${this.$t(`m.resource['属性条件']`)}: `;
      }
    },
    watch: {
      mode (value) {
        this.currentMode = value;
      },
      expanded (value) {
        this.isExpanded = !!value;
      },
      hovering (value) {
        this.isHovering = !!value;
      },
      disabled (value) {
        this.isDisabled = !!value;
        if (value) {
          this.isExpanded = false;
        }
      }
    },
    methods: {
      handleExpanded () {
        if (this.isDisabled) {
          return;
        }
        this.isExpanded = !this.isExpanded;
        this.$emit('update:expanded', this.isExpanded);
        this.$emit('on-expand', this.isExpanded);
      },
      handleAdd () {
        if (this.isDisabled) {
          return;
        }
        this.$emit('on-add');
      },
      handleDelete () {
        if (this.isDisabled) {
          return;
        }
        this.$emit('on-delete');
      },
      handleMouseenter () {
        if (this.isDisabled) {
          return;
        }
        this.$emit('on-mouseover');
      },
      handleMouseleave () {
        if (this.isDisabled) {
          return;
        }
        this.$emit('on-mouseleave');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-resource-instance {
        min-height: 72px;
        position: relative;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        background: #fff;
        box-shadow: 0px 1px 2px 0px rgba(255, 255, 255, .3);
        z-index: 1;
        &.instance.normal::before {
            content: '';
            position: absolute;
            top: 20px;
            width: 3px;
            height: 14px;
            background: #3a84ff;
        }
        &.property.normal::before {
            content: '';
            position: absolute;
            top: 20px;
            width: 3px;
            height: 14px;
            background: #9101ff;
        }
        &.instance.disabled::before {
            content: '';
            position: absolute;
            top: 20px;
            width: 3px;
            height: 14px;
            background: #dcdee5;
        }
        &.property.disabled::before {
            content: '';
            position: absolute;
            top: 20px;
            width: 3px;
            height: 14px;
            background: #dcdee5;
        }
        &.is-group-instance {
            border-radius: 2px 2px 0 0;
        }
        &.is-group-property {
            margin-top: -1px;
            border-radius: 0 0 2px 2px;
        }
        &.is-instance-hover {
            border-top-color: #a3c5fd;
        }
        &.is-not-expanded.normal:hover {
            border-color: #a3c5fd;
            .header {
                .expand-action {
                    i {
                        color: #3a84ff;
                    }
                }
            }
        }
        &.is-show-order-number {
            border-radius: 0 0 2px 2px;
        }
        &.edit.normal:hover {
            .add-instance-action {
                display: block;
            }
            .delete-action {
                display: block;
            }
            .header {
                .expand-action {
                    i {
                        color: #3a84ff;
                    }
                }
            }
        }
        &.disabled {
            .header {
                cursor: not-allowed;
                &:hover {
                    .expand-action {
                        i {
                            color: #dcdee5;
                        }
                    }
                }
                .expand-action {
                    i {
                        color: #dcdee5;
                    }
                }
                .info {
                    p:nth-child(1) {
                        color: #dcdee5;
                    }
                    p:nth-child(2) {
                        color: #dcdee5;
                    }
                }
            }
        }
        .header {
            padding: 20px;
            display: flex;
            justify-content: space-between;
            cursor: pointer;
            &:hover {
                .expand-action {
                    i {
                        color: #3a84ff;
                    }
                }
            }
            &.set-header-style {
                padding-bottom: 0;
            }
            &.set-border-bottom {
                border-bottom: 1px solid #dcdee5;
            }
            .info {
                font-size: 12px;
                p:nth-child(1) {
                    line-height: 16px;
                    color: #313238;
                    font-weight: 700;
                    font-size: 14px;
                }
                p:nth-child(2) {
                    line-height: 16px;
                    color: #63656e;
                    margin-top: 4px;
                }
                .new-icon {
                    position: relative;
                    top: 1px;
                    width: 24px;
                }
            }
            .expand-action {
                width: 32px;
                text-align: right;
                cursor: pointer;
                i {
                    display: block;
                    font-size: 16px;
                    color: #c4c6cc;
                }
            }
        }
        .content {
            padding: 0 20px 19px 20px;
            &.set-property-style {
                padding-top: 19px;
                background: #fafbfd;
            }
            &.set-instance-style {
                /* height: 330px; */
                height: calc(100% - 50px);
                padding: 0;
                /* background: #f5f6fa; */
                background: #fafbfd;
            }
        }
        .add-instance-action {
            display: none;
            position: absolute;
            left: -1px;
            width: calc(100% + 2px);
            height: 20px;
            border: 1px dashed #a3c5fd;
            border-radius: 2px 2px 0 0;
            background: #eff5ff;
            font-size: 12px;
            color: #3a84ff;
            text-align: center;
            cursor: pointer;
            &.is-top {
                top: -20px;
            }
            &.is-bottom {
                bottom: -20px;
            }
        }
        .delete-action {
            display: none;
            position: absolute;
            top: -1px;
            right: -16px;
            width: 16px;
            height: 16px;
            border-radius: 0 2px 2px 0;
            background: #a3c5fd;
            cursor: pointer;
            i {
                position: absolute;
                top: 2px;
                left: 1px;
                color: #fff;
                font-size: 14px;
            }
        }
    }
</style>

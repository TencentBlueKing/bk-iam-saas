<template>
  <div
    ref="searchSelect"
    class="iam-bk-search-select"
    :class="{
      'focused': focused
    }"
    v-bind="$attrs"
    @click="handleSearchSelectClick">
    <div ref="wrap" class="search-select-wrap">
      <div
        ref="tagGroup"
        class="search-tag-group"
        :style="tagGroupStyles">
        <render-tag
          v-for="(item, index) in renderTagList"
          ref="tag"
          :key="`${item.id}_${index}`"
          :index="index"
          :data="item"
          @delete="handleTagDelete"
          @focus="handleInputFocus"
          @change="handleTagChange" />
        <div v-if="isTagMultLine" class="mult-tag-placeholder" key="multPlaceholder">...</div>
        <div class="search-input-box" ref="input" key="input" :style="searchInputBoxStyles" @click.stop="">
          <div style="position: absolute; top: -9999px; left: -9999px;">
            <pre ref="realInputContent" style="display: block; visibility: hidden; font: inherit;">
                            {{ localValue }}
                        </pre>
          </div>
          <div style="min-height: 22px; white-space: normal; word-break: break-all; visibility: hidden;">
            {{ localValue }}
          </div>
          <textarea
            ref="textarea"
            class="input-box"
            :value="localValue"
            :placeholder="placeholderText"
            spellcheck="false"
            @focus="handleInputFocus"
            v-bk-clickoutside="handleInputOutSide"
            @input="handleInputChange"
            @keydown="handleInputKeydown" />
        </div>
        <div
          v-if="focused && showTips"
          v-once
          style="margin-top: 4px; font-size: 12px; line-height: 22px; color: #C4C6CC">
          {{ inputTips }}
        </div>
      </div>
      <div class="search-nextfix">
        <i
          v-if="isClearable"
          class="search-clear bk-icon icon-close-circle-shape"
          @click.self="handleClearAll" />
        <slot name="nextfix">
          <i
            @click.stop="handleSubmit"
            class="bk-icon icon-search search-nextfix-icon"
            :class="{ 'is-focus': focused }" />
        </slot>
      </div>
    </div>
    <div class="bk-select-tips" v-if="validateStr.length">
      <slot name="validate">
        <i class="bk-icon icon-exclamation-circle-shape select-tips"></i>{{validateStr || ''}}
      </slot>
    </div>
  </div>
</template>
<script>
  import Vue from 'vue';
  import _ from 'lodash';
  import il8n from '@/language';
  import Tippy from 'bk-magic-vue/lib/utils/tippy';
  import {
    popperConfig,
    encodeRegexp,
    generatorMenu
  } from './helper';
  import locale from './locale';
  import KeyMenu from './key-menu';
  import ValueMenu from './value-menu';
  import SuggestMenu from './suggest-menu';
  import RenderTag from './render-tag';

  export default {
    name: 'bk-search-select',
    provide () {
      return {
        'searchSelect': this
      };
    },
    components: {
      RenderTag
    },

    model: {
      prop: 'values',
      event: 'change'
    },

    props: {
      data: {
        default: () => [],
        validator (data) {
          if (!Array.isArray(data)) {
            return false;
          }
          return true;
        }
      },
      explainCode: {
        type: String,
        default: il8n('common', '：')
      },
      placeholder: {
        type: String,
        default: locale.t('bk.searchSelect.placeholder')
      },
      emptyText: {
        type: String,
        default: locale.t('bk.searchSelect.emptyText')
      },

      displayKey: {
        type: String,
        default: 'name'
      },
      primaryKey: {
        type: String,
        default: 'id'
      },
      condition: {
        type: Object,
        default () {
          return {};
        }
      },
      values: {
        type: Array,
        default () {
          return [];
        }
      },
      remoteEmptyText: {
        type: String,
        default: locale.t('bk.searchSelect.remoteEmptyText')
      },
      remoteLoadingText: {
        type: String,
        default: locale.t('bk.searchSelect.remoteLoadingText')
      },
      showCondition: {
        type: Boolean,
        default: true
      },
      readonly: {
        type: Boolean,
        default: false
      },
      defaultFocus: {
        type: Boolean,
        default: false
      },
      clearable: {
        type: Boolean,
        default: false
      },
      maxTagWidth: {
        type: Number,
        default: 100
      },
      showTips: {
        type: Boolean,
        default: false
      }
    },

    data () {
      return {
        menu: generatorMenu(),
        chipList: [],
        maxRenderTagNums: -1,
        textareaWidth: 0,
        focused: this.defaultFocus,
        localValue: '',
        defaultCondition: {},
        validateStr: ''
      };
    },

    computed: {
      currentSelectKey () {
        return this.data.find(item => item[this.primaryKey] === this.menu.id) || {};
      },
      // 通过输入框直接搜索的key
      defaultInputKey () {
        for (let i = 0; i < this.data.length; i++) {
          const currentkey = this.data[i];
          // 没有配置自选项的key才支持设置为默认key
          if (currentkey.remote || currentkey.children || currentkey.remoteMethod) {
            continue;
          }
          if (currentkey.default) {
            return currentkey;
          }
        }
        return null;
      },

      placeholderText  () {
        return this.chipList.length > 0 ? '' : this.placeholder;
      },
      renderTagList () {
        if (this.focused) {
          return this.chipList;
        }
        if (this.maxRenderTagNums < 1) {
          return this.chipList;
        }
        return this.chipList.slice(0, this.maxRenderTagNums);
      },
      isTagMultLine: {
        get () {
          if (this.focused) {
            return false;
          }
          return this.maxRenderTagNums > 0;
        },
        set (value) {
          if (!value) {
            this.maxRenderTagNums = -1;
          }
          return value;
        }
      },

      tagGroupStyles () {
        return {
          'width': `calc(100% - 50px)`,
          'max-height': this.focused ? '320px' : '30px',
          'white-space': this.focused ? 'initial' : 'nowrap'
        };
      },

      searchInputBoxStyles () {
        const styles = {
          'position': 'relative',
          'width': this.focused ? `${this.textareaWidth}px` : 'auto',
          'min-width': '20px',
          'max-width': '100%'
        };
        if (this.chipList.length < 1) {
          styles['width'] = '100%';
        }

        return styles;
      },

      isClearable () {
        return !this.readonly && this.clearable && this.chipList.length > 0;
      }
    },

    watch: {
      values: {
        handler (values) {
          if (values !== this.chipList) {
            this.chipList = values;
          }
        },
        deep: true,
        immediate: true
      },
      menu: {
        handler  () {
          this.updateLocalInput();
        },
        deep: true
      }
    },

    created () {
      this.panelInstance = null;
      this.popperInstance = null;
      this.renderTagInstance = null;

      this.defaultCondition = {
        name: locale.t('bk.searchSelect.condition')
      };
      if (!this.defaultCondition[this.displayKey]) {
        this.defaultCondition[this.displayKey] = locale.t('bk.searchSelect.condition');
      }

      this.inputTips = locale.t('bk.searchSelect.tips');

      this.calcTextareaWidth = _.throttle(this._calcTextareaWidth, 30);
      this.showPopper = _.throttle(this._showMenu, 50);
      this.remoteExecuteImmediate();
      if (this.$store.state.fromRouteName === 'myPerm') {
        this.chipList = [];
        this.triggerChange();
      }
    },

    beforeDestroy () {
      this.popperInstance && this.popperInstance.destroy(true);
    },

    methods: {
      _calcTextareaWidth () {
        this.$nextTick(() => {
          const { width } = this.$refs.realInputContent.getBoundingClientRect();
          this.textareaWidth = width + 20;
        });
      },
      // 显示 key 面板
      _showKeyMenu (lastPanelInstance) {
        if (this.panelInstance) {
          return;
        }
        let instance = null;
        if (lastPanelInstance && lastPanelInstance.$options.name === 'BKSearchKey') {
          instance = lastPanelInstance;
        } else {
          instance = new Vue(KeyMenu);
          instance.searchSelect = this;
          instance.$on('select', this.handleKeyChange);
          instance.$on('select-conditon', this.handleKeyConditonChange);
        }
        if (instance.needRender) {
          !instance._isMounted && instance.$mount();
          instance.generatorList();
          this.panelInstance = instance;
        }
      },
      // 显示 value 面板
      _showValueMenu (lastPanelInstance) {
        if (this.panelInstance) {
          return;
        }
        let instance = null;
        if (lastPanelInstance && lastPanelInstance.$options.name === 'BKSearchValue') {
          instance = lastPanelInstance;
        } else {
          instance = new Vue(ValueMenu);
          instance.searchSelect = this;
          instance.$on('select-condition', this.handleValueConditionChange);
          instance.$on('select-check', this.handleMultCheck);
          instance.$on('change', this.handleValueChange);
          instance.$on('cancel', this.handleValueCancel);
        }

        let realValue = this.localValue;
        const keyText = this.currentSelectKey[this.displayKey] + this.explainCode || '';
        realValue = realValue.slice(keyText.length);
        const conditionText = this.menu.condition[this.displayKey] || '';
        realValue = realValue.slice(conditionText.length);

        instance.search = realValue.trim();
        instance.currentItem = this.currentSelectKey;
        instance.menu = this.menu;

        if (instance.needRender) {
          !instance._isMounted && instance.$mount();
          instance.generatorList();
          this.panelInstance = instance;
        }
        this.$emit('on-click-menu', { menu: this.menu });
      },
      // 显示 suggest 面板
      _showSuggestMenu (lastPanelInstance) {
        if (this.panelInstance) {
          return;
        }
        let instance = null;
        if (lastPanelInstance && lastPanelInstance.$options.name === 'BKSearchSuggest') {
          instance = lastPanelInstance;
        } else {
          instance = new Vue(SuggestMenu);
          instance.searchSelect = this;
          instance.$on('select', this.handleMenuSuggestSelect);
        }
        if (instance.needRender) {
          !instance._isMounted && instance.$mount();
          instance.generatorList();
          this.panelInstance = instance;
        }
      },

      _showMenu () {
        if (!this.popperInstance) {
          this.popperInstance = Tippy(this.$refs.input, { ...popperConfig });
        }

        const lastPanelInstance = this.panelInstance;
        this.panelInstance = null;
        setTimeout(() => {
          this._showKeyMenu(lastPanelInstance);
          this._showValueMenu(lastPanelInstance);
          this._showSuggestMenu(lastPanelInstance);

          if (!this.panelInstance) {
            lastPanelInstance && lastPanelInstance.$destroy();
            this.hidePopper(lastPanelInstance);
            return;
          }
          // 两次的弹出面板不是同一类型——销毁上一个
          if (lastPanelInstance
            && lastPanelInstance.$options.name !== this.panelInstance.$options.name) {
            lastPanelInstance.$destroy();
          }
          this.popperInstance.set({
            zIndex: window.__bk_zIndex_manager.nextZIndex()
          });
          this.popperInstance.setContent(this.panelInstance.$el);
          this.popperInstance.popperInstance.update();
          this.popperInstance.show();
          this.renderTagInstance && this.renderTagInstance.hidePopper();
        });
      },

      hidePopper () {
        if (this.panelInstance) {
          this.panelInstance.$destroy();
          this.panelInstance = null;
        }
        if (this.popperInstance) {
          this.popperInstance.hide(0);
        }
      },

      remoteExecuteImmediate () {
        this._remoteKeyImmediateChildrenMap = {};

        for (let i = 0; i < this.data.length; i++) {
          const currentItem = this.data[i];
          if (typeof currentItem.remoteMethod === 'function'
            && currentItem.remoteExecuteImmediate) {
            (async () => {
              try {
                const children = await currentItem.remoteMethod();
                this._remoteKeyImmediateChildrenMap[currentItem[this.primaryKey]] = children;
              } catch {}
            })();
          }
        }
      },

      updateLocalInput () {
        if (!this.menu.id) {
          this.localValue = '';
        } else {
          let text = `${this.currentSelectKey[this.displayKey]}${this.explainCode}`;
          if (this.menu.condition[this.primaryKey]) {
            text += `${this.menu.condition[this.displayKey]} `;
          }
          text += this.menu.checked.map(_ => _[this.displayKey]).join(' | ');
          this.localValue = text;
        }
        this.calcTextareaWidth();
        setTimeout(() => {
          this.$refs.textarea.focus();
        });
      },

      valueValidate (valList) {
        let validate = true;
        if (this.currentSelectKey
          && this.currentSelectKey.validate
          && typeof this.currentSelectKey.validate === 'function') {
          validate = this.currentSelectKey.validate([...valList], this.currentSelectKey);
          if (typeof validate === 'string') {
            this.validateStr = validate;
            validate = false;
          } else {
            validate && (this.validateStr = '');
          }
        } else {
          this.validateStr = '';
        }
        return validate;
      },

      appendChipList  (item) {
        const validate = this.valueValidate(item.values);
        if (!validate) return;

        const result = [...this.chipList];
        result.push(item);

        // 根据primaryKey去重
        const memoMap = {};
        const stack = [];
        for (let i = result.length - 1; i >= 0; i--) {
          const primaryKey = result[i][this.primaryKey];
          if (!primaryKey) {
            stack.unshift(result[i]);
            continue;
          }
          if (!memoMap[primaryKey]) {
            stack.unshift(result[i]);
            memoMap[primaryKey] = true;
          }
        }
        this.chipList = Object.freeze(stack);
        this.triggerChange();
      },

      triggerChange () {
        this.menu = generatorMenu();
        this.$emit('change', [...this.chipList]);
      },

      handleSearchSelectClick () {
        this.handleInputFocus();
      },

      handleInputFocus () {
        this.renderTagInstance && this.renderTagInstance.hidePopper();
        if (this.readonly) {
          return;
        }

        this.focused = true;

        this.$refs.textarea.focus();
        this.showPopper();
        this.$emit('focus');
      },

      handleInputOutSide (event) {
        if (!this.focused) {
          return;
        }
        let parent = event.target.parentNode;
        while (parent && parent.classList) {
          if (parent.classList.contains('iam-bk-search-list') || parent.classList.contains('iam-bk-search-select')) {
            return;
          }
          parent = parent.parentNode;
        }
        this.hidePopper();
        this.maxRenderTagNums = -1;
        this.focused = false;

        this.$nextTick(() => {
          const allTag = this.$refs.tagGroup.querySelectorAll('.search-tag-box');
          const {
            width: searchSelectWidth
          } = this.$refs.searchSelect.getBoundingClientRect();

          let tagWidthTotal = 0;
          for (let i = 0; i < allTag.length; i++) {
            const { width } = allTag[i].getBoundingClientRect();
            if (tagWidthTotal + width + 50 < searchSelectWidth) {
              tagWidthTotal = tagWidthTotal + width + 6;
            } else {
              this.maxRenderTagNums = i;
              break;
            }
          }
        });
        this.$emit('blur');
      },

      handleInputChange (event) {
        const text = event.target.value.replace(/[\r\n]/, '');
        if (text === '') {
          this.menu = generatorMenu();
        }
        this.localValue = text;
        this.calcTextareaWidth();
        this.showPopper();
        this.$emit('input', { event, text });
      },

      keyDelete (event) {
        // 删除逻辑的优先级需要保持下面的顺序

        // 删除value
        if (this.menu.checked.length > 0) {
          event.preventDefault();
          const checked = [...this.menu.checked];
          checked.pop();
          this.menu.checked = Object.freeze(checked);
          return;
        }
        // 删除condition
        const condition = this.menu.condition[this.displayKey];
        const localValue = this.currentSelectKey[this.displayKey] + this.explainCode;
        if (condition && localValue + condition === this.localValue) {
          event.preventDefault();
          this.menu.checked = [];
          this.menu.condition = {};
          this.showPopper();
          return;
        }
        // 删除已选key
        if (this.currentSelectKey[this.primaryKey]) {
          const regx = new RegExp(`${encodeRegexp(this.explainCode)}$`);
          if (regx.test(this.localValue)) {
            event.preventDefault();
            this.menu = generatorMenu();
            this.showPopper();
            return;
          }
        }
        // 删除输入内容
        if (this.localValue !== '') {
          return;
        }
        // 删除tag
        if (this.chipList.length > 0) {
          const result = [...this.chipList];
          result.pop();
          this.chipList = Object.freeze(result);
          this.triggerChange();
          this.showPopper();
        }
      },

      keySubmit () {
        // 输入框没有内容
        if (!this.localValue) {
          return;
        }

        if (!this.currentSelectKey[this.primaryKey]) {
          // 没有选中key

          if (this.defaultInputKey) {
            // 已配置默认key

            const id = this.defaultInputKey[this.primaryKey];
            const name = this.defaultInputKey[this.displayKey];

            this.appendChipList({
              [this.primaryKey]: id,
              [this.displayKey]: name,
              values: [
                {
                  [this.primaryKey]: this.localValue,
                  [this.displayKey]: this.localValue
                }
              ]
            });
            this.showPopper();
          } else {
            // 直接使用输入框的内容
            this.appendChipList({
              [this.primaryKey]: this.localValue,
              [this.displayKey]: this.localValue,
              values: []
            });
            this.showPopper();
          }
        } else {
          // 已选中key

          // 1，如果value配置了本地children或者支持remoteMethod，输入框直接enter无效（需要通过value面板选择）
          if (this.currentSelectKey.children
            || typeof this.currentSelectKey.remoteMethod === 'function') {
            return;
          }
          // 2, enter时value不能为空
          const keyText = this.currentSelectKey[this.displayKey] + this.explainCode;
          const conditionText = this.menu.condition[this.displayKey] || '';
          if (this.localValue.trim() === keyText + conditionText) {
            this.showPopper();
            return;
          }

          // 提交结果
          let realValue = this.localValue.replace(keyText, '');
          if (conditionText) {
            realValue = realValue.replace(this.menu.condition[this.displayKey], '');
          }

          const id = this.currentSelectKey[this.primaryKey];
          const name = this.currentSelectKey[this.displayKey];
          this.appendChipList({
            [this.primaryKey]: id,
            [this.displayKey]: name,
            values: [
              {
                [this.primaryKey]: realValue,
                [this.displayKey]: realValue
              }
            ],
            condition: this.menu.condition
          });
          // this.showPopper()
        }
      },

      handleInputKeydown (event) {
        if (this.readonly) {
          event.preventDefault();
          return;
        }
        if (['ArrowDown', 'ArrowUp'].includes(event.code)) {
          event.preventDefault();
          return;
        }
        if (['Backspace'].includes(event.code)) {
          this.keyDelete(event);
          return;
        }
        if (['Enter', 'NumpadEnter'].includes(event.code) && !event.isComposing) {
          event.preventDefault();
          if (this.popperInstance && this.popperInstance.state.isVisible) {
            return;
          }
          this.keySubmit(event);
        }
      },

      handleSubmit (event) {
        this.keySubmit();
        // 通过搜索按钮触发提交不继续显示keymemu
        setTimeout(() => {
          this.$refs.textarea.blur();
          this.focused = false;
          this.hidePopper();
        }, 100);
        this.$emit('clear', event);
      },

      handleTagChange (index, value) {
        const list = [...this.chipList];
        list.splice(index, 1, value);
        this.chipList = Object.freeze(list);
        this.triggerChange(false);
      },

      handleTagDelete (index) {
        const result = [...this.chipList];
        result.splice(index, 1);
        this.chipList = Object.freeze(result);
        this.triggerChange();
      },

      handleClearAll () {
        this.menu = generatorMenu();
        this.chipList = [];
        this.triggerChange();
        this.showPopper();
        this.$emit('clear');
      },

      handleKeyChange (key) {
        this.menu = generatorMenu();
        this.menu.id = key[this.primaryKey];

        this.showPopper();
      },

      handleKeyConditonChange (value) {
        this.appendChipList(value);
        this.showPopper();
      },

      handleValueConditionChange (condition) {
        this.menu.condition = condition;
        this.showPopper();
      },

      handleMultCheck (values) {
        this.menu.checked = Object.freeze(values);
      },

      handleValueChange () {
        const id = this.currentSelectKey[this.primaryKey];
        const name = this.currentSelectKey[this.displayKey];
        this.appendChipList({
          [this.primaryKey]: id,
          [this.displayKey]: name,
          values: this.menu.checked,
          condition: this.menu.condition
        });
        this.showPopper();
      },

      handleValueCancel () {
        this.menu = generatorMenu();
        this.showPopper();
      },

      handleMenuSuggestSelect (value) {
        this.appendChipList(value);
        this.showPopper();
      },

      getInputInstance () {
        return this.$refs.textarea;
      }
    }
  };
</script>

<style lang="postcss">
    @import './styles/search-select.css';
    @import './styles/search-select-menu.css';
</style>

<template>
  <div class="infinite-list" @scroll="rootScroll">
    <div class="ghost-wrapper" :style="ghostStyle"></div>
    <div class="render-wrapper" ref="content">
      <div class="organization-content">
        <div class="organization-item" v-for="item in renderOrganizationList" :key="item.id">
          <Icon bk type="folder-open-shape" :class="['folder-icon', { 'active': item.selected }]" />
          <span class="organization-name"
            :class="item.selected ? 'active' : ''"
            :title="item.name"
            @click.stop="nodeClick(item)">{{ item.name }}</span>
          <span class="user-count" v-if="item.showCount" @click.stop="nodeClick(item)">
            {{ '(' + item.count + ')' }}
          </span>
          <div class="organization-checkbox" v-if="item.showRadio">
            <bk-checkbox
              :true-value="true"
              :false-value="false"
              :disabled="item.disabled"
              v-model="item.is_selected"
              @change="checkboxChange(...arguments, item)">
            </bk-checkbox>
          </div>
        </div>
      </div>
      <div class="user-content">
        <div class="user-item" v-for="item in renderUserList" :key="item.id">
          <iam-svg name="user-default" ext-cls="user-icon" />
          <span class="user-name"
            :class="item.selected ? 'active' : ''"
            :title="item.username" @click.stop="nodeClick(item)">
            {{ item.username }}
            <template v-if="item.display_name">
              (<span class="cn-name">{{ item.display_name }}</span>)
            </template>
          </span>
        </div>
      </div>
    </div>
  </div>

</template>
<script>
  import _ from 'lodash';

  export default {
    name: 'infinite-list',
    props: {
      // 所有数据
      allData: {
        type: Array,
        default: () => []
      },
      // 每个节点的高度
      itemHeight: {
        type: Number,
        default: 32
      }
    },
    data () {
      return {
        startIndex: 0,
        endIndex: 0
      };
    },
    computed: {
      ghostStyle () {
        return {
          height: this.allData.length * this.itemHeight + 'px'
        };
      },
      // 页面渲染的数据
      renderData () {
        // 渲染在可视区的数据
        return this.allData.slice(this.startIndex, this.endIndex);
      },
      renderOrganizationList () {
        return this.renderData.filter(item => item.type === 'department');
      },
      renderUserList () {
        return this.renderData.filter(item => item.type === 'user');
      }
    },
    mounted () {
      this.endIndex = Math.ceil(this.$el.clientHeight / this.itemHeight);
    },
    methods: {
      /**
       * 滚动回调函数
       */
      rootScroll: _.throttle(function () {
        this.updateRenderData(this.$el.scrollTop);
      }, 0),

      /**
       * 更新可视区渲染的数据列表
       *
       * @param {Number} scrollTop 滚动条高度
       */
      updateRenderData (scrollTop = 0) {
        // 可视区显示的条数
        const count = Math.ceil(this.$el.clientHeight / this.itemHeight);
        // 滚动后可视区新的 startIndex
        const newStartIndex = Math.floor(scrollTop / this.itemHeight);
        // 滚动后可视区新的 endIndex
        const newEndIndex = newStartIndex + count;
        this.startIndex = newStartIndex;
        this.endIndex = newEndIndex;
        this.$refs.content.style.transform = `translate3d(0, ${newStartIndex * this.itemHeight}px, 0)`;
      },

      /**
       * 点击节点
       *
       * @param {Object} node 当前节点
       */
      nodeClick (node) {
        this.$emit('on-click', node);
      },

      /**
       * 搜索结果中组织的多选框 change 回调函数
       *
       * @param {Boolean} newVal
       * @param {Boolean} oldVal
       * @param {Boolean} localVal
       * @param {Object} node 当前节点
       */
      checkboxChange (newVal, oldVal, localVal, node) {
        this.$emit('on-checked', newVal, oldVal, localVal, node);
      }
    }
  };
</script>
<style lang="postcss">
    @import './index.css';
</style>

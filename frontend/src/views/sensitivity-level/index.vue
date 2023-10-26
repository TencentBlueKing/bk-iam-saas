<template>
  <div class="sensitivity-wrapper">
    <div class="sensitivity-left-layout" :draggable="false" :style="leftStyle">
      <SensitivitySystems @on-select-system="handleSelectSystem" />
    </div>
    <div class="sensitivity-drag-dotted-line" v-if="isDrag" :style="dottedLineStyle" />
    <div class="sensitivity-drag-line" :style="dragStyle">
      <img
        class="drag-bar"
        src="@/images/drag-icon.svg"
        alt=""
        :draggable="false"
        @mousedown="handleDragMouseenter($event)"
        @mouseout="handleDragMouseleave($event)"
      />
    </div>
    <div class="sensitivity-right-layout" :draggable="false" :style="rightStyle">
      <SensitivityRightLayout :cur-system-data="curSystemData" />
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import SensitivitySystems from '@/views/sensitivity-level/components/sensitivity-systems.vue';
  import SensitivityRightLayout from '@/views/sensitivity-level/components/sensitivity-right-layout.vue';
  export default {
    name: 'SensitivityLevel',
    components: {
      SensitivitySystems,
      SensitivityRightLayout
    },
    data () {
      return {
        isDrag: false,
        // 默认280，加上全局24px的内边距
        dragWidth: 280,
        dragRealityWidth: 280,
        navWidth: 240,
        curSystemData: {}
      };
    },
    computed: {
    ...mapGetters(['user', 'navStick']),
    leftStyle () {
      if (this.dragWidth > 0) {
        return {
          flexBasis: `${this.dragWidth}px`
        };
      }
      return {
        flexBasis: '280px'
      };
    },
    rightStyle () {
      if (this.dragWidth > 0) {
        return {
          width: `calc(100% - ${this.dragWidth}px)`
        };
      }
      return {
        width: `calc(100% - 280px)`
      };
    },
    dottedLineStyle () {
      return {
        left: `${this.dragRealityWidth}px`
      };
    },
    dragStyle () {
      return {
        left: `${this.dragWidth}px`
      };
    }
    },
    watch: {
      navStick (value) {
        this.navWidth = value ? 240 : 60;
      }
    },
    methods: {
      handleSelectSystem (payload) {
        this.curSystemData = Object.assign({}, payload);
      },

      handleDragMouseenter (e) {
        if (this.isDrag) {
          return;
        }
        this.isDrag = true;
        document.addEventListener('mousemove', this.handleDragMousemove);
        document.addEventListener('mouseup', this.handleDragMouseup);
      },

      handleDragMouseleave (e) {},

      /**
       * handleDragMouseup
       */
      handleDragMouseup (e) {
        this.dragWidth = this.dragRealityWidth;
        this.isDrag = false;
        document.removeEventListener('mousemove', this.handleDragMousemove);
        document.removeEventListener('mouseup', this.handleDragMouseup);
      },

      /**
       * handleDragMousemove
       */
      handleDragMousemove (e) {
        if (!this.isDrag) {
          return;
        }
        // 可拖拽范围
        const minWidth = this.navWidth + 280;
        const maxWidth = this.navWidth + 540;
        if (e.clientX < minWidth || e.clientX >= maxWidth) {
          return;
        }
        this.dragRealityWidth = e.clientX - this.navWidth;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.sensitivity-wrapper {
  position: relative;
  display: flex;
  padding-left: 16px;
  padding-right: 16px;
  .sensitivity-left-layout {
    position: relative;
    flex-grow: 0;
    flex-shrink: 0;
    margin-right: 16px;
    position: relative;
    min-width: 280px;
  }
  .sensitivity-drag-dotted-line {
    position: absolute;
    top: 0;
    left: 280px;
    height: 100%;
    z-index: 1500;
  }
  .sensitivity-drag-line {
    position: absolute;
    top: 0;
    left: 280px;
    height: 100%;
    z-index: 1500;
    .drag-bar {
      position: relative;
      top: calc(50% - 17px);
      left: 20px;
      width: 9px;
      background: transparent;
      cursor: col-resize;
    }
  }
  .sensitivity-right-layout {
    position: relative;
    background-color: #ffffff;
    overflow: auto;
  }
}
</style>

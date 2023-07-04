<template>
  <div class="filter-item">
    <div class="title">
      {{ title }}
    </div>
    <div>
      <bk-dropdown-menu
        ref="dropdown"
        align="right"
        trigger="click"
        @show="handleDropdownShow"
        @hide="handleDropdownHide">
        <div slot="dropdown-trigger" class="trigger-wrapper">
          <span>{{ dataDisplay[currentActive] }}</span>
          <Icon :type="isDropdownShow ? 'up-angle' : 'down-angle'" class="icon" />
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li
            v-for="(item, key) in dataDisplay"
            :key="key"
            :class="{ 'active': currentActive === key }">
            <a @click="handleChange(key)">
              {{ dataDisplay[key] }}
            </a>
          </li>
        </ul>
      </bk-dropdown-menu>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import il8n from '@/language';

  export default {
    name: '',
    props: {
      title: {
        type: String,
        default: il8n('myApply', '申请列表')
      },
      data: {
        type: Object,
        default: () => {
          return {
            'all': il8n('common', '全部'),
            'wait': il8n('myApproval', '待审批')
          };
        }
      },
      active: {
        type: [Number, String],
        required: true
      }
    },
    data () {
      return {
        isDropdownShow: false,
        currentActive: this.active,
        dataDisplay: []
      };
    },
    watch: {
      data: {
        handler (value) {
          this.dataDisplay = _.cloneDeep(value);
        },
        immediate: true
      }
    },
    methods: {
      /**
       * handleDropdownShow
       */
      handleDropdownShow () {
        this.isDropdownShow = true;
      },

      /**
       * handleDropdownHide
       */
      handleDropdownHide () {
        this.isDropdownShow = false;
      },

      /**
       * handleChange
       */
      handleChange (payload) {
        this.currentActive = payload;
        this.$refs.dropdown.hide();
        this.$emit('on-change', payload);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    @import './filter-item.css';
</style>

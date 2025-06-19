<template>
  <div>
    <BkUserSelector
      v-model="list"
      ref="iamUserSelectorRef"
      :api-base-url="apiBaseUrl"
      :tenant-id="tenantId"
      :multiple="true"
      :required="true"
      v-bind="$attrs"
      v-on="$listeners"
      @change="handleChange"
    />
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  export default {
    name: 'IamUserSelector',
    props: {
      value: {
        type: Array,
        default: () => []
      },
      isErrorClass: {
        type: String,
        default: ''
      },
      enableEmpty: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        apiBaseUrl: window.BK_USER_WEB_APIGW_URL,
        list: []
      };
    },
    computed: {
      ...mapGetters(['user']),
      tenantId () {
        return this.user.tenant_id;
      }
    },
    watch: {
      value: {
        handler (payload = []) {
          const isExistName = [...payload].find(e => e.username);
          this.list = [...payload];
          if (isExistName) {
            this.list = [...payload].map(e => e.username);
          }
        },
        immediate: true
      }
    },
    mounted () {
      document.body.addEventListener('click', this.handleTriggerClick);
      document.body.addEventListener('keydown', this.handleEnter);
      this.$once('hook:beforeDestroy', () => {
        document.body.removeEventListener('click', this.handleTriggerClick);
        document.body.removeEventListener('keydown', this.handleEnter);
      });
    },
    methods: {
      handleTriggerClick (event) {
        if (this.$refs.iamUserSelectorRef && this.$refs.iamUserSelectorRef.$el.contains(event.target)) {
          console.log('聚焦了');
          this.$emit('focus');
          return;
        }
        console.log('失焦了');
        this.$emit('blur');
      },

      handleEnter (event) {
        this.$emit('keydown', event);
      },
      
      handleChange (payload) {
        this.$emit('change', payload);
      },

      handleSetAutoFocus () {
        this.$refs.iamUserSelectorRef && this.$refs.iamUserSelectorRef.$el.querySelector('input').focus();
      }
    }
  };
</script>

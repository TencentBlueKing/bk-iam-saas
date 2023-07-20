<template>
  <div class="exception-box">
    <ExceptionEmpty
      :type="emptyData.type"
      scene="page"
      :empty-text="emptyData.text"
      :tip-text="emptyData.tip"
      :tip-type="emptyData.tipType"
      :error-message="emptyData.message"
    />
  </div>
</template>

<script>
  import { formatCodeData, delLocationHref } from '@/common/util';
  /**
   * 403 component
   */
  export default {
    data () {
      return {
        emptyData: {
          type: '403',
          text: '',
          tip: '',
          tipType: 'noPerm'
        }
      };
    },
    mounted () {
      const { message } = this.$route.query;
      if (message) {
        window.sessionStorage.setItem('errorMessage', message);
      }
      const params = {
        ...this.emptyData,
        ...{
          message: message || window.sessionStorage.getItem('errorMessage') || ''
        }
      };
      this.emptyData = formatCodeData(1302403, params);
      delLocationHref(['message']);
    }
  };
</script>

<style lang="postcss" scoped>
    .exception-box {
        text-align: center;
        margin: auto;
        img {
            width: 300px;
            margin-top: 150px;
        }
    }
</style>

<template>
  <div class="exception-box">
    <img src="https://magicbox.bk.tencent.com/static_api/v3/components/exception_building/images/building.png" alt="">
    <p>{{ $t(`m.common['没找到页面']`) }}</p>
  </div>
</template>

<script>
    /**
     * 404 component
     */
  export default {
    data () {
      return {};
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

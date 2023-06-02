<template functional>
  <div class="or-status-bar">
    <p class="bar">or</p>
  </div>
</template>
<style lang="postcss" scoped>
    /* .or-status-bar {
        position: relative;
        margin: 10px 0 20px 0;
        height: 15px;
        border-bottom: 1px dashed #dcdee5;
        .bar {
            position: absolute;
            top: 5px;
            left: 50%;
            transform: translate(-50%, 0);
            width: 30px;
            height: 15px;
            line-height: 14px;
            border-radius: 8px;
            background: #dcdee5;
            color: #fff;
            text-align: center
        }
    } */
    .or-status-bar {
        border-top: 1px dashed #dcdee5;
        height: 1px;
        clear: both;
        display: block;
        overflow: hidden;
        margin: 16px 0;
        .bar {
            padding-top: 7px;
            height: 15px;
            width: 30px;
            background-color: #dcdee5;
            color: #fff;
            position: absolute;
            text-align: center;
            border-radius: 8px;
            line-height: 0;
            margin-top: -8px;
            left: 50%;
            transform: translateX(-50%);
        }
    }
</style>

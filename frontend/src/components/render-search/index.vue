<template functional>
    <div class="iam-serach-wrapper">
        <div class="left">
            <slot />
        </div>
        <div class="right">
            <slot name="right" />
        </div>
    </div>
</template>
<style lang="postcss" scoped>
    .iam-serach-wrapper {
        position: relative;
        display: flex;
        justify-content: space-between;
        /* .left {
            display: flex;
            align-items: center;
        } */
    }
</style>

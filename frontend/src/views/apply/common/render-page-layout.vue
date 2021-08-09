<template functional>
    <div class="page-layout">
        <div class="left-layout">
            <slot />
        </div>
        <div class="right-layout">
            <slot name="right" />
        </div>
    </div>
</template>
<script>
    /**
     * render-page-layout
     *
     * @return component
     */
    export default {
        name: '',
        data () {
            return {}
        }
    }
</script>
<style lang="postcss" scoped>
    .page-layout {
        display: flex;
        padding: 0;
        .left-layout {
            flex: 0 0 280px;
            height: calc(100vh - 61px);
            background: #fff;
            overflow: hidden;
        }
        .right-layout {
            padding: 30px;
            flex: 1 0 auto;
            width: calc(100% - 280px);
            height: calc(100vh - 61px);
            background: #f5f6fa;
            overflow-y: auto;
            &::-webkit-scrollbar {
                width: 4px;
                background-color: lighten(transparent, 80%);
            }
            &::-webkit-scrollbar-thumb {
                height: 5px;
                border-radius: 2px;
                background-color: #e6e9ea;
            }
        }
    }
</style>

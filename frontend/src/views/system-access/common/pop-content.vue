<template>
    <div>
        <h1>{{title}}</h1>
        <div class="pb20">
            {{desc}}
        </div>
        <img class="img-cls" :src="image" alt="sync">
    </div>
</template>
<script>
    import operationGroup from '@/images/operation-group.png'
    export default {
        name: 'PopContent',
        props: {
            title: {
                type: String,
                default: '什么是操作分组'
            },
            desc: {
                type: String,
                default: '操作分组可以让用户在申请权限时更方便的找到想要的操作。'
            },
            image: {
                type: String,
                default: operationGroup
            }
        }
    }
</script>
<style lang="postcss" scoped>
    .img-cls{
        width: 100%;
    }
</style>

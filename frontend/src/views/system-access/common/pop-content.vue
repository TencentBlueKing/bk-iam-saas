<template>
  <div>
    <h1>{{title}}</h1>
    <div :class="isImage ? 'pb20' : ''">
      {{desc}}
    </div>
    <img v-if="isImage" class="img-cls" :src="image" alt="sync">
    <div v-else>
      <div v-for="item in image" :key="item.name">
        <h3>{{item.name}}</h3>
        <img class="img-cls" :src="item.imageSrc" alt="sync">
      </div>
    </div>
  </div>
</template>
<script>
  import operationGroup from '@/images/operation-group.png';
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
        type: [String, Array],
        default: operationGroup
      }
    },
    computed: {
      isImage () {
        return typeof this.image === 'string';
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .img-cls{
        width: 100%;
    }
</style>

<template functional>
  <div :class="['vertical-item', props.extCls || '']">
    <div class="label" :class="props.required ? 'is-required' : ''">
      {{ props.label ? `${props.label}` : '' }}
      <template v-if="props.subTitle">
        <span class="sub-title">({{ props.subTitle }})</span>
      </template>
    </div>
    <div class="content">
      <slot />
    </div>
  </div>
</template>
<style lang="postcss" scoped>
    .vertical-item {
        background: #fff;
    }
    .label {
        position: relative;
        font-size: 12px;
        color: #63656E;
        &.is-required:after {
            height: 8px;
            line-height: 1;
            content: "*";
            color: #ea3636;
            font-size: 12px;
            font-weight: normal;
            position: absolute;
            display: inline-block;
            vertical-align: middle;
            top: 50%;
            transform: translate(3px,-50%);
        }
        .sub-title {
            color: #979ba5;
            font-weight: normal;
        }
    }
</style>

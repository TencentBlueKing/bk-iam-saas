<template functional>
    <div :class="['horizontal-item', props.extCls || '']">
        <div class="label" :class="props.required ? 'is-required' : ''">
            {{ props.label ? `${props.label}` : ''}}
        </div>
        <div class="content">
            <slot />
            <slot name="append" />
        </div>
    </div>
</template>
<style lang="postcss" scoped>
    .horizontal-item {
        position: relative;
        padding: 30px;
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .1);
        background: #fff;
        .label {
            position: relative;
            width: 120px;
            line-height: 20px;
            font-weight: bold;
            font-size: 14px;
            color: #63656E;
            text-align: left;
            &.is-required:after {
                height: 8px;
                line-height: 1;
                content: "*";
                color: #ea3636;
                font-size: 12px;
                font-weight: normal;
                position: relative;
                display: inline-block;
                vertical-align: middle;
                top: -4px;
            }
        }
        .content {
            flex: 1;
            max-width: calc(100% - 134px);
        }
    }
</style>

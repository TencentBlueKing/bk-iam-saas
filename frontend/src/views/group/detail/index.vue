<template>
    <div class="iam-user-group-detail-wrapper">
        <div style="padding-top: 36px;"
            :style="{ minHeight: componentWrapperHeight + 'px' }">
            <component
                :is="componentName"
                :id="id"
                @on-init="handleComInit">
            </component>
        </div>
    </div>
</template>
<script>
    import store from '@/store';
    import { bus } from '@/common/bus';

    const GroupDetail = () => import(
        /* webpackChunkName: 'user-group' */'./group-detail'
    );

    const GroupPerm = () => import(
        /* webpackChunkName: 'user-group' */'./group-perm-new'
    );

    export default {
        name: '',
        components: {
            GroupPerm,
            GroupDetail
        },
        data () {
            return {
                componentWrapperHeight: 0,
                componentName: 'GroupDetail',
                leftOffset: 260,
                id: '',
                comIsLoading: true
            };
        },
        beforeRouteEnter (to, from, next) {
            store.commit('setHeaderTitle', '');
            next();
        },
        created () {
            this.id = Number(this.$route.params.id);
            this.$once('hook:beforeDestroy', () => {
                bus.$off('on-tab-change');
            });
        },
        mounted () {
            this.componentWrapperHeight = window.innerHeight - 108 - 2;
            const query = this.$route.query;
            const tab = (query.tab || '').toLowerCase();
            this.componentName = (tab === 'group_perm' || tab === 'GroupPerm') ? 'GroupPerm' : 'GroupDetail';
            bus.$on('on-tab-change', async (name) => {
                this.comIsLoading = true;
                this.componentName = name;
            });
        },
        methods: {
            /**
             * 切换父组件的 loading 状态回调函数
             *
             * @param {boolean} isLoading loading 状态
             */
            handleComInit (isLoading) {
                this.comIsLoading = isLoading;
            }
        }
    };
</script>

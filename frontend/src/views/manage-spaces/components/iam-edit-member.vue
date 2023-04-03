<template>
    <div class="iam-edit-selector" :style="styles">
        <template v-if="!isEditable">
            <div class="edit-wrapper">
                <div class="edit-content">
                    <slot>
                        <span
                            v-for="(item, index) in displayValue"
                            :key="index"
                            class="member-item"
                            :class="item.readonly ? 'member-readonly' : ''">
                            {{ item.username }}
                            <Icon v-if="!item.readonly && isEditMode" type="close-small"
                                @click.stop="handleDelete(index)" />
                        </span>
                    </slot>
                </div>
                <div class="edit-action-box" v-if="isEditMode">
                    <Icon
                        type="edit-fill"
                        class="edit-action"
                        v-if="!isLoading"
                        @click.self.stop="handleEdit" />
                    <Icon
                        type="loading-circle"
                        class="edit-loading"
                        v-if="isLoading" />
                </div>
            </div>
        </template>
        <template v-else>
            <bk-user-selector
                v-model="editValue"
                :ext-cls="[
                    'user-selector'
                ]"
                ref="input"
                :api="userApi"
                :placeholder="$t(`m.verify['请输入']`)"
                @blur="handleRtxBlur"
                @change="handleChange">
            </bk-user-selector>
        </template>
    </div>
</template>
<script>
    import BkUserSelector from '@blueking/user-selector';
    export default {
        name: 'iam-edit-selector',
        components: {
            BkUserSelector
        },
        props: {
            field: {
                type: String,
                required: true
            },
            value: {
                type: Array,
                default: () => []
            },
            width: {
                type: String,
                default: 'auto'
            },
            remoteHandler: {
                type: Function,
                default: () => Promise.resolve()
            },
            rules: {
                type: Array,
                default: () => []
            },
            mode: {
                type: String,
                default: 'edit',
                validator: function (value) {
                    return ['detail', 'edit'].includes(value);
                }
            }
        },
        data () {
            return {
                displayValue: this.value,
                isEditable: false,
                isLoading: false,
                userApi: window.BK_USER_API,
                newPayload: '',
                disabledValue: [],
                editValue: []
            };
        },
        computed: {
            styles () {
                return {
                    width: this.width
                };
            },
            isEditMode () {
                return this.mode === 'edit';
            }
        },
        watch: {
            value (newVal) {
                this.disabledValue = [...newVal].filter(e => e.readonly);
                this.displayValue = [...newVal];
                // this.editValue = [...newVal].filter(e => !e.readonly).map(e => e.username);
                this.editValue = [...newVal].map(e => e.username);
            }
        },
        mounted () {
            document.body.addEventListener('click', this.hideEdit);
            this.$once('hook:beforeDestroy', () => {
                document.body.removeEventListener('click', this.hideEdit);
            });
        },
        async created () {
            await this.fetchUser();
        },
        methods: {
            async fetchUser () {
                try {
                    this.userInfo = await this.$store.dispatch('userInfo');
                } catch (e) {
                    console.error(e);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                }
            },

            handleEdit () {
                document.body.click();
                this.isEditable = true;
                this.$nextTick(() => {
                    this.$refs.input.focus();
                    const disabledValue = [...this.disabledValue].map(item => item.username);
                    const selectedTag = this.$refs.input.$refs.selected;
                    if (selectedTag && selectedTag.length) {
                        selectedTag.forEach(item => {
                            if (disabledValue.includes(item.innerText)) {
                                item.className = 'user-selector-selected user-selector-selected-readonly';
                            }
                        });
                    }
                });
            },

            handleDelete (index) {
                this.displayValue.splice(index, 1);
                this.$emit('on-change', {
                    [this.field]: this.displayValue
                });
            },

            handleEnter (value, event) {
                if (!this.isEditable) return;
                if (event.key === 'Enter' && event.keyCode === 13) {
                    this.triggerChange();
                }
            },

            hideEdit (event) {
                if (this.displayValue.length < 1) {
                    return;
                }
                if (event.path && event.path.length > 0) {
                    for (let i = 0; i < event.path.length; i++) {
                        const target = event.path[i];
                        if (target.className && target.className === 'iam-edit-selector') {
                            return;
                        }
                    }
                }
                this.isEditable = false;
            },

            triggerChange () {
                this.isEditable = false;
                if (JSON.stringify(this.displayValue) !== JSON.stringify(this.value)) {
                    this.isLoading = true;
                    this.remoteHandler({
                        [this.field]: this.displayValue
                    }).then(() => {
                        this.$emit('on-change', {
                            [this.field]: this.displayValue
                        });
                    }).finally(() => {
                        this.isLoading = false;
                    });
                }
            },

            handleChange () {
                const editValue = this.editValue.reduce((p, v) => {
                    p.push({
                        username: v,
                        readonly: false
                    });
                    return p;
                }, []);
                this.displayValue = [...this.disabledValue, ...editValue];
            },

            handleRtxBlur () {
                if (JSON.stringify(this.displayValue) !== JSON.stringify(this.value)) {
                    this.$emit('on-change', {
                        [this.field]: this.displayValue
                    });
                }
            }
        }
    };
</script>
<style lang="postcss">
    @keyframes textarea-edit-loading {
        to {
            transform: rotateZ(360deg)
        }
    }
</style>
<style lang='postcss' scoped>
   .iam-edit-selector {
        position: relative;
        .edit-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            &:hover {
                .edit-action {
                    display: block;
                }
            }
        }

        .edit-content {
            flex: 0 0 auto;
            max-width: calc(100% - 25px);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            .member-item {
                display: inline-block;
                padding: 0 10px;
                margin: 2px 0 2px 6px;
                line-height: 22px;
                border-radius: 2px;
                background: #f0f1f5;
                font-size: 12px;
                i {
                    font-size: 18px;
                    color: #979ba5;
                    cursor: pointer;
                    &.disabled {
                        color: #c4c6cc;
                        cursor: not-allowed;
                    }
                }
            }
            .member-readonly{
                background: #FFF1DB;
                color: #FE9C00;
            }
        }
        .edit-action-box {
            display: flex;
            align-items: center;
            margin-right: auto;
            font-size: 16px;
            .edit-action {
                padding: 6px 15px 6px 2px;
                cursor: pointer;
                display: none;
                &:hover {
                    color: #3a84ff;
                }
            }
            .edit-loading {
                position: absolute;
                top: 8px;
                margin-left: 2px;
                animation: 'textarea-edit-loading' 1s linear infinite;
            }
        }
        .user-selector {
            width: 100%;
        }
        /deep/ .user-selector-selected-readonly {
            background: #FFF1DB;
            .user-selector-selected-value {
                color: #FE9C00;
            }
            .user-selector-selected-clear {
                display: none;
            }
        }
    }
</style>

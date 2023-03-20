<template>
    <div class="iam-space-basic-info-wrapper">
        <bk-form :model="formData" form-type="vertical" ref="basicInfoForm">
            <iam-form-item :label="$t(`m.levelSpace['空间名称']`)" required>
                <bk-input :value="formData.name" style="width: 450px;" clearable
                    :placeholder="$t(`m.levelSpace['请输入空间名称']`)" :ext-cls="isShowNameError ? 'group-name-error' : ''"
                    data-test-id="space_input_name" @input="handleNameInput" @blur="handleNameBlur"
                    @change="handleNameChange" />
                <p class="name-empty-error" v-if="isShowNameError">{{ nameValidateText }}</p>
            </iam-form-item>
            <iam-form-item :label="$t(`m.levelSpace['空间管理员']`)" required>
                <div class="select-wrap">
                    <bk-user-selector
                        :value="displayMembers"
                        :api="userApi"
                        :placeholder="$t(`m.verify['请输入']`)"
                        :style="{ width: language === 'zh-cn' ? '75%' : '60%' }"
                        :class="isShowMemberError ? 'is-member-empty-cls' : ''"
                        data-test-id="space_userSelector_member" @focus="handleRtxFocus" @blur="handleRtxBlur"
                        @change="handleRtxChange">
                    </bk-user-selector>
                  
                    <bk-checkbox
                        :true-value="true"
                        :false-value="false"
                        class="select-wrap-checkbox"
                        v-model="formData.sync_perm"
                        @change="handleCheckboxChange">
                        {{ $t(`m.grading['同时具备空间下操作和资源权限']`) }}
                    </bk-checkbox>
                </div>
                <p class="name-empty-error" v-if="isShowMemberError">{{ $t(`m.verify['请选择空间管理员']`) }}</p>
            </iam-form-item>
            <iam-form-item :label="$t(`m.common['描述']`)">
                <bk-input type="textarea" maxlength="255" :value="formData.description"
                    :placeholder="$t(`m.verify['请输入']`)" data-test-id="space_input_desc" @change="handleDescChange" />
            </iam-form-item>
        </bk-form>
    </div>
</template>
<script>
    import { language } from '@/language';
    import BkUserSelector from '@blueking/user-selector';
    const getDefaultData = () => ({
        name: '',
        description: '',
        members: [],
        sync_perm: false
    });

    export default {
        name: '',
        components: {
            BkUserSelector
        },
        props: {
            data: {
                type: Object,
                default () {
                    return {};
                }
            }
        },
        data () {
            return {
                language,
                formData: getDefaultData(),
                isShowNameError: false,
                isShowMemberError: false,
                nameValidateText: '',
                userApi: window.BK_USER_API,
                displayMembers: []
            };
        },
        watch: {
            data: {
                handler (value) {
                    if (Object.keys(value).length) {
                        const { name, description, sync_perm } = value;
                        this.displayMembers = value.members.filter(e => !e.readonly).map(e => e.username);
                        const members = value.members.filter(e => !e.readonly).map(e => e.username);
                        this.formData = Object.assign({}, {
                            name,
                            description,
                            members,
                            sync_perm
                        });
                    }
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            handleRtxFocus () {
                this.isShowMemberError = false;
            },

            handleRtxBlur () {
                this.isShowMemberError = this.displayMembers.length < 1;
            },

            handleNameInput (payload) {
                this.isShowNameError = false;
                this.nameValidateText = '';
            },

            handleNameBlur (payload) {
                const maxLength = 32;
                if (payload === '') {
                    this.nameValidateText = this.$t(`m.verify['空间名称必填']`);
                    this.isShowNameError = true;
                }
                if (!this.isShowNameError) {
                    if (payload.trim().length > maxLength) {
                        this.nameValidateText = this.$t(`m.verify['空间名称最长不超过32个字符']`);
                        this.isShowNameError = true;
                    }
                    if (!/^[^\s]*$/g.test(payload)) {
                        this.nameValidateText = this.$t(`m.verify['一级管理空间名称不允许空格']`);
                        this.isShowNameError = true;
                    }
                }
            },

            handleRtxChange (payload) {
                this.isShowMemberError = false;
                payload = payload.reduce((p, v) => {
                    p.push({
                        username: v,
                        readonly: false
                    });
                    return p;
                }, []);
                this.$emit('on-change', 'members', payload);
            },

            handleNameChange (value) {
                this.formData.name = value;
                this.$emit('on-change', 'name', value);
            },

            handleDescChange (value) {
                this.formData.description = value;
                this.$emit('on-change', 'description', value);
            },

            submit () {
                return this.$refs.basicInfoForm.validate().then(validator => {
                    return Promise.resolve(this.formData);
                }, validator => {
                    return Promise.reject(validator.content);
                });
            },

            handleValidator () {
                const maxLength = 32;
                const { name, members } = this.formData;
                if (name === '') {
                    this.nameValidateText = this.$t(`m.verify['空间名称必填']`);
                    this.isShowNameError = true;
                }
                if (!this.isShowNameError) {
                    if (name.trim().length > maxLength) {
                        this.nameValidateText = this.$t(`m.verify['空间名称最长不超过32个字符']`);
                        this.isShowNameError = true;
                    }
                    if (!/^[^\s]*$/g.test(name)) {
                        this.nameValidateText = this.$t(`m.verify['一级管理空间名称不允许空格']`);
                        this.isShowNameError = true;
                    }
                }
                this.isShowMemberError = members.length < 1;

                return this.isShowNameError || this.isShowMemberError;
            },

            reset () {
                this.$refs.basicInfoForm.formItems.forEach(item => {
                    item.validator.content = '';
                    item.validator.state = '';
                });
            },

            handleCheckboxChange () {
                this.$emit('on-change', 'sync_perm', this.formData.sync_perm);
            }
        }
    };
</script>
<style lang="postcss">
.iam-space-basic-info-wrapper {
    position: relative;
    top: -6px;

    .group-name-error {
        .bk-form-input {
            border-color: #ff5656;
        }
    }

    .name-empty-error {
        font-size: 12px;
        color: #ff4d4d;
    }

    .select-wrap {
        display: flex;
        align-items: center;
        &-checkbox {
            display: flex;
            margin-left: 20px;
        }
    }

    .is-member-empty-cls {
        .user-selector-container {
            border-color: #ff4d4d;
        }
    }
}
</style>

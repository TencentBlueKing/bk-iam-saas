<template>
    <!-- eslint-disable max-len -->
    <div class="resource-instance-table-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <bk-table
            v-if="!isLoading"
            :data="tableList"
            border
            :row-class-name="handleRowClass"
            :cell-class-name="getCellClass"
            :empty-text="$t(`m.verify['请选择操作']`)">
            <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" min-width="120">
                <template slot-scope="{ row }">
                    <div v-if="!!row.isAggregate" style="padding: 10px 0;">
                        <span class="action-name" :title="row.name">{{ row.name }}</span>
                    </div>
                    <div v-else>
                        <span class="action-name" :title="row.name">{{ row.name }}</span>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" min-width="420">
                <template slot-scope="{ row, $index }">
                    <!-- isAggregate代表批量编辑状态 -->
                    <div class="relation-content-wrapper" v-if="!!row.isAggregate">
                        <label class="resource-type-name" v-if="row.aggregateResourceType.length === 1">{{ row.aggregateResourceType[0].name }}</label>
                        <div class="bk-button-group tab-button" v-else>
                            <bk-button v-for="(item, index) in row.aggregateResourceType"
                                :key="item.id" @click="selectResourceType(row, index)"
                                :class="row.selectedIndex === index ? 'is-selected' : ''" size="small">{{item.name}}
                                <span v-if="row.instancesDisplayData[item.id]">
                                    ({{row.instancesDisplayData[item.id].length}})</span>
                            </bk-button>
                        </div>
                        <div class="group-container">
                            <render-condition
                                :ref="`condition_${$index}_aggregateRef`"
                                :value="row.value"
                                :is-empty="row.empty"
                                :can-view="false"
                                :can-paste="row.canPaste"
                                :is-error="row.isError"
                                @on-mouseover="handlerAggregateConditionMouseover(row)"
                                @on-mouseleave="handlerAggregateConditionMouseleave(row)"
                                @on-copy="handlerAggregateOnCopy(row, $index)"
                                @on-paste="handlerAggregateOnPaste(row)"
                                @on-batch-paste="handlerAggregateOnBatchPaste(row, $index)"
                                @on-click="showAggregateResourceInstance(row, $index)" />
                        </div>
                    </div>
                    <div class="relation-content-wrapper" :class="tableList.length >= 1 ? 'pr40' : ''" v-else>
                        <template v-if="!row.isEmpty">
                            <div v-for="(_, groIndex) in row.resource_groups" :key="_.id" class="group-container">
                                <div class="relation-content-item" v-for="(content, contentIndex) in _.related_resource_types" :key="contentIndex">
                                    <div class="content-name">
                                        {{ content.name }}
                                        <template v-if="row.isShowRelatedText && _.id">
                                            <div style="display: inline-block; color: #979ba5;">
                                                ({{ $t(`m.info['已帮您自动勾选依赖操作需要的实例']`) }})
                                            </div>
                                        </template>
                                    </div>
                                    <div class="content">
                                        <render-condition
                                            :ref="`condition_${$index}_${contentIndex}_ref`"
                                            :value="content.value"
                                            :is-empty="content.empty"
                                            :can-view="row.canView && !!_.id"
                                            :params="curCopyParams"
                                            :can-paste="content.canPaste"
                                            :is-error="content.isLimitExceeded || content.isError"
                                            @on-mouseover="handlerConditionMouseover(content)"
                                            @on-mouseleave="handlerConditionMouseleave(content)"
                                            @on-view="handlerOnView(row, content, contentIndex, groIndex)"
                                            @on-copy="handlerOnCopy(content, $index, contentIndex, row)"
                                            @on-paste="handlerOnPaste(...arguments, row, content)"
                                            @on-batch-paste="handlerOnBatchPaste(...arguments, content, $index, contentIndex)"
                                            @on-click="showResourceInstance(row, content, contentIndex, groIndex)" />
                                    </div>
                                    <p v-if="content.isLimitExceeded" class="is-limit-error">{{ $t(`m.info['实例数量限制提示']`) }}</p>
                                    <Icon v-if="_.related_resource_types.length > 1 || !!row.related_environments.length" class="add-icon" type="add-hollow" @click="handlerAddCondition(_, $index, contentIndex, groIndex)" />
                                    <Icon v-if="_.related_resource_types.length > 1 || !!row.related_environments.length" :class="row.resource_groups.length <= 1 || !!_.id ? 'disabled' : ''" type="reduce-hollow" class="reduce-icon"
                                        @click="handlerReduceCondition(_, $index, contentIndex, groIndex)" />
                                    <Icon v-if="_.related_resource_types.length > 1 && groIndex === 0" type="help-fill-2" class="help-icon" v-bk-tooltips="tipsContent" />
                                </div>
                                <div v-if="row.resource_groups.length > 1 && groIndex !== row.resource_groups.length - 1" class="group-line"
                                    :class="_.related_resource_types.length > 1 ? 'group-line-more' : ''"></div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="condition-table-cell empty-text">{{ $t(`m.common['无需关联实例']`) }}</div>
                        </template>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" :label="$t(`m.common['生效条件']`)" min-width="300">
                <template slot-scope="{ row, $index }">
                    <template v-if="!!row.isAggregate">
                        <div class="condition-table-cell empty-text">{{ $t(`m.common['无生效条件']`) }}</div>
                    </template>
                    <template v-else>
                        <template v-if="!!row.resource_groups.length">
                            <div class="condition-table-cell" v-if="!!row.related_environments.length"
                                :class="row.resource_groups.length === 1 ? 'empty-text' : ''">
                                <div v-for="(_, groIndex) in row.resource_groups" :key="_.id"
                                    :class="row.resource_groups.length > 1 ? 'environ-group-more' : 'environ-group-one'">
                                    <effect-time
                                        :value="_.environments"
                                        :is-empty="!_.environments.length"
                                        @on-click="showTimeSlider(row, $index, groIndex)">
                                    </effect-time>

                                    <div v-if="row.resource_groups.length > 1 && groIndex !== row.resource_groups.length - 1"
                                        class="condition-line" :class="_.related_resource_types.length > 1 ? 'condition-line-more' : ''"></div>
                                </div>
                            </div>
                            <div v-else class="condition-table-cell empty-text">{{ $t(`m.common['无生效条件']`) }}</div>
                        </template>
                        <template v-else>
                            <div class="condition-table-cell empty-text">{{ $t(`m.common['无生效条件']`) }}</div>
                        </template>
                    </template>
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" prop="description" :label="$t(`m.common['申请期限']`)" min-width="150">
                <template slot-scope="{ row, $index }">
                    <!-- {{row.inOriginalList}}--++--{{row.isNew}}--{{row.expired_display}}--{{row.isExpired}}--{{row.tag}} -->
                    <!-- inOriginalList:{{row.inOriginalList}}--
                    isNew:{{row.isNew}}--
                    isChanged:{{row.isChanged}}--
                    isExpired:{{row.isExpired}}--{{row.tag}}--{{row.expired_display}} -->
                    <!-- tag add 不需要比较过期时间，直接不禁用下拉框 -->
                    <!-- tag update 需要比较过期时间，过期时，显示续期，点击续期然后操作下拉框；不过期时，下拉框禁用 -->
                    <template v-if="row.isShowRenewal">
                        <!-- 11 -->
                        <div class="renewal-action-warp">
                            <bk-button theme="primary" class="renewal-action" outline @click="handleOpenRenewal(row, $index)">
                                {{ $t(`m.renewal['续期']`) }}
                            </bk-button>
                        </div>
                    </template>
                    <template v-else>
                        <!-- 22 -->
                        <template v-if="!row.isNew && !row.isExpired">
                            <!-- 33 -->
                            <div class="mock-disabled-select">{{row.expired_display}}</div>
                        </template>
                        <template v-else>
                            <!-- 44 -->
                            <template v-if="row.isShowRelatedText && row.inOriginalList && !cacheId && !row.isNew">
                                <!-- 55{{!cacheId}} -->
                                <div class="mock-disabled-select">{{row.expired_display}}</div>
                            </template>
                            <template v-else>
                                <!-- 66{{!cacheId}} -->
                                <bk-select
                                    v-model="row.expired_at"
                                    :clearable="false"
                                    :ref="`${row.id}&expiredAtRef`"
                                    :placeholder="row.expiredAtPlaceholder"
                                    ext-cls="iam-deadline-select"
                                    ext-popover-cls="iam-deadline-select-dropdown-content"
                                    @toggle="handleExpiredToggle(...arguments, row)"
                                    @selected="handleExpiredSelect(...arguments, row)">
                                    <bk-option v-for="option in durationList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                    <div slot="extension" style="cursor: pointer;" @click.stop="handleOpenCustom(row)">
                                        <template v-if="!row.isShowCustom">
                                            {{ $t(`m.common['自定义']`) }}
                                        </template>
                                        <template v-else>
                                            <bk-input
                                                v-model="row.customValue"
                                                size="small"
                                                :placeholder="$t(`m.common['临时期限选择提示']`)"
                                                maxlength="3"
                                                ext-cls="iam-perm-apply-expired-input-cls"
                                                @blur="handleBlur(...arguments, row)"
                                                @input="handleInput(...arguments, row)"
                                                @enter="handleEnter(...arguments, row)">
                                                <template slot="append">
                                                    <div class="group-text">{{ $t(`m.common['小时']`) }}</div>
                                                </template>
                                            </bk-input>
                                        </template>
                                    </div>
                                </bk-select>
                                <bk-button
                                    class="cancel-renewal-action"
                                    outline
                                    v-if="!row.isNew && !row.isShowRenewal"
                                    @click="handleCancelRenewal(row)">
                                    {{ $t(`m.permApply['取消续期']`) }}
                                </bk-button>
                            </template>
                        </template>
                    </template>
                </template>
            </bk-table-column>
            <template slot="empty">
                <ExceptionEmpty />
            </template>
        </bk-table>

        <bk-sideslider
            :is-show="isShowResourceInstanceSideslider"
            :title="resourceInstanceSidesliderTitle"
            :width="720"
            quick-close
            transfer
            :ext-cls="'relate-instance-sideslider'"
            @update:isShow="handleResourceCancel">
            <div slot="content" class="sideslider-content">
                <render-resource
                    ref="renderResourceRef"
                    :data="condition"
                    :original-data="originalCondition"
                    :flag="curFlag"
                    :selection-mode="curSelectionMode"
                    :disabled="curDisabled"
                    :params="params"
                    @on-limit-change="handleLimitChange"
                    @on-init="handleOnInit" />
            </div>
            <div slot="footer" style="margin-left: 25px;">
                <bk-button theme="primary" :loading="sliderLoading" :disabled="disabled" @click="handleResourceSumit">{{ $t(`m.common['保存']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourcePreview" v-if="isShowPreview">{{ $t(`m.common['预览']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel">{{ $t(`m.common['取消']`) }}</bk-button>
            </div>
        </bk-sideslider>

        <bk-sideslider :is-show="isShowResourceInstanceEffectTime"
            :title="resourceInstanceEffectTimeTitle"
            :width="720"
            quick-close
            @update:isShow="handleResourceEffectTimeCancel"
            :ext-cls="'relate-instance-sideslider'">
            <div slot="content" class="sideslider-content">
                <sideslider-effect-time
                    ref="sidesliderRef"
                    :data="environmentsData"
                ></sideslider-effect-time>
            </div>
            <div slot="footer" style="margin-left: 25px;">
                <bk-button theme="primary" :loading="sliderLoading" @click="handleResourceEffectTimeSumit">{{ $t(`m.common['保存']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" @click="handleResourceEffectTimeCancel">{{ $t(`m.common['取消']`) }}</bk-button>
            </div>
        </bk-sideslider>

        <preview-resource-dialog
            :show="isShowPreviewDialog"
            :title="previewDialogTitle"
            :params="previewResourceParams"
            @on-after-leave="handlePreviewDialogClose" />

        <render-aggregate-sideslider
            :show.sync="isShowAggregateSideslider"
            :params="aggregateResourceParams"
            :value="aggregateValue"
            @on-selected="handlerSelectAggregateRes" />
    </div>
</template>

<script>
    import _ from 'lodash';
    import { mapGetters } from 'vuex';
    import RenderAggregateSideslider from '@/components/choose-ip/sideslider';
    import Condition from '@/model/condition';
    import Policy from '@/model/policy';
    import { leaveConfirm } from '@/common/leave-confirm';
    import { PERMANENT_TIMESTAMP } from '@/common/constants';
    import RenderResource from './render-resource';
    import RenderCondition from './render-condition';
    import EffectTime from './effect-time';
    import SidesliderEffectTime from './sideslider-effect-time';
    import PreviewResourceDialog from './preview-resource-dialog';

    // 单次申请的最大实例数
    const RESOURCE_MAX_LEN = 20;

    // 6个月的时间戳
    const DEFAULT_TIMESTAMP = 15552000;

    export default {
        name: 'resource-instance-table',
        components: {
            RenderAggregateSideslider,
            RenderResource,
            RenderCondition,
            PreviewResourceDialog,
            EffectTime,
            SidesliderEffectTime
        },
        props: {
            list: {
                type: Array,
                default: () => []
            },
            originalList: {
                type: Array,
                default: () => []
            },
            systemId: {
                type: String,
                default: ''
            },
            cacheId: {
                type: String,
                default: ''
            },
            isAllExpanded: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                tableList: [],
                durationList: [
                    { id: 3600, name: this.$t(`m.common['1小时']`) },
                    { id: 10800, name: this.$t(`m.common['3小时']`) },
                    { id: 21600, name: this.$t(`m.common['6小时']`) },
                    { id: 43200, name: this.$t(`m.common['12小时']`) },
                    { id: 86400, name: this.$t(`m.common['24小时']`) }
                    // { id: 4102444800, name: this.$t(`m.common['永久']`) }
                ],
                isShowResourceInstanceSideslider: false,
                resourceInstanceSidesliderTitle: '',
                // 查询参数
                params: {},
                disabled: false,
                curIndex: -1,
                curResIndex: -1,
                curGroupIndex: -1,
                isShowPreviewDialog: false,
                previewDialogTitle: '',
                previewResourceParams: {},
                curCopyData: ['none'],
                curCopyType: '',

                curId: '',
                isLoading: false,

                isShowAggregateSideslider: false,

                aggregateResourceParams: {},
                aggregateIndex: -1,
                aggregateValue: [],
                // 当前复制的数据形态: normal: 普通; aggregate: 聚合后
                curCopyMode: 'normal',
                curAggregateResourceType: {},
                curCopyParams: {},
                sliderLoading: false,
                needEmitFlag: false,
                isShowResourceInstanceEffectTime: false,
                tipsContent: {
                    content: '<p>添加多组实例可以实现分批鉴权的需求</p><p>比如，root账号只能登陆主机1，user账号只能登陆主机2，root账号不能登陆主机2，user账号不能登陆主机1</p><p>这时可以添加两组实例，第一组实例为[root，主机1]，第二组实例为[user，主机2]来实现</p>',
                    html: '<p>添加多组实例可以实现分批鉴权的需求</p><p>比如，root账号只能登陆主机1，user账号只能登陆主机2，root账号不能登陆主机2，user账号不能登陆主机1</p><p>这时可以添加两组实例，第一组实例为[root，主机1]，第二组实例为[user，主机2]来实现</p>'
                },
                selectedIndex: 0,
                instanceKey: ''
            };
        },
        computed: {
            ...mapGetters(['user']),
            condition () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return [];
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex];
                if (!curData) {
                    return [];
                }
                if (curData.condition.length === 0) curData.condition = ['none'];
                return _.cloneDeep(curData.condition);
            },
            originalCondition () {
                if (this.curIndex === -1
                    || this.curResIndex === -1
                    || this.curGroupIndex === -1
                    || this.originalList.length < 1) {
                    return [];
                }
                const curId = this.tableList[this.curIndex].id;
                const curType = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex].type;
                if (!this.originalList.some(item => item.id === curId)) {
                    return [];
                }
                const curResTypeData = this.originalList.find(item => item.id === curId)
                    .resource_groups[this.curGroupIndex];
                if (!curResTypeData) return [];
                if (!curResTypeData.related_resource_types.some(item => item.type === curType)) {
                    return [];
                }
                const curData = curResTypeData.related_resource_types.find(item => item.type === curType);
                if (!curData) {
                    return [];
                }
                return _.cloneDeep(curData.condition);
            },
            environmentsData () {
                if (this.curIndex === -1 || this.curGroupIndex === -1) {
                    return [];
                }
                const environmentsData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .environments;

                if (!environmentsData) {
                    return [];
                }
                return _.cloneDeep(environmentsData);
            },
            curDisabled () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return false;
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex];
                return curData.isDefaultLimit;
            },
            curFlag () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return 'add';
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex];
                return curData.flag;
            },
            curSelectionMode () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return 'all';
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex];
                return curData.selectionMode;
            },
            isShowPreview () {
                if (this.curIndex === -1) {
                    return false;
                }
                return this.tableList[this.curIndex].policy_id !== '';
            }
        },
        watch: {
            list: {
                handler (value) {
                    value.forEach(e => {
                        e.expired_at = 3600;
                    });
                    if (this.isAllExpanded) {
                        this.tableList = value.filter(e =>
                            (e.resource_groups && e.resource_groups.length)
                            || e.isAggregate);
                        this.emptyResourceGroupsList = value.filter(e =>
                            e.resource_groups && !e.resource_groups.length);
                        this.emptyResourceGroupsName = (this.emptyResourceGroupsList || []).reduce((p, e) => {
                            p.push(e.name);
                            return p;
                        }, []);
                        if (this.emptyResourceGroupsName.length) {
                            this.emptyResourceGroupsList[0].name = this.emptyResourceGroupsName.join('，');
                            this.emptyResourceGroupsTableList = this.emptyResourceGroupsList[0];
                            this.tableList.unshift(this.emptyResourceGroupsTableList);
                        }
                    } else {
                        value.forEach(e => {
                            e.name = e.name.split('，')[0];
                        });
                        this.emptyResourceGroupsList = []; // 重置变量
                        this.tableList = value;
                    }
                    this.originalList = _.cloneDeep(this.tableList);
                },
                immediate: true
            },
            systemId: {
                handler (value) {
                    if (value !== '') {
                        this.curCopyType = '';
                        this.curCopyData = ['none'];
                        this.curIndex = -1;
                        this.curResIndex = -1;
                        this.curGroupIndex = -1;
                        this.aggregateResourceParams = {};
                        this.aggregateIndex = -1;
                        this.aggregateValue = [];
                        this.curCopyMode = 'normal';
                        this.curCopyParams = {};
                        this.curAggregateResourceType = {};
                        this.needEmitFlag = false;
                    }
                },
                immediate: true
            }
        },
        created () {
        },
        methods: {
            handleOpenRenewal (row, index) {
                row.isShowRenewal = false;
                row.customValueBackup = row.customValue;
                row.expired_at_backup = row.expired_at;
                row.expired_display_backup = row.expired_display;
                row.expired_at = DEFAULT_TIMESTAMP;
                row.expired_display = '';
                row.customValue = '';
                this.$set(this.tableList, index, row);
            },

            handleCancelRenewal (payload) {
                payload.isShowRenewal = true;
                payload.expired_at = payload.expired_at_backup;
                payload.expired_display = payload.expired_display_backup;
                payload.customValue = payload.customValueBackup;
                delete payload.expired_at_backup;
                delete payload.expired_display_backup;
                delete payload.customValueBackup;
            },

            handlerSelectAggregateRes (payload) {
                const instances = payload.map(item => {
                    return {
                        id: item.id,
                        name: item.display_name
                    };
                });
                this.tableList[this.aggregateIndex].isError = false;
                const instanceKey = this.tableList[this.aggregateIndex].aggregateResourceType[this.selectedIndex].id;
                const instancesDisplayData = _.cloneDeep(this.tableList[this.aggregateIndex].instancesDisplayData);
                this.tableList[this.aggregateIndex].instancesDisplayData = {
                    ...instancesDisplayData,
                    [instanceKey]: instances
                };
                this.tableList[this.aggregateIndex].instances = [];

                for (const key in this.tableList[this.aggregateIndex].instancesDisplayData) {
                    // eslint-disable-next-line max-len
                    this.tableList[this.aggregateIndex].instances.push(...this.tableList[this.aggregateIndex].instancesDisplayData[key]);
                }
                this.$emit('on-select', this.tableList[this.aggregateIndex]);
            },

            handlerAggregateConditionMouseover (payload) {
                if (this.curCopyData[0] === 'none') {
                    return;
                }
                if (this.curCopyKey === `${payload.aggregateResourceType.system_id}${payload.aggregateResourceType.id}`) {
                    payload.canPaste = true;
                }
            },

            handlerAggregateConditionMouseleave (payload) {
                payload.canPaste = false;
            },

            handlerAggregateOnCopy (payload, index) {
                this.instanceKey = payload.aggregateResourceType[payload.selectedIndex].id;
                this.curCopyKey = `${payload.aggregateResourceType.system_id}${payload.aggregateResourceType.id}`;
                this.curAggregateResourceType = payload.aggregateResourceType[payload.selectedIndex];
                this.curCopyData = _.cloneDeep(payload.instancesDisplayData[this.instanceKey]);
                this.curCopyMode = 'aggregate';
                this.showMessage(this.$t(`m.info['实例复制']`));
                this.$refs[`condition_${index}_aggregateRef`] && this.$refs[`condition_${index}_aggregateRef`].setImmediatelyShow(true);
            },

            handlerAggregateOnPaste (payload) {
                let tempInstances = [];
                if (this.curCopyMode === 'aggregate') {
                    tempInstances = this.curCopyData;
                } else {
                    if (this.curCopyData[0] !== 'none') {
                        const instances = this.curCopyData.map(item => item.instance);
                        const instanceData = instances[0][0];
                        tempInstances = instanceData.path.map(pathItem => {
                            return {
                                id: pathItem[0].id,
                                name: pathItem[0].name
                            };
                        });
                    }
                }
                if (tempInstances.length < 1) {
                    return;
                }
                payload.instances = _.cloneDeep(tempInstances);
                payload.isError = false;
                this.showMessage(this.$t(`m.info['粘贴成功']`));
            },

            handlerAggregateOnBatchPaste (payload, index) {
                let tempCurData = ['none'];
                let tempArrgegateData = [];
                if (this.curCopyMode === 'normal') {
                    if (this.curCopyData[0] !== 'none') {
                        tempCurData = this.curCopyData.map(item => {
                            delete item.id;
                            return item;
                        });
                        const instances = this.curCopyData.map(item => item.instance);
                        const instanceData = instances[0][0];
                        tempArrgegateData = instanceData.path.map(pathItem => {
                            return {
                                id: pathItem[0].id,
                                name: pathItem[0].name
                            };
                        });
                    }
                } else {
                    tempArrgegateData = this.curCopyData;
                    const instances = (() => {
                        const arr = [];
                        const { id, name, system_id } = this.curAggregateResourceType;
                        this.curCopyData && this.curCopyData.forEach(v => {
                            const curItem = arr.find(_ => _.type === id);
                            if (curItem) {
                                curItem.path.push([{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }]);
                            } else {
                                arr.push({
                                    name,
                                    type: id,
                                    path: [[{
                                        id: v.id,
                                        name: v.name,
                                        system_id,
                                        type: id,
                                        type_name: name
                                    }]]
                                });
                            }
                        });
                        return arr;
                    })();
                    if (instances.length > 0) {
                        tempCurData = [new Condition({ instances }, '', 'add')];
                    }
                }
                this.tableList.forEach(item => {
                    if (!item.isAggregate) {
                        item.resource_groups.forEach(groupItem => {
                            groupItem.related_resource_types && groupItem.related_resource_types.forEach(subItem => {
                                if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                                    subItem.condition = _.cloneDeep(tempCurData);
                                    subItem.isError = false;
                                }
                            });
                        });
                    } else {
                        item.aggregateResourceType.forEach(aggregateResourceItem => {
                            if (`${aggregateResourceItem.system_id}${aggregateResourceItem.id}` === this.curCopyKey) {
                                if (Object.keys(item.instancesDisplayData).length) {
                                    item.instancesDisplayData[this.instanceKey] = _.cloneDeep(tempArrgegateData);
                                    item.instances = this.setInstanceData(item.instancesDisplayData);
                                } else {
                                    item.instances = _.cloneDeep(tempArrgegateData);
                                    this.setInstancesDisplayData(item);
                                }
                            }
                        });
                        item.isError = false;
                    }
                });
                payload.isError = false;
                this.curCopyData = ['none'];
                this.$refs[`condition_${index}_aggregateRef`] && this.$refs[`condition_${index}_aggregateRef`].setImmediatelyShow(false);
                this.showMessage(this.$t(`m.info['批量粘贴成功']`));
            },

            // 设置instances
            setInstanceData (data) {
                return Object.keys(data).reduce((p, v) => {
                    p.push(...data[v]);
                    return p;
                }, []);
            },

            // 设置InstancesDisplayData
            setInstancesDisplayData (data) {
                data.instancesDisplayData = data.instances.reduce((p, v) => {
                    if (!p[this.instanceKey]) {
                        p[this.instanceKey] = [];
                    }
                    p[this.instanceKey].push({
                        id: v.id,
                        name: v.name
                    });
                    return p;
                }, {});
            },

            // 设置正常粘贴InstancesDisplayData
            setNomalInstancesDisplayData (data, key) {
                data.instancesDisplayData[key] = data.instances.map(e => ({
                    id: e.id,
                    name: e.name
                }));
            },

            showAggregateResourceInstance (data, index) {
                this.aggregateResourceParams = _.cloneDeep(data.aggregateResourceType[this.selectedIndex]);
                this.aggregateIndex = index;
                const instanceKey = data.aggregateResourceType[this.selectedIndex].id;
                this.instanceKey = instanceKey;
                if (!data.instancesDisplayData[instanceKey]) data.instancesDisplayData[instanceKey] = [];
                this.aggregateValue = _.cloneDeep(data.instancesDisplayData[instanceKey].map(item => {
                    return {
                        id: item.id,
                        display_name: item.name
                    };
                }));
                this.isShowAggregateSideslider = true;
            },

            showMessage (payload) {
                this.bkMessageInstance = this.$bkMessage({
                    limit: 1,
                    theme: 'success',
                    message: payload
                });
            },

            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 1 || columnIndex === 2) {
                    return 'iam-perm-table-cell-cls';
                }
                return '';
            },

            handleRowClass (payload) {
                const { row } = payload;
                if (row.isAggregate) {
                    return '';
                }
                if (row.tid !== '' && ['add', 'update'].includes(row.tag) && !this.$route.query.system_id && !this.$route.query.tid) {
                    return 'has-perm-row-cls';
                }
                if (row.isExistPermAnimation) {
                    return 'has-perm-row-animation-cls';
                }
                return '';
            },

            handleLinearData (payload, parentId = null) {
                payload.forEach(item => {
                    item.parent = parentId;
                    this.actionLinearTopologies.push(_.cloneDeep(item));
                    if (item.sub_actions && item.sub_actions.length > 0) {
                        this.handleLinearData(item.sub_actions, item.id);
                    }
                });
            },

            handleLimitChange () {
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex];
                curData.isChange = true;
            },

            handleOnInit (payload) {
                this.disabled = !payload;
            },

            handleOpenCustom (payload) {
                payload.isShowCustom = true;
            },

            showResourceInstance (data, resItem, resIndex, groupIndex) {
                this.params = {
                    system_id: this.systemId,
                    action_id: data.id,
                    resource_type_system: resItem.system_id,
                    resource_type_id: resItem.type
                };
                const index = this.tableList.findIndex(item => item.id === data.id);
                this.curIndex = index;
                this.curResIndex = resIndex;
                this.curGroupIndex = groupIndex;

                this.resourceInstanceSidesliderTitle = `${this.$t(`m.common['关联操作']`)}${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
                window.changeAlert = 'iamSidesider';
                this.isShowResourceInstanceSideslider = true;
            },

            async handleMainActionSubmit (payload, relatedActions) {
                let curPayload = _.cloneDeep(payload);
                this.sliderLoading = true;
                curPayload = curPayload.filter(e => {
                    if ((e.instance && e.instance.length > 0) || (e.attribute && e.attribute.length > 0)) {
                        e.instances = e.instance || [];
                        e.attributes = e.attribute || [];
                        delete e.instance;
                        delete e.attribute;
                        return true;
                    }
                    return false;
                }

                );
                const curData = _.cloneDeep(this.tableList[this.curIndex]);
                // eslint-disable-next-line max-len
                curData.resource_groups[this.curGroupIndex].related_resource_types = [curData.resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]];
                curData.resource_groups[this.curGroupIndex].related_resource_types[0].condition = curPayload;
                if (curData.expired_at !== PERMANENT_TIMESTAMP) {
                    curData.expired_at = curData.expired_at + this.user.timestamp;
                }

                curData.resource_groups = curData.resource_groups.filter(groupItem => {
                    groupItem.related_resource_types = groupItem.related_resource_types.filter(typeItem => {
                        typeItem.condition.filter(e => {
                            if ((e.instance && e.instance.length > 0) || (e.attribute && e.attribute.length > 0)) {
                                e.instances = e.instance || [];
                                e.attributes = e.attribute || [];
                                delete e.instance;
                                delete e.attribute;
                                return true;
                            }
                            return false;
                        });
                        return !(typeItem.condition.length === 1 && typeItem.condition[0] === 'none');
                    });
                    // eslint-disable-next-line max-len
                    return !(groupItem.related_resource_types[0] && groupItem.related_resource_types[0].condition.length === 1
                        && groupItem.related_resource_types[0].condition[0] === 'none');
                });

                const relatedList = _.cloneDeep(this.tableList.filter(item => {
                    return !item.isAggregate
                        && relatedActions.includes(item.id)
                        // && item.resource_groups[this.curGroupIndex]
                        // && !item.resource_groups[this.curGroupIndex].related_resource_types.every(sub => sub.empty)
                        && item.resource_groups.map(item => !item.related_resource_types.every(sub => sub.empty))[0];
                }));

                if (relatedList.length > 0) {
                    relatedList.forEach(item => {
                        if (!item.policy_id) {
                            item.expired_at = item.expired_at + this.user.timestamp;
                        }
                        delete item.policy_id;
                        item.resource_groups.forEach(groupItem => {
                            groupItem.related_resource_types.forEach(resItem => {
                                resItem.condition.filter(conditionItem => {
                                    // eslint-disable-next-line max-len
                                    if ((conditionItem.instance && conditionItem.instance.length > 0) || (conditionItem.attribute && conditionItem.attribute.length > 0)) {
                                        conditionItem.instances = conditionItem.instance || [];
                                        conditionItem.attributes = conditionItem.attribute || [];
                                        delete conditionItem.instance;
                                        delete conditionItem.attribute;
                                        return true;
                                    }
                                    return false;
                                });
                            });
                        });
                        // item.resource_groups[this.curGroupIndex].related_resource_types.forEach(resItem => {
                        //     resItem.condition.forEach(conditionItem => {
                        //         conditionItem.instances = conditionItem.instance || []
                        //         conditionItem.attributes = conditionItem.attribute || []
                        //         delete conditionItem.instance
                        //         delete conditionItem.attribute
                        //     })
                        // })
                    });
                }
                try {
                    const res = await this.$store.dispatch('permApply/getRelatedPolicy', {
                        source_policy: curData,
                        system_id: this.systemId,
                        target_policies: relatedList
                    });
                    this.handleRelatedAction(res.data);
                } catch (e) {
                    console.error(e);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                } finally {
                    this.sliderLoading = false;
                }
            },

            /**
             *new Policy() 第三个参数会影响@/components/choose-ip/view中是否可移除的disabled
             * 具体体现在instance.js文件initPath方法中
             */
            handleRelatedAction (payload) {
                if (payload.length < 1) {
                    return;
                }

                payload.forEach(item => {
                    const curIndex = this.tableList.findIndex(sub => sub.id === item.id);
                    if (curIndex > -1) {
                        const curData = this.tableList[curIndex];
                        // 记录原来数据的生效条件
                        if (curData.related_environments && !!curData.related_environments.length) {
                            item.related_environments = curData.related_environments;
                        }
                        this.needEmitFlag = true;
                        const inOriginalList = !!this.originalList.filter(
                            original => String(original.id) === String(item.id)
                        ).length;
                        item.expired_at = item.expired_at - this.user.timestamp;
                        this.tableList.splice(
                            curIndex,
                            1,
                            new Policy({ ...item, tag: curData.tag === 'add' ? 'add' : item.tag, isShowRelatedText: true, inOriginalList }, '', false)
                        );
                    }
                });
            },

            async handleResourceSumit () {
                const conditionData = this.$refs.renderResourceRef.handleGetValue();
                const { isEmpty, data } = conditionData;
                if (isEmpty) {
                    return;
                }

                const resItem = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex];
                const isConditionEmpty = data.length === 1 && data[0] === 'none';
                if (isConditionEmpty) {
                    resItem.condition = ['none'];
                    resItem.isLimitExceeded = false;
                } else {
                    const { isMainAction, related_actions } = this.tableList[this.curIndex];
                    // 如果为主操作
                    if (isMainAction) {
                        await this.handleMainActionSubmit(data, related_actions);
                    }
                    resItem.condition = data;
                    resItem.isError = false;
                }

                window.changeAlert = false;
                this.resourceInstanceSidesliderTitle = '';
                this.isShowResourceInstanceSideslider = false;

                if (!isConditionEmpty && resItem.isLimitExceeded) {
                    let newResourceCount = 0;
                    const conditionList = resItem.condition;
                    conditionList.forEach(item => {
                        item.instance.forEach(instanceItem => {
                            instanceItem.paths.forEach(v => {
                                // 是否带有下一层级的无限制
                                const isHasNoLimit = v.some(({ id }) => id === '*');
                                const isDisabled = v.some(_ => !!_.disabled);
                                // 可编辑的才会计数
                                if (!isHasNoLimit && !isDisabled) {
                                    ++newResourceCount;
                                }
                            });
                        });
                    });
                    console.warn('newResourceCount: ' + newResourceCount);
                    if (newResourceCount <= RESOURCE_MAX_LEN) {
                        resItem.isLimitExceeded = false;
                    }
                }

                this.curIndex = -1;
                this.curResIndex = -1;
                this.curGroupIndex = -1;

                // 主操作的实例映射到了具体的依赖操作上，需更新到父级的缓存数据中
                if (this.needEmitFlag) {
                    this.$emit('on-realted-change', this.tableList);
                }
            },

            handleResourcePreview () {
                const { system_id, type, name } = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex];
                const condition = [];
                const conditionData = this.$refs.renderResourceRef.handleGetPreviewValue();
                conditionData.forEach(item => {
                    const { id, attribute, instance } = item;
                    condition.push({
                        id,
                        attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
                        instances: instance ? instance.filter(item => item.path.length > 0) : []
                    });
                });
                this.previewResourceParams = {
                    policy_id: this.tableList[this.curIndex].policy_id,
                    resource_group_id: this.tableList[this.curIndex].resource_groups[this.curGroupIndex].id,
                    related_resource_type: {
                        system_id,
                        type,
                        name,
                        condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
                    }
                };
                this.previewDialogTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${this.tableList[this.curIndex].name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)} ${this.$t(`m.common['差异对比']`)}`;
                this.isShowPreviewDialog = true;
            },

            handlerConditionMouseover (payload) {
                if (Object.keys(this.curCopyParams).length < 1 && this.curCopyMode === 'normal') {
                    return;
                }
                if (this.curCopyData[0] === 'none' && this.curCopyMode === 'aggregate') {
                    return;
                }
                if (this.curCopyKey === `${payload.system_id}${payload.type}`) {
                    payload.canPaste = true;
                }
            },

            handlerConditionMouseleave (payload) {
                payload.canPaste = false;
            },

            handlerOnView (payload, item, itemIndex, groupIndex) {
                const { system_id, type, name } = item;
                const condition = [];
                item.condition.forEach(item => {
                    const { id, attribute, instance } = item;
                    condition.push({
                        id,
                        attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
                        instances: instance ? instance.filter(item => item.path.length > 0) : []
                    });
                });
                this.previewResourceParams = {
                    policy_id: payload.policy_id,
                    resource_group_id: payload.resource_groups[groupIndex].id,
                    related_resource_type: {
                        system_id,
                        type,
                        name,
                        condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
                    }
                };
                this.previewDialogTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)} ${this.$t(`m.common['差异对比']`)}`;
                this.isShowPreviewDialog = true;
            },

            handlerOnCopy (payload, index, subIndex, action) {
                this.curCopyKey = `${payload.system_id}${payload.type}`;
                this.curCopyData = _.cloneDeep(payload.condition);
                this.curCopyMode = 'normal';
                this.curCopyParams = this.getBacthCopyParms(action, payload);
                this.showMessage(this.$t(`m.info['实例复制']`));
                this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(true);
            },

            getBacthCopyParms (payload, content) {
                const actions = [];
                this.tableList.forEach(item => {
                    if (!item.isAggregate) {
                        if (item.id !== payload.id) {
                            actions.push({
                                system_id: this.systemId,
                                id: item.id
                            });
                        }
                    }
                });
                actions.unshift({
                    system_id: this.systemId,
                    id: payload.id
                });
                return {
                    resource_type: {
                        system_id: content.system_id,
                        type: content.type,
                        condition: content.condition.map(item => {
                            return {
                                id: item.id,
                                instances: item.instance || [],
                                attributes: item.attribute || []
                            };
                        })
                    },
                    actions
                };
            },

            handlerOnPaste (payload, row, content) {
                let tempCurData = ['none'];
                if (this.curCopyMode === 'normal') {
                    // if (this.curCopyData.length < 1) {
                    //     tempCurData = []
                    // } else {
                    //     if (this.curCopyData[0] !== 'none') {
                    //         tempCurData = this.curCopyData.map(item => {
                    //             delete item.id
                    //             return item
                    //         })
                    //         tempCurData.forEach((item, index) => {
                    //             if (content.condition[index]) {
                    //                 if (content.condition[index].id) {
                    //                     item.id = content.condition[index].id
                    //                 } else {
                    //                     item.id = ''
                    //                 }
                    //             } else {
                    //                 item.id = ''
                    //             }
                    //         })
                    //     }
                    // }
                    if (!payload.flag) {
                        return;
                    }
                    if (payload.data.length === 0) {
                        content.condition = [];
                    } else {
                        content.condition = payload.data.map(conditionItem => new Condition(conditionItem, '', 'add'));
                    }
                } else {
                    const instances = (() => {
                        const arr = [];
                        const { id, name, system_id } = this.curAggregateResourceType;
                        this.curCopyData.forEach(v => {
                            const curItem = arr.find(_ => _.type === id);
                            if (curItem) {
                                curItem.path.push([{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }]);
                            } else {
                                arr.push({
                                    name,
                                    type: id,
                                    path: [[{
                                        id: v.id,
                                        name: v.name,
                                        system_id,
                                        type: id,
                                        type_name: name
                                    }]]
                                });
                            }
                        });
                        return arr;
                    })();
                    if (instances.length > 0) {
                        tempCurData = [new Condition({ instances }, '', 'add')];
                    }
                }
                if (tempCurData[0] === 'none') {
                    return;
                }
                content.condition = _.cloneDeep(tempCurData);
                content.isError = false;
                this.showMessage(this.$t(`m.info['粘贴成功']`));
            },

            handlerOnBatchPaste (payload, content, index, subIndex) {
                let tempCurData = ['none'];
                let tempArrgegateData = [];
                if (this.curCopyMode === 'normal') {
                    if (!payload.flag) {
                        return;
                    }
                    // 预计算是否存在 聚合后的数据 可以粘贴
                    const flag = this.tableList.some(item => {
                        return !!item.isAggregate
                            && item.aggregateResourceType.some(e => `${e.system_id}${e.id}` === this.curCopyKey);
                    });
                    if (flag) {
                        if (this.curCopyData.length < 1) {
                            tempCurData = [];
                        } else {
                            if (this.curCopyData[0] !== 'none') {
                                tempCurData = this.curCopyData.map(item => {
                                    delete item.id;
                                    return item;
                                });
                                tempCurData.forEach((item, index) => {
                                    if (content.condition[index]) {
                                        if (content.condition[index].id) {
                                            item.id = content.condition[index].id;
                                        } else {
                                            item.id = '';
                                        }
                                    } else {
                                        item.id = '';
                                    }
                                });
                                const instances = this.curCopyData.map(item => item.instance);
                                const instanceData = instances[0][0];
                                tempArrgegateData = instanceData.path.map(pathItem => {
                                    return {
                                        id: pathItem[0].id,
                                        name: pathItem[0].name
                                    };
                                });
                            }
                        }
                    }
                    if (payload.data.length === 0) {
                        this.tableList.forEach(item => {
                            if (!item.isAggregate) {
                                item.resource_groups.forEach(groupItem => {
                                    groupItem.related_resource_types.forEach(resItem => {
                                        if (`${resItem.system_id}${resItem.type}` === this.curCopyKey) {
                                            resItem.condition = [];
                                            resItem.isError = false;
                                        }
                                    });
                                });
                            } else {
                                if (`${item.aggregateResourceType[item.selectedIndex].system_id}${item.aggregateResourceType[item.selectedIndex].id}` === this.curCopyKey) {
                                    item.instances = _.cloneDeep(tempArrgegateData);
                                    item.isError = false;
                                    this.$emit('on-select', item);
                                }
                            }
                        });
                    } else {
                        this.tableList.forEach(item => {
                            if (!item.isAggregate) {
                                const curPasteData = payload.data.find(_ => _.id === item.id);
                                if (curPasteData) {
                                    item.resource_groups.forEach(groupItem => {
                                        groupItem.related_resource_types.forEach(resItem => {
                                            if (`${resItem.system_id}${resItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                                                resItem.condition = curPasteData.resource_type.condition.map(conditionItem => new Condition(conditionItem, '', 'add'));
                                                resItem.isError = false;
                                            }
                                        });
                                    });
                                }
                            } else {
                                item.aggregateResourceType.forEach(aggregateResourceItem => {
                                    if (`${aggregateResourceItem.system_id}${aggregateResourceItem.id}` === this.curCopyKey) {
                                        item.instances = _.cloneDeep(tempArrgegateData);
                                        this.instanceKey = aggregateResourceItem.id;
                                        this.setNomalInstancesDisplayData(item, this.instanceKey);
                                        this.instanceKey = ''; // 重置
                                        item.isError = false;
                                    }
                                });
                                this.$emit('on-select', item);
                            }
                        });
                    }
                } else {
                    tempArrgegateData = this.curCopyData;
                    const instances = (() => {
                        const arr = [];
                        const { id, name, system_id } = this.curAggregateResourceType;
                        this.curCopyData.forEach(v => {
                            const curItem = arr.find(_ => _.type === id);
                            if (curItem) {
                                curItem.path.push([{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }]);
                            } else {
                                arr.push({
                                    name,
                                    type: id,
                                    path: [[{
                                        id: v.id,
                                        name: v.name,
                                        system_id,
                                        type: id,
                                        type_name: name
                                    }]]
                                });
                            }
                        });
                        return arr;
                    })();
                    if (instances.length > 0) {
                        tempCurData = [new Condition({ instances }, '', 'add')];
                    }
                    this.tableList.forEach(item => {
                        if (!item.isAggregate) {
                            item.related_resource_types.forEach(subItem => {
                                if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                                    subItem.condition = _.cloneDeep(tempCurData);
                                    subItem.isError = false;
                                }
                            });
                        } else {
                            if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                                item.instances = _.cloneDeep(tempArrgegateData);
                                item.isError = false;
                            }
                        }
                    });
                }
                content.isError = false;
                this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(false);
                this.curCopyData = ['none'];
                this.showMessage(this.$t(`m.info['批量粘贴成功']`));
            },

            handlePreviewDialogClose () {
                this.previewDialogTitle = '';
                this.isShowPreviewDialog = false;
            },

            resetDataAfterClose () {
                this.curIndex = -1;
                this.curResIndex = -1;
                this.curGroupIndex = -1;
                this.previewResourceParams = {};
                this.params = {};
                this.resourceInstanceSidesliderTitle = '';
                this.resourceInstanceEffectTimeTitle = '';
            },

            handleResourceCancel () {
                let cancelHandler = Promise.resolve();
                if (window.changeAlert) {
                    cancelHandler = leaveConfirm();
                }
                cancelHandler.then(() => {
                    this.isShowResourceInstanceSideslider = false;
                    this.resetDataAfterClose();
                }, _ => _);
            },

            handleExpiredToggle (value, row) {
                if (!value) {
                    row.isShowCustom = false;
                    row.customValue = '';
                }
            },

            handleExpiredSelect (value, option, row) {
                row.isShowCustom = false;
                row.customValue = '';
                const curSelected = this.durationList.find(item => item.id === value);
                row.expired_display = curSelected.name;
            },

            handleBlur (value, e, row) {
                row.isShowCustom = false;
                row.customValue = '';
                this.handleEnter(value, e, row);
            },

            handleInput (value, e, row) {
                const flag = /^([1-9]|[1-2][0-4])$/.test(value);
                if (!flag) {
                    if (parseInt(value, 10) > 24) {
                        setTimeout(() => {
                            row.customValue = 24;
                        }, 100);
                    } else {
                        setTimeout(() => {
                            row.customValue = '';
                        }, 100);
                    }
                }
            },

            handleEnter (value, e, row) {
                if (value === '') {
                    return;
                }
                row.isShowCustom = false;
                row.customValue = Number(value);
                row.expired_at = '';
                row.expired_display = `${value} ${this.$t(`m.common['小时']`)}`;
                this.$refs[`${row.id}&expiredAtRef`] && this.$refs[`${row.id}&expiredAtRef`].close();
            },

            handleGetValue () {
                // flag：提交时校验标识
                let flag = false;
                if (this.tableList.length < 1) {
                    flag = true;
                    return {
                        flag,
                        actions: [],
                        aggregations: []
                    };
                }
                const actionList = [];
                const aggregations = [];

                // 重新赋值
                if (this.isAllExpanded) {
                    this.tableList = this.tableList.filter(e =>
                        (e.resource_groups && e.resource_groups.length)
                        || e.isAggregate);
                    if (this.emptyResourceGroupsList.length) {
                        this.emptyResourceGroupsList[0].name = this.emptyResourceGroupsName[0];
                        this.tableList = [...this.tableList, ...this.emptyResourceGroupsList];
                    }
                }
                
                this.tableList.forEach(item => {
                    let tempExpiredAt = '';
                    if (item.expired_at === '' && item.expired_display) {
                        tempExpiredAt = parseInt(item.expired_display, 10);
                    }

                    if (!item.isAggregate) {
                        const { type, id, name, environment, description, policy_id, isNew, isChanged } = item;
                        
                        const groupResourceTypes = [];
                        if (item.resource_groups.length > 0) {
                            item.resource_groups.forEach(groupItem => {
                                const relatedResourceTypes = [];
                                if (groupItem.related_resource_types.length > 0) {
                                    groupItem.related_resource_types.forEach(resItem => {
                                        let newResourceCount = 0;
                                        if (resItem.empty) {
                                            resItem.isError = true;
                                            flag = true;
                                        }
                                        const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                                            ? resItem.condition.map(conItem => {
                                                const { id, instance, attribute } = conItem;
                                                const attributeList = (attribute && attribute.length > 0)
                                                    ? attribute.map(({ id, name, values }) => ({ id, name, values }))
                                                    : [];
        
                                                const instanceList = (instance && instance.length > 0)
                                                    ? instance.map(({ name, type, paths }) => {
                                                        const tempPath = _.cloneDeep(paths);
                                                        tempPath.forEach(pathItem => {
                                                            // 是否带有下一层级的无限制
                                                            const isHasNoLimit = pathItem.some(({ id }) => id === '*');
                                                            const isDisabled = pathItem.some(_ => !!_.disabled);
                                                            if (!isHasNoLimit && !isDisabled) {
                                                                ++newResourceCount;
                                                            }
                                                            pathItem.forEach(pathSubItem => {
                                                                delete pathSubItem.disabled;
                                                            });
                                                        });
                                                        return {
                                                            name,
                                                            type,
                                                            path: tempPath
                                                        };
                                                    })
                                                    : [];
                                                return {
                                                    id,
                                                    instances: instanceList,
                                                    attributes: attributeList
                                                };
                                            })
                                            : [];
                                        console.warn('newResourceCount: ' + newResourceCount);
                                        if (newResourceCount > RESOURCE_MAX_LEN) {
                                            resItem.isLimitExceeded = true;
                                            flag = true;
                                        }
                                        relatedResourceTypes.push({
                                            type: resItem.type,
                                            system_id: resItem.system_id,
                                            name: resItem.name,
                                            condition: conditionList.filter(
                                                item => item.instances.length > 0 || item.attributes.length > 0
                                            )
                                        });
                                    });
                                }
                                groupResourceTypes.push({
                                    environments: groupItem.environments,
                                    id: groupItem.id,
                                    related_resource_types: relatedResourceTypes
                                });
                            });
                            // 强制刷新下
                            item.resource_groups = _.cloneDeep(item.resource_groups);
                        }
                        const params = {
                            type,
                            name,
                            id,
                            description,
                            resource_groups: groupResourceTypes,
                            environment,
                            policy_id,
                            expired_at: item.expired_at === '' ? tempExpiredAt : Number(item.expired_at)
                        };
                        if ((isNew || isChanged || item.isExpired) && params.expired_at !== PERMANENT_TIMESTAMP) { // 变更isChanged也需要加上this.user.timestamp
                            // 说明显示了 取消续期 按钮，即选择续期时间的下拉框已经选择了选择具体的续期时间，所以过期时间是选择的那个续期时间加上时间戳
                            // 如果没有显示 取消续期 按钮，那么就是显示的续期按钮，这时没有选择具体的续期时间因此过期时间还是之前的，不变
                            if (!item.isShowRenewal) {
                                params.expired_at = params.expired_at + this.user.timestamp;
                            }
                        }
                        if (params.policy_id === '') {
                            delete params.policy_id;
                        }
                        actionList.push(_.cloneDeep(params));
                    } else {
                        const { actions, aggregateResourceType, instances, instancesDisplayData } = item;
                        if (instances.length < 1) {
                            item.isError = true;
                            flag = true;
                        } else {
                            const aggregateResourceTypes = aggregateResourceType.reduce((p, e) => {
                                if (instancesDisplayData[e.id] && instancesDisplayData[e.id].length) {
                                    const obj = {};
                                    obj.id = e.id;
                                    obj.system_id = e.system_id;
                                    obj.instances = instancesDisplayData[e.id];
                                    p.push(obj);
                                }
                                return p;
                            }, []);
                            const params = {
                                actions,
                                expired_at: item.expired_at === '' ? tempExpiredAt : Number(item.expired_at),
                                aggregate_resource_types: aggregateResourceTypes
                            };
                            if (params.expired_at !== PERMANENT_TIMESTAMP) {
                                params.expired_at = params.expired_at + this.user.timestamp;
                            }
                            aggregations.push(params);
                        }
                    }
                });
                return {
                    flag,
                    actions: actionList,
                    aggregations
                };
            },

            handlerAddCondition (data, index, resIndex) {
                const dataClone = _.cloneDeep(data);
                // dataClone.related_resource_types[resIndex].condition = ['none']
                // dataClone.related_resource_types[resIndex].conditionBackup = ['none']
                dataClone.related_resource_types = dataClone.related_resource_types.map(e => {
                    e.condition = ['none'];
                    e.conditionBackup = ['none'];
                    return e;
                });
                const relatedResourceTypes = _.cloneDeep(
                    {
                        id: '',
                        related_resource_types: dataClone.related_resource_types
                    }
                );
                if (dataClone.environments) {
                    relatedResourceTypes.environments = [];
                }
                this.tableList[index].resource_groups.push(relatedResourceTypes);
                this.originalList = _.cloneDeep(this.tableList);
            },

            handlerReduceCondition (data, index, resIndex, groupIndex) {
                if (data.id || this.tableList[index].resource_groups.length === 1) return;
                this.tableList[index].resource_groups.splice(groupIndex, 1);
            },

            // 生效条件侧边栏
            showTimeSlider (data, index, groupIndex) {
                this.curIndex = index;
                this.curGroupIndex = groupIndex;
                this.isShowResourceInstanceEffectTime = true;
                this.resourceInstanceEffectTimeTitle = `${this.$t(`m.common['关联操作']`)}${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['生效条件']`)}`;
            },

            // 生效条件保存
            handleResourceEffectTimeSumit () {
                const environments = this.$refs.sidesliderRef.handleGetValue();
                if (!environments) return;

                const resItem = this.tableList[this.curIndex].resource_groups[this.curGroupIndex];
                resItem.environments = environments;

                window.changeAlert = false;
                this.resourceInstanceEffectTimeTitle = '';
                this.isShowResourceInstanceEffectTime = false;
                this.curIndex = -1;
                this.curGroupIndex = -1;
            },

            handleResourceEffectTimeCancel () {
                let cancelHandler = Promise.resolve();
                if (window.changeAlert) {
                    cancelHandler = leaveConfirm();
                }
                cancelHandler.then(() => {
                    this.isShowResourceInstanceEffectTime = false;
                    this.resetDataAfterClose();
                }, _ => _);
            },

            selectResourceType (data, index) {
                data.selectedIndex = index;
                this.selectedIndex = index;
            }
        }
    };
</script>

<style>
    @import './resource-instance-table.css';
</style>

<!-- eslint-disable max-len -->
<template>
  <div>
    <!-- 申请自定义权限正常跳转 -->
    <smart-action class="biz-perm-apply" v-if="!isNoPermApply && !isNoPermissionsSet">
      <render-horizontal-block :required="true" ext-cls="apply-way-wrapper" :label="$t(`m.permApply['选择操作']`)">
        <render-search>
          <bk-select
            v-model="systemValue"
            style="width: 480px;"
            :popover-min-width="480"
            :empty-text="$t(`m.common['暂无数据']`)"
            :search-placeholder="$t(`m.info['搜索关键字']`)"
            :searchable="true"
            :search-with-pinyin="true"
            :clearable="false"
            @selected="handleSysSelected"
            @toggle="handleToggle">
            <bk-option
              v-for="option in systemList"
              v-bind="option"
              :key="option.id"
              :id="option.id"
              :name="option.displayName">
              <div class="select-collection"
                @mouseenter="handleSystemEnter(option.id)"
                @mouseleave="handleSystemLeave(option.id)"
              >
                <div>
                  <span>{{ option.name }}</span>
                  <span style="color: #c4c6cc;">({{ option.id }})</span>
                </div>
                <bk-star
                  v-if="(hoverId === option.id || option.is_favorite)"
                  :rate="option.is_favorite"
                  :max-stars="1"
                  @click.native.stop="handleCollection(option)">
                </bk-star>
              </div>
            </bk-option>
          </bk-select>
          <div slot="right">
            <bk-input
              clearable
              v-model="actionSearchValue"
              :placeholder="$t(`m.info['操作搜索提示']`)"
              style="width: 320px;"
              @enter="handleActionSearch">
            </bk-input>
          </div>
        </render-search>
        <form class="bk-form bk-form-vertical inner-content">
          <div class="bk-form-item">
            <div
              ref="selectActionRef"
              v-bkloading="{ isLoading: customLoading, opacity: 1 }"
              :class="[
                'custom-tmpl-list-content-wrapper',
                { 'is-loading': customLoading }
              ]"
            >
              <render-action-tag
                ref="commonActionRef"
                :system-id="systemValue"
                :tag-action-list="tagActionList"
                v-if="commonActions.length > 0 && !customLoading"
                mode="detail"
                :data="commonActions"
                @on-change="handleActionTagChange"
                @on-mouse-enter="handleActionTagEnter"
                @on-mouse-leave="handleActionTagLeave" />
              <template v-if="originalCustomTmplList.length > 0 && !customLoading">
                <div class="action-empty-error" v-if="isShowActionError">{{ $t(`m.verify['请选择操作']`) }}</div>
                <div class="actions-wrapper">
                  <div
                    v-for="(item, index) in originalCustomTmplList"
                    :key="index"
                    :class="[
                      'action-item',
                      { 'set-border': originalCustomTmplList.length > 1 },
                      { 'action-item-none': !isShowGroupTitle(item) }
                    ]">
                    <p style="cursor: pointer;" @click.stop="handleExpanded(item)" v-if="isShowGroupTitle(item)">
                      <section :class="['action-group-name', { 'set-cursor': originalCustomTmplList.length > 1 }]">
                        <Icon :type="item.expanded ? 'down-angle' : 'right-angle'" v-if="originalCustomTmplList.length > 1" />
                        <span :class="[{ 'action-hover': handleFormatTitleHover(item) }]">
                          {{ item.name }}
                        </span>
                        <span class="count">{{$t(`m.common['已选']`)}} {{ item.count }} / {{ item.allCount }} {{ $t(`m.common['个']`) }}</span>
                      </section>
                      <span :class="['check-all', { 'is-disabled': item.actionsAllDisabled }]" @click.stop="handleCheckAll(item)">
                        {{ item.actionsAllChecked ? $t(`m.common['取消全选']`) : $t(`m.common['选择全部']`) }}
                      </span>
                    </p>
                    <div class="action-content" v-if="item.expanded">
                      <div
                        :class="['self-action-content', { 'set-border-bottom': isShowGroupAction(item) }]"
                        v-if="item.actions && item.actions.length > 0">
                        <bk-checkbox
                          v-for="(act, actIndex) in item.actions"
                          :key="actIndex"
                          :true-value="true"
                          :false-value="false"
                          v-model="act.checked"
                          :disabled="act.disabled"
                          :ext-cls="hoverActionData.actions.includes(act.id) ? 'iam-action-cls iam-action-hover' : 'iam-action-cls'"
                          @change="handleActionChecked(...arguments, act, item)">
                          <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                            <template v-if="act.disabled">
                              <span class="text" @click.stop="handleDisabledClick(act)">{{ act.name }}</span>
                            </template>
                            <template v-else>
                              <span class="text">{{ act.name }}</span>
                            </template>
                            <div slot="content" class="iam-perm-apply-action-popover-content">
                              <div>
                                <span class="name">{{ act.name }}</span>
                                <span :class="handleClassComputed(act)">({{ act.checked ? act.disabled ? $t(`m.common['已获得']`) : $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})</span>
                              </div>
                              <div class="description">{{ $t(`m.common['描述']`) + '：' + (act.description || '--') }}</div>
                              <div class="relate-action" v-if="act.related_actions.length > 0">
                                {{ getRelatedActionTips(act.related_actions) }}
                              </div>
                            </div>
                          </bk-popover>
                        </bk-checkbox>
                        <bk-checkbox
                          :true-value="true"
                          :false-value="false"
                          v-model="item.allChecked"
                          :disabled="item.actions.every(v => v.disabled)"
                          ext-cls="iam-action-all-cls"
                          @change="handleAllChange(...arguments, item)">
                          {{ $t(`m.common['全选']`) }}
                        </bk-checkbox>
                      </div>
                      <div class="sub-group-action-content" v-if="isShowGroupSubAction(item)">
                        <section
                          v-for="(subAct, subIndex) in item.sub_groups"
                          :key="subIndex"
                          :class="[
                            'sub-action-item',
                            { 'set-margin': subIndex !== 0 },
                            { 'sub-action-item-none': !subAct.actions.length }
                          ]">
                          <div class="sub-action-wrapper">
                            <span class="name" :title="subAct.name" v-if="subAct.actions.length > 0">{{ subAct.name }}</span>
                            <section>
                              <bk-checkbox
                                v-for="(act, actIndex) in subAct.actions"
                                :key="actIndex"
                                :true-value="true"
                                :false-value="false"
                                v-model="act.checked"
                                :disabled="act.disabled"
                                :ext-cls="hoverActionData.actions.includes(act.id) ? 'iam-action-cls iam-action-hover' : 'iam-action-cls'"
                                @change="handleSubActionChecked(...arguments, act, subAct, item)">
                                <bk-popover placement="top" :delay="300" ext-cls="iam-tooltips-cls">
                                  <template v-if="act.disabled">
                                    <span class="text" @click.stop="handleDisabledClick(act)">{{ act.name }}</span>
                                  </template>
                                  <template v-else>
                                    <span class="text">{{ act.name }}</span>
                                  </template>
                                  <div slot="content" class="iam-perm-apply-action-popover-content">
                                    <div>
                                      <span class="name">{{ act.name }}</span>
                                      <span :class="handleClassComputed(act)">({{ act.checked ? act.disabled ? $t(`m.common['已获得']`) : $t(`m.common['已选择']`) : $t(`m.common['未选择']`) }})</span>
                                    </div>
                                    <div class="description">{{ $t(`m.common['描述']`) + '：' + (act.description || '--') }}</div>
                                    <div class="relate-action" v-if="act.related_actions.length > 0">
                                      {{ getRelatedActionTips(act.related_actions) }}
                                    </div>
                                  </div>
                                </bk-popover>
                              </bk-checkbox>
                            </section>
                          </div>
                          <bk-checkbox
                            v-if="subAct.actions.length > 0"
                            :true-value="true"
                            :false-value="false"
                            v-model="subAct.allChecked"
                            :disabled="subAct.actions.every(v => v.disabled)"
                            ext-cls="iam-sub-action-all-cls"
                            @change="handleSubAllChange(...arguments, subAct, item)">
                            {{ $t(`m.common['全选']`) }}
                          </bk-checkbox>
                        </section>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
              <template v-if="originalCustomTmplList.length < 1 && !customLoading">
                <div class="empty-wrapper">
                  <ExceptionEmpty
                    :type="emptyData.type"
                    :empty-text="emptyData.text"
                    :tip-text="emptyData.tip"
                    :tip-type="emptyData.tipType"
                    @on-clear="handleEmptyClear"
                    @on-refresh="handleEmptyRefresh"
                  />
                  <!-- <Icon type="warning" />
                                    {{ isActionsFilter ? $t(`m.common['搜索无结果']`) : $t(`m.permApply['暂无可申请的操作']`) }} -->
                </div>
              </template>
            </div>
          </div>
        </form>
      </render-horizontal-block>
      <render-horizontal-block ext-cls="mt16" :label="$t(`m.permApply['关联资源实例']`)">
        <div
          ref="instanceTableRef"
          class="aggregate-tab-instance-table perm-apply-resource-instance-table"
        >
          <resource-instance-table
            :list="tableData"
            :original-table-list="tableDataBackup"
            :system-id="systemValue"
            :button-loading="buttonLoading"
            :is-all-expanded="isAllExpanded"
            ref="resInstanceTableRef"
            @on-select="handleResourceSelect"
            @on-realted-change="handleRelatedChange"
          />
          <div slot="append" class="expanded-action-wrapper">
            <div class="apply-custom-switch">
              <div class="apply-custom-switch-item">
                <bk-switcher
                  v-model="isAllUnlimited"
                  theme="primary"
                  size="small"
                  :disabled="isUnlimitedDisabled"
                  @change="handleUnlimitedActionChange">
                </bk-switcher>
                <span class="expanded-text">{{ $t(`m.common['批量无限制']`) }}</span>
              </div>
              <div class="aggregate-action-tab-group">
                <div
                  v-for="item in AGGREGATION_EDIT_ENUM"
                  :key="item.value"
                  :class="[
                    'aggregate-action-btn',
                    { 'is-active': isAllExpanded === item.value },
                    { 'is-disabled': isAggregateDisabled }
                  ]"
                  @click.stop="handleAggregateActionChange(item.value)"
                >
                  <span>{{ $t(`m.grading['${item.name}']`)}}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </render-horizontal-block>
      <render-horizontal-block :label="$t(`m.permApply['选择权限获得者']`)" :required="false">
        <section ref="permRecipientRef">
          <bk-user-selector
            :value="permMembers"
            :api="userApi"
            :placeholder="$t(`m.permApply['请输入权限获得者']`)"
            :style="{ width: '60%' }"
            :class="isShowMemberError ? 'is-member-empty-cls' : ''"
            :empty-text="$t(`m.common['无匹配人员']`)"
            data-test-id="grading_userSelector_member"
            @focus="handleRtxFocus"
            @blur="handleRtxBlur"
            @change="handleRtxChange" />
          <!-- <p class="perm-recipient-error" v-if="isShowMemberError">{{ $t(`m.permApply['请选择权限获得者']`) }}</p> -->
        </section>
      </render-horizontal-block>
      <render-horizontal-block ext-cls="reason-wrapper" :label="$t(`m.common['理由']`)" :required="true">
        <section ref="resInstanceReasonRef">
          <bk-input
            type="textarea"
            v-model="reason"
            :maxlength="255"
            :placeholder="$t(`m.verify['请输入']`)"
            :ext-cls="isShowReasonError ? 'perm-apply-reason-error' : ''"
            @input="handleReasonInput"
            @blur="handleReasonBlur">
          </bk-input>
          <p class="reason-empty-wrapper" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
        </section>
      </render-horizontal-block>
      <div slot="action">
        <bk-button
          theme="primary"
          :loading="buttonLoading"
          @click="handleApplySubmit">
          {{ $t(`m.common['提交']`) }}
        </bk-button>
        <bk-button
          style="margin-left: 10px;"
          @click="handleCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </smart-action>
    <!-- 用户组权限申请默认页面  -->
    <smart-action class="applpForPermission" v-if="isNoPermissionsSet && isShowHasUserGroup">
      <div class="form-tab">
        <div class="tab-item"
          :class="tabIndex === index ? 'active' : ''"
          v-for="(item, index) in tabData" :key="item.key"
          @click="clickTab(index, item.key)">
          <div class="tab-title">
            <span :title="item.title" :class="index === 0 ? 'tab-item-title' : ''">{{item.title}}</span>
            <span class="recommend" v-if="index === 0">{{$t(`m.permApply['推荐']`)}}</span>
          </div>
          <div class="tab-desc" :title="item.desc">{{item.desc}}</div>
        </div>
      </div>
      <div class="groupPermissionQequest" v-if="isShowUserGroup">
        <render-horizontal-block>
          <div class="userGroup">
            <div class="requestRecommendText pl20">
              {{$t(`m.permApply['根据你的需求，自动匹配到以下的用户组']`)}}
            </div>
            <div class="info">
              {{ $t(`m.info['如果需要更多用户组权限']`) }}{{ $t(`m.common['，']`) }}
              {{ $t(`m.info['可前往']`) }}
              <bk-button
                text
                theme="primary"
                style="font-size: 12px;"
                @click="handleToUserGroup">
                {{ $t(`m.info['申请用户组权限']`) }}
              </bk-button>
            </div>
          </div>
          <div>
            <bk-transition name="bk-fade-in-ease">
              <div>
                <div class="user-group-table">
                  <bk-table
                    ref="groupTableRef"
                    ext-cls="user-group-table"
                    :class="{ 'set-border': tableLoading }"
                    v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                    :data="tableList"
                    @select="handlerOneChange"
                    @select-all="handlerAllChange"
                    :cell-attributes="handleCellAttributes">
                    <bk-table-column type="selection" align="center" :selectable="setDefaultSelect"></bk-table-column>
                    <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
                      <template slot-scope="{ row }">
                        <div class="user-group-name-column">
                          <span class="single-hide user-group-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
                          <div v-if="row.expired_at && user.timestamp > row.expired_at">
                            <!-- <Icon type="error-fill" class="error-icon" />
                            <span class="expired-text">{{$t(`m.permApply['你已获得该组权限，但是已过期']`)}}</span> -->
                            (
                            <span>{{ row.expired_at_display }}{{ $t(`m.common['，']`) }}</span>
                            <bk-button
                              text
                              theme="primary"
                              style="font-size: 12px;"
                              @click="handleBatchRenewal">
                              {{ $t(`m.permApply['去续期']`) }}
                            </bk-button>
                            )
                          </div>
                          <template v-else>
                            <span v-if="row.expired_at_display">
                              {{ row.expired_at === 4102444800 ?
                                `(${row.expired_at_display})`
                                : `(${$t(`m.common['有效期']`)}  ${row.expired_at_display})`}}
                            </span>
                          </template>
                        </div>
                      </template>
                    </bk-table-column>
                    <bk-table-column :label="$t(`m.userGroup['描述']`)">
                      <template slot-scope="{ row }">
                        <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
                      </template>
                    </bk-table-column>
                    <bk-table-column :label="$t(`m.grading['管理空间']`)">
                      <template slot-scope="{ row }">
                        <span
                          :title="row.role && row.role.name ? row.role.name : ''"
                        >
                          {{ row.role ? row.role.name : '--' }}
                        </span>
                      </template>
                    </bk-table-column>
                    <bk-table-column :label="$t(`m.levelSpace['管理员']`)" width="300">
                      <template slot-scope="{ row, $index }">
                        <iam-edit-member-selector
                          mode="detail"
                          field="role_members"
                          width="300"
                          :placeholder="$t(`m.verify['请输入']`)"
                          :value="row.role_members"
                          :index="$index"
                        />
                      </template>
                    </bk-table-column>
                    <template slot="empty">
                      <ExceptionEmpty />
                    </template>
                  </bk-table>
                  <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.permApply['请选择用户组']`) }}</p>
                </div>
                <div class="applicationPeriod">
                  <render-horizontal-block ext-cls="expired-at-wrapper" :label="$t(`m.common['申请期限']`)" :required="true">
                    <section ref="expiredAtRef">
                      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
                      <p class="expired-at-error" v-if="isShowExpiredError">{{ $t(`m.permApply['请选择申请期限']`) }}</p>
                    </section>
                  </render-horizontal-block>
                </div>
                <div class="reason">
                  <render-horizontal-block ext-cls="reason-wrapper" :label="$t(`m.common['理由']`)" :required="true">
                    <section ref="resInstanceReasonRef">
                      <bk-input
                        type="textarea"
                        v-model="reason"
                        :maxlength="255"
                        :placeholder="$t(`m.verify['请输入']`)"
                        :ext-cls="isShowReasonError ? 'perm-apply-reason-error' : ''"
                        @input="handleReasonInput"
                        @blur="handleReasonBlur">
                      </bk-input>
                      <p class="reason-empty-wrapper" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
                    </section>
                  </render-horizontal-block>
                </div>
                <div class="buttonBox">
                  <bk-button
                    theme="primary"
                    :loading="buttonLoading"
                    @click="handleSubmit">
                    {{ $t(`m.common['提交']`) }}
                  </bk-button>
                  <bk-button
                    style="margin-left: 10px;"
                    @click="handleCancel">
                    {{ $t(`m.common['取消']`) }}
                  </bk-button>
                </div>
              </div>
            </bk-transition>
          </div>
        </render-horizontal-block>
      </div>
      <div class="IndependentApplication" v-if="isShowIndependent">
        <render-horizontal-block>
          <div class="independent">
            <div class="requestRecommendText pl20">
              {{$t(`m.permApply['以下是你必须申请的权限']`)}}
            </div>
            <div class="info">
              {{ $t(`m.info['如果需要更多自定义权限']`) }}{{ $t(`m.common['，']`) }}
              {{ $t(`m.info['可前往']`) }}
              <bk-button
                text
                theme="primary"
                style="font-size: 12px;"
                @click="handleToCustompermissions">
                {{ $t(`m.info['申请自定义权限']`) }}
              </bk-button>
            </div>
          </div>
          <div>
            <bk-transition name="bk-fade-in-ease">
              <div>
                <div
                  ref="instanceTableRef"
                  class="tableData"
                >
                  <resource-instance-table
                    :list="newTableList"
                    :original-table-list="tableDataBackup"
                    :system-id="systemValue"
                    :system-list="systemList"
                    ref="resInstanceTableRef"
                    @on-select="handleResourceSelect"
                    @on-realted-change="handleRelatedChange" />
                </div>

                <div class="requestRecommendText">{{$t(`m.permApply['以下相关权限，你可以按需申请']`)}}</div>
                <div
                  ref="instanceTableRef"
                  class="tableData"
                >
                  <resource-instance-table
                    :is-recommend="isRecommend"
                    :cache-id="routerQuery.cache_id"
                    :list="newRecommendTableList"
                    :original-table-list="tableRecommendDataBackup"
                    :system-id="systemValue"
                    :system-list="systemList"
                    ref="resInstanceRecommendTableRef"
                    @on-select="handleResourceSelect"
                    @on-realted-change="handleRelatedChange" />
                </div>
                <div class="reason">
                  <render-horizontal-block ext-cls="reason-wrapper" :label="$t(`m.common['理由']`)" :required="true">
                    <section ref="resInstanceReasonRef">
                      <bk-input
                        type="textarea"
                        v-model="reason"
                        :maxlength="255"
                        :placeholder="$t(`m.verify['请输入']`)"
                        :ext-cls="isShowReasonError ? 'perm-apply-reason-error' : ''"
                        @input="handleReasonInput"
                        @blur="handleReasonBlur">
                      </bk-input>
                      <p class="reason-empty-wrapper" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
                    </section>
                  </render-horizontal-block>
                </div>
                <div class="buttonBox">
                  <bk-button
                    theme="primary"
                    :loading="buttonLoading"
                    @click="handleApplySubmit">
                    {{ $t(`m.common['提交']`) }}
                  </bk-button>
                  <bk-button
                    style="margin-left: 10px;"
                    @click="handleCancel">
                    {{ $t(`m.common['取消']`) }}
                  </bk-button>
                </div>
              </div>
            </bk-transition>
          </div>
        </render-horizontal-block>
      </div>
    </smart-action>
    <!-- 无权限组时页面 -->
    <smart-action class="noPermissionPage blueBorder" v-if="isNoPermissionsSet && !isShowHasUserGroup ">
      <render-horizontal-block>
        <div class="tableData">
          <bk-alert type="info">
            <div slot="title">
              {{ $t(`m.info['没有匹配到合适的用户组']`) }}{{ $t(`m.common['，']`) }}
              {{ $t(`m.info['如需要可继续前往']`) }}
              <bk-button
                text
                theme="primary"
                style="font-size: 12px;"
                @click="handleToUserGroup">
                {{ $t(`m.info['申请用户组权限']`) }}
              </bk-button>
            </div>
          </bk-alert>
        </div>
        <div class="requestIndependent">
          <div class="requestIndependentText">{{$t(`m.permApply['以下是你必须申请的权限']`)}}</div>
          <div class="info">
            {{ $t(`m.info['如果需要更多自定义权限']`) }}{{ $t(`m.common['，']`) }}
            {{ $t(`m.info['可前往']`) }}
            <bk-button
              text
              theme="primary"
              style="font-size: 12px;"
              @click="handleToCustompermissions">
              {{ $t(`m.info['申请自定义权限']`) }}
            </bk-button>
          </div>
        </div>
        <div
          ref="instanceTableRef"
          class="tableData"
        >
          <resource-instance-table
            :has-system="true"
            :is-no-perm-page="true"
            :cache-id="routerQuery.cache_id"
            :list="newTableList"
            :original-table-list="tableDataBackup"
            :system-id="systemValue"
            :system-list="systemList"
            ref="resInstanceTableRef"
            @on-select="handleResourceSelect"
            @on-realted-change="handleRelatedChange" />
        </div>

        <div class="requestRecommendText">{{$t(`m.permApply['以下相关权限，你可以按需申请']`)}}</div>
        <div
          ref="instanceTableRef"
          class="tableData"
        >
          <resource-instance-table
            :has-system="true"
            :is-no-perm-page="true"
            :is-recommend="isRecommend"
            :cache-id="routerQuery.cache_id"
            :list="newRecommendTableList"
            :original-table-list="tableRecommendDataBackup"
            :system-id="systemValue"
            :system-list="systemList"
            ref="resInstanceRecommendTableRef"
            @on-select="handleResourceSelect"
            @on-realted-change="handleRelatedChange" />
        </div>
        <div class="reason">
          <render-horizontal-block ext-cls="reason-wrapper" :label="$t(`m.common['理由']`)" :required="true">
            <section ref="resInstanceReasonRef">
              <bk-input
                type="textarea"
                v-model="reason"
                :maxlength="255"
                :placeholder="$t(`m.verify['请输入']`)"
                :ext-cls="isShowReasonError ? 'perm-apply-reason-error' : ''"
                @input="handleReasonInput"
                @blur="handleReasonBlur">
              </bk-input>
              <p class="reason-empty-wrapper" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
            </section>
          </render-horizontal-block>
        </div>
        <div class="buttonBox">
          <bk-button
            theme="primary"
            :loading="buttonLoading"
            @click="handleApplySubmit">
            {{ $t(`m.common['提交']`) }}
          </bk-button>
          <bk-button
            style="margin-left: 10px;"
            @click="handleCancel">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </render-horizontal-block>
    </smart-action>
    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      :show-member="false"
      @animation-end="handleAnimationEnd" />

    <confirmDialog
      :width="600"
      :show.sync="isShowConfirmDialog"
      :title="confirmDialogTitle"
      :is-custom-style="true"
      @on-cancel="isShowConfirmDialog = false"
      @on-sumbit="isShowConfirmDialog = false"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { guid, formatCodeData } from '@/common/util';
  import { PERMANENT_TIMESTAMP, AGGREGATION_EDIT_ENUM } from '@/common/constants';
  import { bus } from '@/common/bus';
  import { buildURLParams } from '@/common/url';
  import RenderActionTag from '@/components/common-action';
  import ResourceInstanceTable from '../components/resource-instance-table';
  import Policy from '@/model/policy';
  import AggregationPolicy from '@/model/aggregation-policy';
  import Condition from '@/model/condition';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider';
  import BkUserSelector from '@blueking/user-selector';
  import ConfirmDialog from '@/components/iam-confirm-dialog/index';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';

  export default {
    components: {
      RenderActionTag,
      ResourceInstanceTable,
      IamDeadline,
      RenderPermSideslider,
      BkUserSelector,
      ConfirmDialog,
      IamEditMemberSelector
    },
    data () {
      return {
        AGGREGATION_EDIT_ENUM,
        userApi: window.BK_USER_API,
        enableGroupInstanceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true',
        systemValue: '',
        systemList: [],
        buttonLoading: false,
        originalCustomTmplList: [],
        originalCustomTmplListBackup: [],
        containerNode: null,
        tableData: [],
        tableDataBackup: [],
        reason: '',
        isShowActionError: false,
        isShowReasonError: false,
        routerQuery: {},
        linearActionList: [],
        requestQueue: ['action', 'policy', 'aggregate', 'commonAction'],
        isAllExpanded: false,
        isAllUnlimited: false,
        aggregationMap: [],
        aggregations: [],
        aggregationsBackup: [],
        aggregationsTableData: [],
        commonActions: [],
        actionSearchValue: '',
        // 用户组列表数据
        tableList: [],
        isShowPermSidesilder: false,
        curGroupName: '',
        curGroupId: '',
        isShowUserGroup: true,
        isShowIndependent: false,
        isShowExpiredError: false,
        isShowGroupError: false,
        isShowHasUserGroup: false,
        isShowMemberError: false,
        sliderLoading: false,
        currentSelectList: [],
        curUserGroup: [],
        expiredAt: 15552000,
        expiredAtUse: 15552000,
        // 默认按钮选中
        checkRadio: 'userGroup',
        tableLoading: false,
        gradeMembers: [],
        // route.query 里的 tid 参数改变名字为 cache_id
        sysAndtid: false,
        routerValue: {},
        newTableList: [],
        newRecommendTableList: [],
        tableRecommendData: [],
        tableRecommendDataBackup: [],
        aggregationsTableRecommendData: [],
        isRecommend: true,
        tagActionList: [],
        tabData: [
          { title: this.$t(`m.permApply['用户组推荐']`), desc: this.$t(`m.permApply['包含更大范围的权限（运维\开发\测试等角色类权限）']`), key: 'userGroup' },
          { title: this.$t(`m.permApply['细粒度权限']`), desc: this.$t(`m.permApply['只包含当前需要的最小范围权限']`), key: 'independent' }
        ],
        tabIndex: 0,
        hoverId: -1,
        hoverActionData: {
          actions: []
        },
        // permMembers: [{ username: 'poloohuang', readonly: false }, { username: 'gc_lihao', readonly: false }].map(item => item.username)
        permMembers: [],
        personalUserGroup: [],
        emptyData: {
          type: 'search-empty',
          text: '搜索结果为空',
          tip: '',
          tipType: 'search'
        },
        isShowConfirmDialog: false,
        confirmDialogTitle: this.$t(`m.verify['admin无需申请权限']`)
      };
    },
    computed: {
        ...mapGetters(['user', 'externalSystemId']),
        // 是否无权限申请
        isNoPermApply () {
            return this.routerQuery.system_id;
        },
        // 无权限组时
        isNoPermissionsSet () {
            return this.routerQuery.cache_id;
        },
        isShowGroupTitle () {
            return (item) => {
              const isExistActions = item.actions && item.actions.length > 0;
                const isExistSubGroup = (item.sub_groups || []).some(v =>
                (v.sub_groups && v.sub_groups.length > 0)
                 || (v.actions && v.actions.length > 0)
                 );
              return isExistSubGroup || isExistActions;
            };
        },
        isShowGroupAction () {
            return (item) => {
                const isExistSubGroup = (item.sub_groups || []).some(v => v.sub_groups && v.sub_groups.length > 0);
                return item.sub_groups && item.sub_groups.length > 0 && !isExistSubGroup;
            };
        },
        isShowGroupSubAction () {
            return (item) => {
              const isExistSubGroup = (item.sub_groups || []).some(v =>
                (v.sub_groups && v.sub_groups.length > 0)
                 || (v.actions && v.actions.length > 0)
                 );
              return item.sub_groups && item.sub_groups.length > 0 && isExistSubGroup;
            };
        },
        customLoading () {
            return this.requestQueue.length > 0;
        },
        isAggregateDisabled () {
            const isDisabled = this.tableData.length < 1 || this.aggregations.length < 1
            || (this.tableData.length === 1 && !this.tableData[0].isAggregate);
            return isDisabled;
        },
        isUnlimitedDisabled () {
          const isDisabled = this.tableData.every(item =>
           ((!item.resource_groups || (item.resource_groups && !item.resource_groups.length)) && !item.instances)
           );
           if (isDisabled) {
            this.isAllUnlimited = false;
           }
          return isDisabled;
        },
        curSelectActions () {
            const allActionIds = [];
            this.originalCustomTmplList.forEach(payload => {
              if (!payload.actionsAllDisabled) {
                payload.actions.forEach(item => {
                    if (item.checked) {
                        allActionIds.push(item.id);
                    }
                });
                (payload.sub_groups || []).forEach(subItem => {
                    (subItem.actions || []).forEach(act => {
                        if (act.checked) {
                            allActionIds.push(act.id);
                        }
                    });
                });
              }
            });
            return allActionIds;
        }
    },
    watch: {
      '$route': {
        handler (value) {
          // value.query.system_id = 'bk_job';
          // value.query.cache_id = 'f3419dba47964a6b8a3e7467ff685b5e';
          if (value.query.system_id && value.query.cache_id) {
            const { system_id, cache_id } = value.query;
            this.routerQuery = Object.assign({}, {
              system_id,
              cache_id
            });
            this.sysAndtid = true;
          } else {
            this.routerQuery = Object.assign({}, {
              system_id: '',
              cache_id: ''
            });
            this.sysAndtid = false;
          }
          if (value.query.tab_key) {
            this.handleTabChange(value.query.tab_key);
          }
        },
        immediate: true
      },
      reason (value) {
        this.isShowReasonError = false;
      },
      curSelectActions (value) {
        this.aggregationsTableData = this.aggregationsTableData.filter(item => value.includes(item.id));
        // 监听新增或移除的操作，重新组装数据
        this.getFilterAggregateAction();
        // 这里是为了处理无限制和无资源实例后台都是空数据的情况，所以为了兼容编辑回显状态下为空的数据，首次加载不需要调用批量无限制
        if (this.isAllUnlimited) {
          this.handleUnlimitedActionChange(this.isAllUnlimited);
        }
      },
      tableData: {
        handler (value) {
          this.tagActionList = value.map(e => e.id);
          if (value.filter(item => item.isAggregate).length < 1) {
            this.isAllExpanded = false;
          }
          if (this.isDisabled && this.isAllUnlimited) {
            this.isAllUnlimited = false;
          }
        },
        deep: true
      },
      actionSearchValue (newVal, oldValue) {
        if (newVal === '' && oldValue !== '' && this.isActionsFilter) {
          this.isActionsFilter = false;
          this.originalCustomTmplList = _.cloneDeep(this.originalCustomTmplListBackup);
          this.handleActionLinearData(true);
        }
      }
    },
    created () {
      this.navStick = true;
      // 判断数组是否被另外一个数组包含
      this.isArrayInclude = (target, origin) => {
        const itemAry = [];
        target.forEach(function (p1) {
          if (origin.indexOf(p1) !== -1) {
            itemAry.push(p1);
          }
        });
        if (itemAry.length === target.length) {
          return true;
        }
        return false;
      };
      this.isActionsFilter = false;
      this.permMembers = [this.user.username];
    },
    methods: {
      handleView (payload) {
        this.curGroupName = payload.name;
        this.curGroupId = payload.id;
        this.isShowPermSidesilder = true;
      },
      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSidesilder = false;
      },
      handleToUserGroup () {
        this.$router.push({
          name: 'applyJoinUserGroup'
        });
      },
      handleToCustompermissions () {
        this.$router.push({
          name: 'applyCustomPerm'
        });
      },
      handlerOneChange (selection, row) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },
      handlerAllChange (selection) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },
      handleCellAttributes ({ rowIndex, cellIndex, row, column }) {
        if (cellIndex === 0) {
          if (this.curUserGroup.includes(row.id.toString())) {
            return {
              title: this.$t(`m.info['你已加入该组']`)
            };
          }
          return {};
        }
        return {};
      },
      handleRtxFocus () {
        this.isShowMemberError = false;
      },

      handleRtxBlur () {
        this.isShowMemberError = this.permMembers.length < 1;
      },

      handleRtxChange (payload) {
        this.isShowMemberError = false;
        this.permMembers = [...payload];
      },
      setDefaultSelect (payload) {
        return !this.curUserGroup.includes(payload.id.toString());
      },
      // 用户组数据
      async fetchUserGroupList () {
        this.tableLoading = true;
        const params = {
          cache_id: this.routerQuery.cache_id,
          apply_disable: false
        };
        try {
          const res = await this.$store.dispatch('userGroup/getUserGroupList', params);
          if (res.data.count > 0) {
            this.isShowHasUserGroup = true;
          }
          // 处理用户组权限申请默认页面场景下ENABLE_GROUP_INSTANCE_SEARCH为false需要展示FunctionalDependency组件
          if (this.isNoPermissionsSet && this.isShowHasUserGroup && !this.enableGroupInstanceSearch) {
            bus.$emit('show-function-dependency', {
              routeName: this.$route.name,
              show: true
            });
          }
          this.tableList.splice(0, this.tableList.length, ...(res.data.results || []));
          this.$nextTick(() => {
            this.tableList.forEach(item => {
              if (item.role_members && item.role_members.length) {
                const hasName = item.role_members.some((v) => v.username);
                if (!hasName) {
                  item.role_members = item.role_members.map(v => {
                    return {
                      username: v,
                      readonly: false
                    };
                  });
                }
              }
              if (this.personalUserGroup.length) {
                const hasSelected = this.personalUserGroup.find((v) => String(v.id) === String(item.id));
                if (hasSelected) {
                  this.$set(item, 'expired_at', hasSelected.expired_at);
                  this.$set(item, 'expired_at_display', hasSelected.expired_at_display);
                  this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
                }
              }
            });
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },
      async fetchCurUserGroup () {
        try {
          const { data } = await this.$store.dispatch('perm/getPersonalGroups', {
            page_size: 1000,
            page: 1
          });
          if (data.results && data.results.length) {
            this.curUserGroup = data.results.filter(item => item.department_id === 0).map(item => item.id);
            this.personalUserGroup = data.results.filter(item => item.department_id === 0);
          }
        } catch (e) {
          this.$emit('toggle-loading', false);
          console.error(e);
          this.messageAdvancedError(e);
        }
      },
      /**
       * 获取页面数据
       */
      // async fetchPageData () {
      //     await this.fetchSystems();
      //     if (this.systemValue) {
      //         await Promise.all([
      //             this.fetchPolicies(this.systemValue),
      //             this.fetchAggregationAction(this.systemValue),
      //             this.fetchCommonActions(this.systemValue)
      //         ]);
      //     }
      //     if (this.sysAndtid) {
      //         await Promise.all([
      //             // 获取用户组数据
      //             this.fetchUserGroupList(),
      //             // 获取个人用户的用户组列表
      //             this.fetchCurUserGroup(),
      //             // 获取推荐操作
      //             this.fetchRecommended()
      //         ]);
      //     }
      // },
      async fetchPageData () {
        await this.fetchSystems();
        if (this.systemValue) {
          await this.fetchPolicies(this.systemValue);
          await this.fetchAggregationAction(this.systemValue);
          await this.fetchCommonActions(this.systemValue);
        }
        if (this.sysAndtid) {
          // 获取个人用户的用户组列表
          await this.fetchCurUserGroup();
          // 获取用户组数据
          await this.fetchUserGroupList();
          // 获取推荐操作
          await this.fetchRecommended();
        }
      },

      // 获取推荐操作
      async fetchRecommended () {
        const params = {
          system_id: this.routerQuery.system_id,
          cache_id: this.routerQuery.cache_id
        };
        try {
          const res = await this.$store.dispatch('perm/getRecommended', params);
          // 常用操作需要过滤掉需要隐藏的操作
          const recommendActions = res.data.actions.filter((item) => !item.hidden) || [];
          const recommendPolicies = res.data.policies || [];
          const data = recommendActions.map(item => {
            const resourceGroups = recommendPolicies.find(sub => sub.id === item.id);
            if (resourceGroups) {
              resourceGroups.resource_groups.map(v => {
                v.related_resource_types.forEach(e => {
                  e.id = e.type;
                });
                return v;
              });
            }
            item.resource_groups = resourceGroups && resourceGroups.resource_groups
              ? resourceGroups.resource_groups : [];
            if (!item.resource_groups || !item.resource_groups.length) {
              item.resource_groups = item.related_resource_types.length ? [{ id: '', related_resource_types: item.related_resource_types }] : [];
            }
            return new Policy(
              {
                ...item,
                tag: 'add',
                isNoPermApplyPage: !!(this.routerQuery.cache_id && !this.isShowHasUserGroup)
              },
              'custom'
            );
          });
          this.tableRecommendData = data;
          this.tableRecommendData.forEach(item => {
            item.expired_at = 1627616000;

            // 无权限跳转过来, 新增的操作过期时间为 0 即小于 user.timestamp 时，expired_at 就设置为六个月 15552000
            if (item.tag === 'add') {
              if (item.expired_at <= this.user.timestamp) {
                item.expired_at = 15552000;
              }
            } else {
              // 新增的权限不判断是否过期
              if (item.expired_at <= this.user.timestamp) {
                item.isShowRenewal = true;
                item.isExpired = true;
              }
            }
          });
          this.newRecommendTableList = _.cloneDeep(this.tableRecommendData.filter(item => {
            return !item.isExpiredAtDisabled;
          }));
          this.tableRecommendDataBackup = _.cloneDeep(this.tableRecommendData);
          this.aggregationsTableRecommendData = _.cloneDeep(this.tableRecommendData);
        } catch (e) {
          this.$emit('toggle-loading', false);
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },

      getRelatedActionTips (payload) {
        const relatedActions = this.linearActionList.filter(item => payload.includes(item.id));
        return `${this.$t(`m.common['依赖操作']`)}: ${relatedActions.map(item => item.name).join('，')}`;
      },

      handleRelatedActions (payload, flag) {
        this.originalCustomTmplList.forEach((item, index) => {
          item.actions.forEach(act => {
            if (!act.disabled) {
              if (payload.related_actions.includes(act.id) && flag && !act.checked) {
                act.checked = true;
                this.setTableDataByRelated(act, true, item);
              }
              if (act.related_actions.includes(payload.id) && !flag && act.checked) {
                act.checked = false;
                this.setTableDataByRelated(act, false, item);
              }
            }
          })
          ;(item.sub_groups || []).forEach(sub => {
            sub.actions.forEach(act => {
              if (!act.disabled) {
                if (payload.related_actions.includes(act.id) && flag) {
                  act.checked = true;
                  this.setTableDataByRelated(act, true, item);
                }
                if (act.related_actions.includes(payload.id) && !flag) {
                  act.checked = false;
                  this.setTableDataByRelated(act, false, item);
                }
              }
            });
            const isSubAllChecked = sub.actions.every(v => v.checked);
            sub.allChecked = isSubAllChecked;
          });
          const isAllChecked = item.actions.every(v => v.checked);
          item.allChecked = isAllChecked;
          if (item.sub_groups && item.sub_groups.length > 0) {
            item.actionsAllChecked = isAllChecked && item.sub_groups.every(v => v.allChecked);
          } else {
            item.actionsAllChecked = isAllChecked;
          }
        });
      },

      setTableDataByRelated (payload, flag, item) {
        // 操作表格数据前需判断其是否已经存在
        const isExist = this.tableData.some(item => {
          return item.id === payload.id
            || (item.isAggregate && item.actions.map(_ => _.id).includes(payload.id));
        });
        if (flag) {
          if (!isExist) {
            ++item.count;
            if (!payload.resource_groups || !payload.resource_groups.length) {
              payload.resource_groups = payload.related_resource_types.length ? [{ id: '', related_resource_types: payload.related_resource_types }] : [];
            }
            this.tableData.unshift(new Policy({ ...payload, tag: 'add' }, 'custom'));
          }
        } else {
          if (isExist) {
            const index = this.tableData.findIndex(item => item.id === payload.id);
            if (index > -1) {
              this.tableData.splice(index, 1);
              --item.count;
            } else {
              this.tableData.forEach(item => {
                if (item.isAggregate) {
                  if (item.actions.map(_ => _.id).includes(payload.id)) {
                    item.actions = item.actions.filter(act => act.id !== payload.id);
                    --item.count;
                  }
                }
              });
              this.tableData = this.tableData.filter(
                item => !item.isAggregate || (item.isAggregate && item.actions.length > 0)
              );
            }
          }
        }
      },

      handleActionSearch (value) {
        const keyword = value.trim();
        if (keyword === '') {
          return;
        }
        this.isActionsFilter = true;
        this.emptyData = formatCodeData(0, Object.assign(this.emptyData, { tipType: 'search' }));
        let tempList = [];
        this.originalCustomTmplListBackup.forEach(item => {
          let tempAction = [];
          const tempSubGroups = [];
          if (item.actions && item.actions.length > 0) {
            tempAction = item.actions.filter(act => act.name.indexOf(keyword) > -1);
          }
          if (item.sub_groups && item.sub_groups.length > 0) {
            item.sub_groups.forEach(sub => {
              const temps = sub.actions.filter(act => act.name.indexOf(keyword) > -1);
              tempSubGroups.push({
                actions: temps,
                name: sub.name
              });
            });
          }
          tempList.push({
            name: item.name,
            actions: tempAction,
            sub_groups: tempSubGroups.filter(item => item.actions.length > 0)
          });
        });
        tempList = tempList.filter(item => item.actions.length > 0 || item.sub_groups.length > 0);
        this.originalCustomTmplList = _.cloneDeep(tempList);
        this.handleActionLinearData(true);
      },

      handleEmptyClear () {
        this.actionSearchValue = '';
        this.emptyData.tipType = '';
      },

      handleEmptyRefresh () {
        this.fetchPageData();
      },

      /**
       * 获取系统对应的常用操作
       *
       * @param {String} systemId 系统id
       */
      async fetchCommonActions (systemId) {
        try {
          const res = await this.$store.dispatch('permApply/getUserCommonAction', { systemId });
          this.commonActions.splice(0, this.commonActions.length, ...(res.data || []));
          this.commonActions.forEach(item => {
            item.$id = guid();
          });
          if (this.commonActions.length > 0) {
            if (this.originalCustomTmplList.length > 1) {
              this.originalCustomTmplList.forEach((item, index) => {
                item.expanded = index < 1;
              });
            }
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },
      handleActionTagChange (flag, payload) {
        if (payload.length < 1 || this.originalCustomTmplList.length < 1) {
          return;
        }
        this.handleActionMatchChecked(flag, payload);
        // 默认权限不能改变，所以不能参与匹配
        const temps = [];
        payload.forEach(item => {
          const data = this.linearActionList.find(act => act.id === item);
          if (!data.disabled) {
            temps.push(item);
          }
        });
        if (flag) {
          const differenceSetIds = temps.filter(v => !this.tableData.map(sub => sub.id).includes(v));
          differenceSetIds.forEach(v => {
            const data = this.linearActionList.find(act => act.id === v);
            if (!data.resource_groups || !data.resource_groups.length) {
              data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
            }
            this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom'));
          });
        } else {
          this.tableData = this.tableData.filter(v => !temps.includes(v.id));
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !temps.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 1));
        }
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleActionTagEnter (payload) {
        this.hoverActionData = payload;
      },

      handleActionTagLeave (payload) {
        this.hoverActionData = Object.assign(payload, { actions: [] });
      },

      handleFormatTitleHover (payload) {
        let subGroupId = [];
        const originIds = payload.actions.map(item => item.id);
        payload.sub_groups.forEach(item => {
          item.actions.forEach((subItem) => {
            subGroupId = [...new Set(subGroupId.concat(subItem.id))];
          });
        });
        const list = [...new Set(subGroupId.concat(originIds))];
        const result = this.hoverActionData.actions.filter(item => list.includes(item));
        return !!result.length;
      },

      handleActionMatchChecked (flag, payload) {
        this.originalCustomTmplList.forEach(item => {
          let allCheckedLen = 0;
          let count = 0;
          let delCount = 0;
          item.actions.forEach(item => {
            if (!item.disabled) {
              if (payload.includes(item.id)) {
                if (!item.checked && flag) {
                  ++count;
                }
                if (item.checked && !flag) {
                  ++delCount;
                }
                item.checked = flag;
              }
            }
            if (item.disabled || item.checked) {
              allCheckedLen++;
            }
          });
          item.allChecked = allCheckedLen === item.actions.length

          ;(item.sub_groups || []).forEach(subItem => {
            let allSubCheckedLen = 0
            ;(subItem.actions || []).forEach(act => {
              if (!act.disabled) {
                if (payload.includes(act.id)) {
                  if (!act.checked && flag) {
                    ++count;
                  }
                  if (act.checked && !flag) {
                    ++delCount;
                  }
                  act.checked = flag;
                }
              }
              if (act.disabled || act.checked) {
                allSubCheckedLen++;
              }
            });
            subItem.allChecked = allSubCheckedLen === subItem.actions.length;
          });

          item.actionsAllChecked = item.actions.every(act => act.checked) && (item.sub_groups || []).every(
            v => {
              return v.actions.every(act => act.checked);
            });

          if (flag) {
            item.count = item.count + count;
          } else {
            item.count = item.count - delCount;
          }
        });
      },
      async fetchAggregationAction (payload) {
        try {
          const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: payload });
          if (res.data.aggregations.length < 1) {
            return;
          }
          // 过滤掉不存在当前系统下的操作
          const actionIds = [];
          this.originalCustomTmplList.forEach(item => {
            actionIds.push(...item.actions.map(_ => _.id));
            if (item.sub_groups && item.sub_groups.length > 0) {
              item.sub_groups.forEach(subItem => {
                actionIds.push(...subItem.actions.map(_ => _.id));
              });
            }
          });
          const aggregations = []
          ;(res.data.aggregations || []).forEach(item => {
            const { actions, aggregate_resource_types } = item;
            const curActions = actions.filter(_ => actionIds.includes(_.id));
            if (curActions.length > 0) {
              aggregations.push({
                actions: curActions,
                aggregate_resource_types
              });
            }
          });
          this.aggregationsBackup = _.cloneDeep(aggregations);
          this.aggregations = aggregations;
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },
      handleExpanded (payload) {
        if (this.originalCustomTmplList.length < 2) {
          return;
        }
        payload.expanded = !payload.expanded;
      },

      handleCheckAll (payload) {
        if (payload.actionsAllDisabled) {
          return;
        }
        const tempActionIds = [];
        const allActionIds = [];
        const tempActions = [];
        this.isShowActionError = false;
        payload.actionsAllChecked = !payload.actionsAllChecked;
        if (!payload.actions.every(v => v.disabled)) {
          payload.allChecked = payload.actionsAllChecked;
        }
        payload.actions.forEach(item => {
          if (!item.disabled) {
            item.checked = payload.actionsAllChecked;
            tempActionIds.push(item.id);
            tempActions.push(item);
          }
          allActionIds.push(item.id);
        })
        ;(payload.sub_groups || []).forEach(subItem => {
          subItem.actionsAllChecked = payload.actionsAllChecked;
          subItem.allChecked = payload.actionsAllChecked
          ;(subItem.actions || []).forEach(act => {
            if (!act.disabled) {
              act.checked = payload.actionsAllChecked;
              tempActionIds.push(act.id);
              tempActions.push(act);
            }
            allActionIds.push(act.id);
          });
        });

        if (!payload.actionsAllChecked) {
          const tempData = [];
          this.tableData.forEach(item => {
            if (!item.isAggregate && !tempActionIds.includes(item.id)) {
              tempData.push(item);
            }
            if (item.isAggregate && !this.isArrayInclude(item.actions.map(v => v.id), tempActionIds)) {
              tempData.push(item);
            }
          });
          this.tableData.splice(0, this.tableData.length, ...tempData);
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !tempActionIds.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 0));
        } else {
          const differenceSetIds = allActionIds.filter(v => !this.tableData.map(sub => sub.id).includes(v));
          differenceSetIds.forEach(v => {
            const data = this.linearActionList.find(act => act.id === v);
            if (!data.resource_groups || !data.resource_groups.length) {
              data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
            }
            this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom'));
          });
        }

        tempActions.forEach(item => {
          this.handleRelatedActions(item, payload.actionsAllChecked);
        });
        payload.count = payload.actionsAllChecked ? payload.allCount : 0;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleSubAllChange (newVal, oldVal, val, payload, item) {
        const tempActionIds = [];
        let count = 0;
        this.isShowActionError = false;
        payload.actions.forEach(item => {
          if (!item.disabled) {
            if (!item.checked && newVal) {
              ++count;
              ++item.hasAddCount;
            }
            item.checked = newVal;
            tempActionIds.push(item.id);
            this.handleRelatedActions(item, newVal);
          }
        });

        if (!newVal) {
          item.actionsAllChecked = false;
          const tempData = [];
          this.tableData.forEach(item => {
            if (!item.isAggregate && !tempActionIds.includes(item.id)) {
              tempData.push(item);
            }
            if (item.isAggregate && !this.isArrayInclude(item.actions.map(v => v.id), tempActionIds)) {
              tempData.push(item);
            }
          });
          this.tableData.splice(0, this.tableData.length, ...tempData);
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !tempActionIds.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 0));

          item.count = item.count - payload.actions.length;
          return;
        }

        item.actionsAllChecked = item.actions.every(act => act.checked) && item.sub_groups.every(v => {
          return v.actions.every(act => act.checked);
        });

        const differenceSetIds = payload.actions.map(v => v.id).filter(
          v => !this.tableData.map(sub => sub.id).includes(v)
        );
        differenceSetIds.forEach(v => {
          const data = this.linearActionList.find(act => act.id === v);
          if (!data.resource_groups || !data.resource_groups.length) {
            data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
          }
          this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom'));
        });

        item.count = item.count + count;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleAllChange (newVal, oldVal, val, payload) {
        const tempActionIds = [];
        let count = 0;
        this.isShowActionError = false;
        payload.actions.forEach(item => {
          if (!item.disabled) {
            if (!item.checked && newVal) {
              ++count;
              ++item.hasAddCount;
            }
            item.checked = newVal;
            tempActionIds.push(item.id);
          }
        });

        if (!newVal) {
          payload.actionsAllChecked = false;
          const tempData = [];
          this.tableData.forEach(item => {
            if (!item.isAggregate && !tempActionIds.includes(item.id)) {
              tempData.push(item);
            }
            if (item.isAggregate && !this.isArrayInclude(item.actions.map(v => v.id), tempActionIds)) {
              tempData.push(item);
            }
          });
          this.tableData.splice(0, this.tableData.length, ...tempData);
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              item.actions = item.actions.filter(v => !tempActionIds.includes(v.id));
            }
          });
          this.tableData = this.tableData.filter(item => !(item.isAggregate && item.actions.length < 0));

          payload.count = payload.count - payload.actions.length;
          return;
        }

        if (payload.sub_groups && payload.sub_groups.length > 0) {
          payload.actionsAllChecked = payload.sub_groups.every(v => {
            return v.actions.every(item => item.checked);
          });
        } else {
          payload.actionsAllChecked = true;
        }

        const differenceSetIds = payload.actions.map(v => v.id).filter(
          v => !this.tableData.map(sub => sub.id).includes(v)
        );
        differenceSetIds.forEach(item => {
          const data = this.linearActionList.find(act => act.id === item);
          if (!data.resource_groups || !data.resource_groups.length) {
            data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
          }
          this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom'));
        });

        payload.count = payload.count + count;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      /**
       * 获取选中的操作具有的分组
       */
      getFilterAggregateAction () {
        let aggregationAction = [];
        const curSelectActions = (() => {
          const tempAction = [];
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              tempAction.push(...item.actions.map(_ => _.id));
            } else {
              tempAction.push(item.id);
            }
          });
          return tempAction;
        })();
        this.aggregationsBackup.forEach((item, index) => {
          const tempObj = _.cloneDeep(item);
          const tempAction = tempObj.actions.map(_ => _.id);
          const intersection = [...new Set(tempAction.filter(v => curSelectActions.includes(v)))];
          if (intersection.length > 0) {
            tempObj.actions = tempObj.actions.filter(v => intersection.includes(v.id));
            aggregationAction.push(tempObj);
          }
        });
        aggregationAction = aggregationAction.filter(item => item.actions.length > 1);
        this.aggregations = _.cloneDeep(aggregationAction);
      },

      handleAggregateActionChange (payload) {
        this.getFilterAggregateAction();
        this.handleAggregateAction(payload);
        this.handleUnlimitedActionChange(this.isAllUnlimited);
      },

      handleUnlimitedActionChange (payload) {
        const tableData = _.cloneDeep(this.tableData);
        tableData.forEach((item, index) => {
          if (!item.isAggregate) {
            if (item.resource_groups && item.resource_groups.length) {
              item.resource_groups.forEach(groupItem => {
                groupItem.related_resource_types && groupItem.related_resource_types.forEach(types => {
                  if (!payload && (types.condition.length > 0 && types.condition[0] !== 'none')) {
                    return;
                  }
                  types.condition = payload ? [] : ['none'];
                  if (payload) {
                    types.isError = false;
                  }
                });
              });
            } else {
              item.name = item.name.split('，')[0];
            }
          }
          if (item.instances && item.isAggregate) {
            item.isNoLimited = false;
            item.isError = !(item.instances.length || (!item.instances.length && item.isNoLimited));
            item.isNeedNoLimited = true;
            if (!payload || item.instances.length) {
              item.isNoLimited = false;
              item.isError = false;
            }
            if ((!item.instances.length && !payload && item.isNoLimited) || payload) {
              item.isNoLimited = true;
              item.isError = false;
              item.instances = [];
            }
            return this.$set(
              tableData,
              index,
              new AggregationPolicy(item)
            );
          }
        });
        this.tableData = _.cloneDeep(tableData);
      },

      handleRelatedChange (payload) {
        this.aggregationsTableData = _.cloneDeep(payload);
      },

      handleResourceSelect (payload) {
        const curAction = payload.actions.map(item => item.id);
        const instances = (function () {
          const arr = [];
          payload.aggregateResourceType.forEach(resourceItem => {
            const { id, name, system_id } = resourceItem;
            payload.instancesDisplayData[id] && payload.instancesDisplayData[id].forEach(v => {
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
          });
          return arr;
        })();
        if (instances.length) {
          let selectPath = instances[0].path;
          this.aggregationsTableData.forEach(item => {
            if (curAction.includes(item.id)) {
              if (item.tag === 'unchanged') {
                item.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types
                    && groupItem.related_resource_types.forEach(subItem => {
                      subItem.condition.forEach(conditionItem => {
                        conditionItem.instance.forEach(instanceItem => {
                          if (instanceItem.type === instances[0].type) {
                            selectPath = selectPath.filter(v => {
                              const target = v.map(_ => `${_.type}${_.id}`).sort();
                              return instanceItem.path.map(pathItem => pathItem.map(v => `${v.type}${v.id}`).sort()).filter(pathSub => _.isEqual(target, pathSub)).length < 1;
                            });
                            if (selectPath.length > 0) {
                              instanceItem.path.push(...selectPath);
                              instanceItem.paths.push(...selectPath);
                            }
                          }
                        });
                      });
                    });
                });
              } else {
                item.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types
                    && groupItem.related_resource_types.forEach(subItem => {
                      subItem.condition = [new Condition({ instances }, '', 'add')];
                    });
                });
              }
            }
          });
        }
      },

      handleAggregateAction (payload) {
        this.isAllExpanded = payload;
        const aggregationAction = this.aggregations;
        const actionIds = [];
        aggregationAction.forEach(item => {
          actionIds.push(...item.actions.map(_ => _.id));
        });
        if (payload) {
          // 缓存新增加的操作权限数据
          aggregationAction.forEach(item => {
            const filterArray = this.tableData.filter(
              subItem => item.actions.map(_ => _.id).includes(subItem.id)
            );

            const addArray = _.cloneDeep(filterArray.filter(
              subItem => !this.aggregationsTableData.map(_ => _.id).includes(subItem.id)
            ));
            if (addArray.length > 0) {
              this.aggregationsTableData.push(...addArray);
            }
          });
          const aggregations = aggregationAction.filter(item => {
            const target = item.actions.map(v => v.id).sort();
            const existData = this.tableData.find(subItem => {
              return subItem.isAggregate && _.isEqual(target, subItem.actions.map(v => v.id).sort());
            });
            return !existData;
          }).map((item, index) => {
            const existTableData = this.aggregationsTableData.filter(
              subItem => item.actions.map(act => act.id).includes(subItem.id)
            );

            if (existTableData.length > 0) {
              item.tag = existTableData.every(subItem => subItem.tag === 'unchanged') ? 'unchanged' : 'add';
              const tempObj = existTableData.find(subItem => subItem.tag === 'add');
              if (tempObj) {
                item.expired_at = tempObj.expired_at || 15552000;
                item.expired_display = tempObj.expired_display || this.$t(`m.common['6个月']`);
              } else {
                item.expired_at = existTableData[0].expired_at || 15552000;
                item.expired_display = existTableData[0].expired_display || this.$t(`m.common['6个月']`);
              }
              if (item.tag === 'add') {
                const conditions = existTableData.map(
                  subItem => subItem.resource_groups && subItem.resource_groups.length
                    ? subItem.resource_groups[0].related_resource_types[0].condition : []
                );
                // 是否都选择了实例
                const isAllHasInstance = conditions.every(subItem => subItem[0] !== 'none'); // 这里可能有bug, 都设置了属性点击批量编辑时数据变了
                if (isAllHasInstance) {
                  const instances = conditions.map(subItem => subItem.map(v => v.instance || []));
                  let isAllEqual = true;
                  for (let i = 0; i < instances.length - 1; i++) {
                    if (!_.isEqual(instances[i], instances[i + 1])) {
                      isAllEqual = false;
                      break;
                    }
                  }
                  if (isAllEqual) {
                    // const instanceData = instances[0][0][0];
                    // if (instanceData && instanceData.path) {
                    //     item.instances = instanceData.path.map(pathItem => {
                    //         return {
                    //             id: pathItem[0].id,
                    //             name: pathItem[0].name
                    //         };
                    //     });
                    // }
                    const instanceData = instances[0][0];
                    item.instances = [];
                    instanceData && instanceData.map(pathItem => {
                      const instance = pathItem.path.map(e => {
                        return {
                          id: e[0].id,
                          name: e[0].name,
                          type: e[0].type
                        };
                      });
                      item.instances.push(...instance);
                    });
                    this.setInstancesDisplayData(item);
                  } else {
                    item.instances = [];
                  }
                } else {
                  item.instances = [];
                }
              }
            }
            return new AggregationPolicy(item);
          });
          this.tableData = this.tableData.filter(item => !actionIds.includes(item.id));
          this.tableData.unshift(...aggregations);
          return;
        }

        const aggregationData = [];
        const newTableData = [];
        this.tableData.forEach(item => {
          if (!item.isAggregate) {
            newTableData.push(item);
          } else {
            aggregationData.push(_.cloneDeep(item));
          }
        });
        this.tableData = _.cloneDeep(newTableData);
        const reallyActionIds = actionIds.filter(item => !this.tableData.map(v => v.id).includes(item));
        reallyActionIds.forEach(item => {
          // 优先从已有权限取值
          const curObj = this.aggregationsTableData.find(_ => _.id === item);
          if (curObj) {
            this.tableData.unshift(curObj);
          } else {
            const curAction = this.linearActionList.find(_ => _.id === item);
            const curAggregation = aggregationData.find(_ => _.actions.map(v => v.id).includes(item));
            this.tableData.unshift(new Policy({ ...curAction, tag: 'add' }, 'custom'));
            if (curAggregation && curAggregation.instances.length > 0) {
              const curData = this.tableData[0];
              const instances = (function () {
                const arr = [];
                const aggregateResourceType = curAggregation.aggregateResourceType;
                aggregateResourceType.forEach(aggregateResourceItem => {
                  const { id, name, system_id } = aggregateResourceItem;
                  curAggregation.instances.forEach(v => {
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
                });
                return arr;
              })();
              if (instances.length > 0) {
                curData.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types
                    && groupItem.related_resource_types.forEach(subItem => {
                      subItem.condition = [new Condition({ instances }, '', 'add')];
                    });
                });
              }
            }
          }
        });
      },

      // 设置InstancesDisplayData
      setInstancesDisplayData (data) {
        data.instancesDisplayData = data.instances.reduce((p, v) => {
          if (!p[v['type']]) {
            p[v['type']] = [];
          }
          p[v['type']].push({
            id: v.id,
            name: v.name
          });
          return p;
        }, {});
      },
            
      handleActionChecked (newVal, oldVal, val, actData, payload) {
        const data = this.linearActionList.find(item => item.id === actData.id);
        this.isShowActionError = false;
        if (!newVal) {
          payload.allChecked = false;
          payload.actionsAllChecked = false;

          const isExistIndex = this.tableData.findIndex(item => item.id === actData.id);
          isExistIndex !== -1 && this.tableData.splice(isExistIndex, 1);

          if (isExistIndex === -1) {
            for (let i = 0; i < this.tableData.length; i++) {
              const item = this.tableData[i];
              if (item.isAggregate) {
                for (let j = 0; j < item.actions.length; j++) {
                  const actionItem = item.actions[j];
                  if (actionItem.id === actData.id) {
                    item.actions.splice(j, 1);
                    if (item.actions.length === 1) {
                      const curAction = this.linearActionList.find(
                        _ => _.id === item.actions[0].id
                      );
                      const curData = new Policy({ ...curAction, tag: 'add' }, 'custom');
                      const instances = (function () {
                        const arr = [];
                        const aggregateResourceType = item.aggregateResourceType;
                        const { id, name, system_id } = aggregateResourceType;
                        item.instances.forEach(v => {
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
                      curData.expired_at = item.expired_at;
                      curData.expired_display = item.expired_display;
                      if (instances.length > 0) {
                        curData.resource_groups.forEach(groupItem => {
                          groupItem.related_resource_types
                            && groupItem.related_resource_types.forEach(subItem => {
                              subItem.condition = [new Condition({ instances }, '', 'add')];
                            });
                        });
                      }
                      this.tableData.splice(i, 1, curData);
                      break;
                    }
                    break;
                  }
                }
              }
            }
          }

          this.handleRelatedActions(actData, false);
          payload.count--;
          return;
        }
        payload.allChecked = payload.actions.every(item => item.checked);
        if (payload.sub_groups && payload.sub_groups.length > 0) {
          payload.actionsAllChecked = payload.allChecked && payload.sub_groups.every(v => {
            return v.actions.every(act => act.checked);
          });
        } else {
          payload.actionsAllChecked = payload.allChecked;
        }

        if (!data.resource_groups || !data.resource_groups.length) {
          data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
        }
        this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom'));

        this.handleRelatedActions(actData, true);
        payload.count++;

        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },

      handleSubActionChecked (newVal, oldVal, val, actData, payload, item) {
        const data = this.linearActionList.find(v => v.id === actData.id);
        this.isShowActionError = false;
        if (!newVal) {
          payload.allChecked = false;
          item.actionsAllChecked = false;

          const isExistIndex = this.tableData.findIndex(v => v.id === actData.id);
          isExistIndex !== -1 && this.tableData.splice(isExistIndex, 1);

          if (isExistIndex === -1) {
            for (let i = 0; i < this.tableData.length; i++) {
              const item = this.tableData[i];
              if (item.isAggregate) {
                for (let j = 0; j < item.actions.length; j++) {
                  const actionItem = item.actions[j];
                  if (actionItem.id === actData.id) {
                    item.actions.splice(j, 1);
                    if (item.actions.length === 1) {
                      const curAction = this.linearActionList.find(
                        _ => _.id === item.actions[0].id
                      );
                      const curData = new Policy({ ...curAction, tag: 'add' }, 'custom');
                      const instances = (function () {
                        const arr = [];
                        const aggregateResourceType = item.aggregateResourceType;
                        const { id, name, system_id } = aggregateResourceType;
                        item.instances.forEach(v => {
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
                      curData.expired_at = item.expired_at;
                      curData.expired_display = item.expired_display;
                      if (instances.length > 0) {
                        curData.resource_groups.forEach(groupItem => {
                          groupItem.related_resource_types
                            && groupItem.related_resource_types.forEach(subItem => {
                              subItem.condition = [new Condition({ instances }, '', 'add')];
                            });
                        });
                      }
                      this.tableData.splice(i, 1, curData);
                      break;
                    }
                    break;
                  }
                }
              }
            }
          }

          this.handleRelatedActions(actData, false);
          item.count--;
          return;
        }
        payload.allChecked = payload.actions.every(item => item.checked);

        item.actionsAllChecked = item.actions.every(act => act.checked) && item.sub_groups.every(v => {
          return v.actions.every(act => act.checked);
        });

        if (!data.resource_groups || !data.resource_groups.length) {
          data.resource_groups = data.related_resource_types.length ? [{ id: '', related_resource_types: data.related_resource_types }] : [];
        }
        this.tableData.unshift(new Policy({ ...data, tag: 'add' }, 'custom'));

        this.handleRelatedActions(actData, true);
        item.count++;
        if (this.isAllExpanded) {
          this.handleAggregateActionChange(false);
        }
      },
            
      /**
       *
       * @param {Boolean} setChecked
       * 此方法获取数据赋值给this.linearActionList
       */
      handleActionLinearData (setChecked = false) {
        const linearActions = [];
        const hasCheckedList = [];
        if (setChecked) {
          this.tableData.forEach(item => {
            if (item.isAggregate) {
              hasCheckedList.push(...item.actions.map(act => act.id));
            } else {
              hasCheckedList.push(item.id);
            }
          });
        }
        this.originalCustomTmplList.forEach((item, index) => {
          this.$set(item, 'expanded', index === 0);
          let allCount = 0;
          let count = 0;
          let hasCheckedCount = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          item.actions = item.actions.filter(v => !v.hidden);
          item.actions.forEach(act => {
            this.$set(act, 'checked', ['checked', 'readonly'].includes(act.tag) || hasCheckedList.includes(act.id));
            this.$set(act, 'disabled', act.tag === 'readonly');
            linearActions.push(act);
            if (act.checked) {
              ++count;
              if (['readonly'].includes(act.tag)) {
                ++hasCheckedCount;
              }
            }
          });
          allCount = allCount + item.actions.length;
          (item.sub_groups || []).forEach(sub => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions = sub.actions.filter(v => !v.hidden);
            sub.actions.forEach(act => {
              this.$set(act, 'checked', ['checked', 'readonly'].includes(act.tag) || hasCheckedList.includes(act.id));
              this.$set(act, 'disabled', act.tag === 'readonly');
              linearActions.push(act);
              if (act.checked) {
                ++count;
                if (['readonly'].includes(act.tag)) {
                  ++hasCheckedCount;
                }
              }
            });

            allCount = allCount + sub.actions.length;

            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });

          // 存在已选择的操作所在的分组未展开时，让其展开
          const isHasCheckedFlag = item.actions.some(act => act.checked && act.tag === 'checked')
            || (item.sub_groups || []).some(sub => sub.actions.some(act => act.checked && act.tag === 'checked'));
          if (index !== 0) {
            item.expanded = isHasCheckedFlag;
          }

          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
          this.$set(item, 'allCount', allCount);
          this.$set(item, 'count', count);
          this.$set(item, 'hasCheckedCount', hasCheckedCount);
          if (item.sub_groups && item.sub_groups.length > 0) {
            this.$set(item, 'actionsAllChecked', isAllChecked && item.sub_groups.every(v => v.allChecked));
            this.$set(item, 'actionsAllDisabled', isAllDisabled && item.sub_groups.every(v => {
              return v.actions.every(sub => sub.disabled);
            }));
          } else {
            this.$set(item, 'actionsAllChecked', isAllChecked);
            this.$set(item, 'actionsAllDisabled', isAllDisabled);
          }
        });

        this.linearActionList = _.cloneDeep(linearActions);
      },

      handleResetExpandedStatus () {
        // 面板收起时默认回到初始态只是第一个分类操作展开其它收起
        this.originalCustomTmplList.forEach((item, index) => {
          item.expanded = index === 0;
        });
      },

      /**
       * 获取系统列表
       */
      async fetchSystems () {
        if (this.routerQuery.system_id) {
          this.systemValue = this.routerQuery.system_id;
        }
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const res = await this.$store.dispatch('system/getSystems', params);
          (res.data || []).forEach(item => {
            item.displayName = `${item.name}(${item.id})`;
            item.is_favorite = item.is_favorite ? 1 : 0;
          });
          this.systemList = res.data || [];
          if (!this.systemValue) {
            if (this.systemList.length) {
              this.systemValue = this.systemList[0].id;
            } else {
              this.fetchResetData();
              this.requestQueue = [];
              return;
            }
          }
          await this.fetchActions(this.systemValue);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },
      handleClassComputed (payload) {
        return payload.checked ? payload.disabled ? 'has-obtained' : 'has-selected' : 'no-obtained';
      },

      /**
       * 获取系统下的权限列表
       *
       * @param {String} systemId 系统id
       * 此方法获取数据，继承处理赋值给this.tableData
       * this.linearActionList 在handleActionLinearData获取并处理
       */
      async fetchPolicies (systemId) {
        const params = {
          system_id: systemId
        };
        if (this.routerQuery.cache_id) {
          params.cache_id = this.routerQuery.cache_id;
        }
        try {
          const res = await this.$store.dispatch('permApply/getPolicies', params);
          // 无权限申请过滤需要隐藏的操作
          if (res.data && res.data.length > 0) {
            const allPolicyList = this.linearActionList.filter((v) => !v.hidden).map((item) => `${item.name}&${item.id}`);
            const result = res.data.filter((item) => allPolicyList.includes(`${item.name}&${item.id}`));
            const data = result.map(item => {
              let relatedActions = [];
              const findLinerActions = this.linearActionList.find(sub => sub.id === item.id);
              if (findLinerActions) {
                const { related_actions, related_environments } = findLinerActions;
                // eslint-disable-next-line camelcase
                relatedActions = [...related_actions];
                // eslint-disable-next-line camelcase
                item.related_environments = related_environments;
              }
              // 此处处理related_resource_types中value的赋值
              return new Policy({
                ...item,
                related_actions: relatedActions,
                tid: this.routerQuery.cache_id ? this.routerQuery.cache_id : '',
                isNoPermApplyPage: !!(this.routerQuery.cache_id && !this.isShowHasUserGroup)
              });
            });
            this.tableData = data || [];
            this.tableData.forEach(item => {
              // item.expired_at = 1627616000
  
              // 无权限跳转过来, 新增的操作过期时间为 0 即小于 user.timestamp 时，expired_at 就设置为六个月 15552000
              if (item.tag === 'add') {
                if (item.expired_at <= this.user.timestamp) {
                  item.expired_at = 15552000;
                }
              } else {
                // 新增的权限不判断是否过期
                if (item.expired_at <= this.user.timestamp) {
                  item.isShowRenewal = true;
                  item.isExpired = true;
                }
              }
  
              // // 新增的权限不判断是否过期
              // if (item.expired_at <= this.user.timestamp && item.tag !== 'add') {
              //     item.isShowRenewal = true
              //     item.isExpired = true
              //     // this.$set(item, 'isShowRenewal', true)
              //     // this.$set(item, 'isExpired', true)
              // }
            });
            this.newTableList = _.cloneDeep(this.tableData.filter(item => {
              return !item.isExpiredAtDisabled;
            }));
          }
          this.tableDataBackup = _.cloneDeep(this.tableData);
          this.aggregationsTableData = _.cloneDeep(this.tableData);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },

      /**
       * 获取系统对应的自定义操作
       *
       * @param {String} systemId 系统id
       * 执行handleActionLinearData方法
       */
      async fetchActions (systemId) {
        const params = {
          system_id: systemId,
          user_id: this.user.username
        };
        if (this.routerQuery.cache_id) {
          params.cache_id = this.routerQuery.cache_id;
        }
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const { code, data } = await this.$store.dispatch('permApply/getActions', params);
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
          this.originalCustomTmplListBackup = _.cloneDeep(data);
          this.originalCustomTmplList = _.cloneDeep(data);
          this.handleActionLinearData();
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          if (this.requestQueue.length > 0) {
            this.requestQueue.shift();
          }
        }
      },

      handleDisabledClick (payload) {
        const curPermData = this.tableData.find(item => item.id === payload.id);
        if (curPermData) {
          if (curPermData.isExistPermAnimation) {
            return;
          }
          curPermData.isExistPermAnimation = true;
          setTimeout(() => {
            curPermData.isExistPermAnimation = false;
          }, 1500);
        }
      },

      handleReasonInput (payload) {
        this.isShowReasonError = false;
      },

      handleReasonBlur (payload) {
        if (payload === '') {
          this.isShowReasonError = true;
        }
      },
      /**
       * 系统选择回调函数
       *
       * @param {String} 系统id
       * @param {Object} option
       */
      // async handleSysSelected (value, option) {
      //     // 切换系统时重置数据
      //     this.reason = '';
      //     this.isShowReasonError = false;
      //     this.isShowActionError = false;
      //     this.fetchResetData();
      //     await Promise.all([
      //         this.fetchActions(value),
      //         this.fetchPolicies(value),
      //         this.fetchAggregationAction(value),
      //         this.fetchCommonActions(value)
      //     ]);
      // },
      async handleSysSelected (value, option) {
        // 切换系统时重置数据
        this.reason = '';
        this.isShowReasonError = false;
        this.isShowActionError = false;
        this.fetchResetData();
        await this.fetchActions(value);
        await this.fetchPolicies(value);
        await this.fetchAggregationAction(value);
        await this.fetchCommonActions(value);
      },

      /**
       * 提交权限申请
       */
      async handleApplySubmit () {
        const tableData = this.$refs.resInstanceTableRef.handleGetValue();
        const { flag, aggregations } = tableData;
        let actions = tableData.actions;
        let recommendActions = [];
        let recommendFlag = false;
                
        if (this.$refs.resInstanceRecommendTableRef) {
          const tableRecommendData = this.$refs.resInstanceRecommendTableRef.handleGetValue();
          recommendActions = tableRecommendData.actions;
          recommendFlag = recommendActions.some((e, i) => {
            const newRecommendTableList = this.newRecommendTableList.find(item => item.id === e.id);
            return newRecommendTableList.resource_groups.some(v => {
              return v.related_resource_types.some(j => {
                return j.empty;
              });
            });
          });
        }
        actions = [...actions, ...recommendActions];
        this.isShowReasonError = !this.reason;
        if (recommendFlag || flag || this.isShowReasonError) {
          if (actions.length < 1 && aggregations.length < 1) {
            this.isShowActionError = true;
            if (this.$refs.selectActionRef) {
              this.scrollToLocation(this.$refs.selectActionRef);
              return;
            }
          }
          const tableRef = this.$refs.instanceTableRef;
          const reasonRef = this.$refs.resInstanceReasonRef;
          if (flag || recommendFlag) {
            this.scrollToLocation(tableRef);
            return;
          }
          if (this.isShowReasonError) {
            this.scrollToLocation(reasonRef);
            return;
          }
        }
        // if (!this.permMembers.length) {
        // this.isShowMemberError = true;
        // this.scrollToLocation(this.$refs.permRecipientRef);
        // return;
        // }
        const curSystem = this.systemList.find(item => item.id === this.systemValue);
        const params = {
          system: {
            id: this.systemValue,
            name: curSystem ? curSystem.name : ''
          },
          templates: [],
          actions,
          aggregations,
          reason: this.reason,
          usernames: this.permMembers
        };
        this.buttonLoading = true;
        try {
          await this.$store.dispatch('permApply/permApply', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          if (['admin'].includes(this.user.username)) {
            this.isShowConfirmDialog = true;
          } else {
            this.messageAdvancedError(e);
          }
        } finally {
          this.buttonLoading = false;
        }
      },

      handleSystemEnter (id) {
        this.hoverId = id;
      },

      handleSystemLeave () {
        this.hoverId = -1;
      },

      handleCollection (option) {
        const params = [option.id];
        const typeMap = {
          0: async () => {
            try {
              const { code } = await this.$store.dispatch('perm/updateCollectSystem', params);
              if (code === 0) {
                this.messageSuccess(this.$t(`m.pemApply['收藏成功']`), 3000);
                await this.fetchSystems();
              }
            } catch (e) {
              this.messageAdvancedError(e);
            }
          },
          1: async () => {
            try {
              const { code } = await this.$store.dispatch('perm/deleteCollectSystem', params);
              if (code === 0) {
                this.messageSuccess(this.$t(`m.pemApply['取消收藏成功']`), 3000);
                await this.fetchSystems();
              }
            } catch (e) {
              this.messageAdvancedError(e);
            }
          }
        };
        return typeMap[option.is_favorite]();
      },

      // 收藏置顶
      handleToggle () {
        // this.systemList = this.systemList.sort((pre, next) => {
        //   return next.is_favorite - pre.is_favorite;
        // });
      },
            
      // 申请期限逻辑
      handleDeadlineChange (payload) {
        if (payload) {
          this.isShowExpiredError = false;
        }
        if (payload !== PERMANENT_TIMESTAMP && payload) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex(item => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expiredAtUse = payload + nowSecond;
          return;
        }
        this.expiredAtUse = payload;
      },
      handleExpiredAt () {
        const nowTimestamp = +new Date() / 1000;
        const tempArr = String(nowTimestamp).split('');
        const dotIndex = tempArr.findIndex(item => item === '.');
        const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
        const expiredAt = this.expiredAtUse + nowSecond;
        return expiredAt;
      },
      // 用户组权限提交
      async handleSubmit () {
        if (!this.currentSelectList.length) {
          this.isShowGroupError = true;
          this.scrollToLocation(this.$refs.groupTableRef);
          return;
        }
        if (!this.reason) {
          this.isShowReasonError = true;
          this.scrollToLocation(this.$refs.reasonRef);
          return;
        }
        if (this.expiredAtUse === 0) {
          this.isShowExpiredError = true;
          this.scrollToLocation(this.$refs.expiredAtRef);
          return;
        }
        this.buttonLoading = true;
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const params = {
          expired_at: this.expiredAtUse,
          reason: this.reason,
          groups: this.currentSelectList.map(({ id, name, description }) => ({ id, name, description }))
        };
        try {
          await this.$store.dispatch('permApply/applyJoinGroup', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          const applyCount = this.personalUserGroup.length + this.currentSelectList.length;
          if (['admin'].includes(this.user.username)) {
            this.isShowConfirmDialog = true;
            return;
          }
          if (applyCount > 100) {
            this.messageAdvancedError(
              e,
              8000,
              3,
              this.$t(
                `m.info['已加入用户组数量 ， 新申请数量，总数超过上限：100，请减少申请或退出部分用户组后重试']`,
                { applyCount: this.personalUserGroup.length, newApplyCount: this.currentSelectList.length }
              ));
            return;
          }
          this.messageAdvancedError(e);
        } finally {
          this.buttonLoading = false;
        }
      },

      /**
       * 取消
       */
      handleCancel () {
        this.$router.push({
          name: 'applyJoinUserGroup'
        });
      },

      /**
       * 去续期
       */
      handleBatchRenewal () {
        this.$router.push({
          name: 'permRenewal',
          query: {
            tab: 'group'
          }
        });
      },

      /**
       * 点击tab
       */
      clickTab (i, key) {
        this.handleTabChange(key);
        this.tabIndex = i;
      },

      handleTabChange (key) {
        this.tabIndex = this.tabData.findIndex(item => item.key === key);
        if (this.tabIndex === -1) {
          this.tabIndex = 0;
          key = 'userGroup';
        }
        const tabMap = {
          userGroup: () => {
            this.isShowUserGroup = true;
            this.isShowIndependent = false;
          },
          independent: () => {
            this.isShowIndependent = true;
            this.isShowUserGroup = false;
          }
        };
        window.history.replaceState({}, '', `?${buildURLParams(Object.assign({}, this.$route.query, {
          tab_key: key
        }))}`);
        return tabMap[key]();
      },

      fetchResetData () {
        this.isAllExpanded = false;
        this.isAllUnlimited = false;
        this.sysAndtid = false;
        this.aggregationMap = [];
        this.aggregations = [];
        this.tableData = [];
        this.tableDataBackup = [];
        this.aggregationsBackup = [];
        this.aggregationsTableData = [];
        this.actionSearchValue = '';
        this.requestQueue = ['action', 'policy', 'aggregate', 'commonAction'];
      }
    }
  };
</script>
<style lang="postcss" scoped>
@import './index.css';
@import '@/css/mixins/manage-members-detail-slidesider.css';
@import '@/css/mixins/aggregate-action-group.css';
.action-hover {
  color: #3a84ff;
}

.iam-action-hover {
  background: #E7EFFE;
  color: #3a84ff;
}

.user-group-name-column {
  display: flex;
  align-items: center;
  .user-group-name {
    max-width: 200px;
    margin-right: 5px;
  }
}

.select-collection {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.apply-custom-switch {
  display: flex;
  align-items: center;
  &-item {
    &:not(&:last-of-type) {
      margin-left: 4px;
      margin-right: 16px;
    }
  }
}

/deep/ .bk-table-header-wrapper {
    .has-gutter {
        .is-first {
            .bk-form-checkbox  {
                display: none;
            }
        }
    }
}
</style>

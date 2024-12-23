/*
 * Tencent is pleased to support the open source community by making
 * 蓝鲸智云-权限中心(BlueKing-IAM) available.
 *
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 *
 * 蓝鲸智云-权限中心(BlueKing-IAM) is licensed under the MIT License.
 *
 * License for 蓝鲸智云-权限中心(BlueKing-IAM):
 *
 * ---------------------------------------------------
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 * to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
 * the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 * THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

import il8n from '@/language';

// 永久时间戳
export const PERMANENT_TIMESTAMP = 4102444800;

// 6个月时间戳
export const SIX_MONTH_TIMESTAMP = 15552000;

// 自定义权限的模板id
export const CUSTOM_PERM_TEMPLATE_ID = 0;

// 一天时间的时间戳
export const ONE_DAY_TIMESTAMP = 86400;

// 权限期限时间戳
export const DURATION_LIST = [2592000, 7776000, 15552000, 31104000, 4102444800, 3600, 10800, 21600, 43200, 86400];

// 全球各个时区
export const GLOBAL_TIME_ZONE = [
  { name: '(GMT-12:00) 国际换线时间', value: 'Etc/GMT+12' },
  { name: '(GMT-11:00) 中途岛时间', value: 'Pacific/Midway' },
  { name: '(GMT-10:00) 夏威夷时间', value: 'Pacific/Honolulu' },
  { name: '(GMT-09:00) 阿拉斯加州时间', value: 'US/Alaska' },
  { name: '(GMT-08:00) 太平洋时间（美国和加拿大）', value: 'America/Los_Angeles' },
  { name: '(GMT-07:00) 亚利桑那时间', value: 'US/Arizona' },
  { name: '(GMT-06:00) 萨斯喀彻温省时间', value: 'Canada/Saskatchewan' },
  { name: '(GMT-05:00) 印第安纳州（东部）时间', value: 'US/East-Indiana' },
  { name: '(GMT-04:00) 圣地亚哥时间', value: 'America/Santiago' },
  { name: '(GMT-03:00) 蒙得维的亚时间', value: 'America/Montevideo' },
  { name: '(GMT-02:00) 中大西洋时间', value: 'America/Noronha' },
  { name: '(GMT-01:00) 亚速尔群岛时间', value: 'Atlantic/Azores' },
  { name: '(GMT+00:00) 伦敦时间', value: 'Etc/Greenwich' },
  { name: '(GMT+01:00) 中西部非洲时间', value: 'Africa/Lagos' },
  { name: '(GMT+02:00) 温得和克时间', value: 'Africa/Windhoek' },
  { name: '(GMT+03:00) 德黑兰时间', value: 'Asia/Tehran' },
  { name: '(GMT+04:00) 喀布尔时间', value: 'Asia/Kabul' },
  { name: '(GMT+05:00) 叶卡捷琳堡时间', value: 'Asia/Yekaterinburg' },
  { name: '(GMT+06:00) 加德满都时间', value: 'Asia/Katmandu' },
  { name: '(GMT+07:00) 曼谷时间', value: 'Asia/Bangkok' },
  { name: '(GMT+08:00) 中国标准时间 - 北京', value: 'Asia/Shanghai' },
  { name: '(GMT+09:00) 东京时间', value: 'Asia/Tokyo' },
  { name: '(GMT+10:00) 布里斯班时间', value: 'Australia/Brisbane' },
  { name: '(GMT+11:00) 马加丹', value: 'Asia/Magadan' },
  { name: '(GMT+12:00) 堪察加半岛时间', value: 'Pacific/Fiji' },
  { name: '(GMT+13:00) 努库阿洛法时间', value: 'Pacific/Tongatapu' }
];

// 全球各个时区
export const GLOBAL_TIME_ZONE_ENUM = {
  'Etc/GMT+12': '(GMT-12:00)',
  'Pacific/Midway': '(GMT-11:00)',
  'Pacific/Honolulu': '(GMT-10:00)',
  'US/Alaska': '(GMT-09:00)',
  'America/Los_Angeles': '(GMT-08:00)',
  'US/Arizona': '(GMT-07:00)',
  'Canada/Saskatchewan': '(GMT-06:00)',
  'US/East-Indiana': '(GMT-05:00)',
  'America/Santiago': '(GMT-04:00)',
  'America/Montevideo': '(GMT-03:00)',
  'America/Noronha': '(GMT-02:00)',
  'Atlantic/Azores': '(GMT-01:00)',
  'Etc/Greenwich': '(GMT+00:00)',
  'Africa/Lagos': '(GMT+01:00)',
  'Africa/Windhoek': '(GMT+02:00)',
  'Asia/Tehran': '(GMT+03:00)',
  'Asia/Kabul': '(GMT+04:00)',
  'Asia/Yekaterinburg': '(GMT+05:00)',
  'Asia/Katmandu': '(GMT+6:00)',
  'Asia/Bangkok': '(GMT+07:00)',
  'Asia/Shanghai': '(GMT+08:00)',
  'Asia/Tokyo': '(GMT+09:00)',
  'Australia/Brisbane': '(GMT+10:00)',
  'Asia/Magadan': '(GMT+11:00)',
  'Pacific/Fiji': '(GMT+12:00)',
  'Pacific/Tongatapu': '(GMT+13:00)'
};

// 逐项/批量编辑
export const AGGREGATION_EDIT_ENUM = [
  { name: '逐项编辑', value: false },
  { name: '批量编辑', value: true }
];

// 批量展开
export const BOUNDARY_KEYS_ENUM = {
  resourcePerm: {
    title: '最大可授权操作和资源边界',
    isExpanded: false
  },
  membersPerm: {
    title: '最大可授权人员边界',
    isExpanded: false
  },
  transferPreview: {
    title: '转移预览',
    isExpanded: false
  }
};

// 需要弹出保存提示dialog的页面
export const NEED_CONFIRM_DIALOG_ROUTER = [
  'permTemplateCreate',
  'permTemplateEdit',
  'permTemplateDiff',
  'createUserGroup',
  'gradingAdminCreate',
  'gradingAdminEdit',
  'myManageSpaceCreate',
  'myManageSpaceClone',
  'authorBoundaryEditFirstLevel',
  'secondaryManageSpaceCreate'
];

// 不同导航栏下的路由模块分类
export const ALL_ROUTES_LIST = new Map([
  // 权限模板
  [
    ['permTemplate', 'permTemplateDetail', 'permTemplateCreate', 'permTemplateEdit', 'permTemplateDiff'],
    'permTemplateNav'
  ],
  // 首页
  [['', 'index'], 'indexNav'],
  // 用户组
  [
    ['userGroup', 'userGroupDetail', 'createUserGroup', 'cloneUserGroup', 'userGroupPermDetail', 'groupPermRenewal', 'addGroupPerm'],
    'userGroupNav'
  ],
  // 系统接入
  [
    [
      'systemAccess',
      'systemAccessCreate',
      'systemAccessAccess',
      'systemAccessRegistry',
      'systemAccessOptimize',
      'systemAccessComplete'
    ],
    'systemAccessNav'
  ],
  // 我的申请
  [['apply'], 'applyNav'],
  // 权限申请 'permApply'
  [['applyCustomPerm', 'applyJoinUserGroup'], 'permApplyNav'],
  // 临时权限申请 'provisionPermApply'
  [['applyProvisionPerm'], 'provisionPermApplyNav'],
  // 我的权限
  [
    [
      'myPerm',
      'templatePermDetail',
      'groupPermDetail',
      'permRenewal',
      'groupPermRenewal',
      'permTransfer',
      'permTransferHistory',
      'applyPerm'
    ],
    'myPermNav'
  ],
  // 我的管理空间
  [['myManageSpace', 'myManageSpaceCreate', 'myManageSpaceClone', 'myManageSpaceSubDetail'], 'myManageSpaceNav'],
  // 分级管理员
  [['ratingManager', 'gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit'], 'gradingAdminNav'],
  // 二级管理空间
  [
    [
      'secondaryManageSpace',
      'secondaryManageSpaceCreate',
      'secondaryManageSpaceClone',
      'secondaryManageSpaceDetail',
      'secondaryManageSpaceEdit'
    ],
    'secondaryManageSpaceNav'
  ],
  // 授权边界
  [['authorBoundary', 'authorBoundaryEditFirstLevel', 'authorBoundaryEditSecondLevel'], 'authorBoundaryNav'],
  // 最大可授权人员边界
  [['addMemberBoundary'], 'addMemberBoundaryNav'],
  // 资源权限
  [['resourcePermiss'], 'resourcePermissNav'],
  // 管理员
  [['administrator'], 'settingNav'],
  // 审批流程
  [['approvalProcess'], 'approvalProcessNav'],
  // 用户
  [['user'], 'userNav'],
  // 审计
  [['audit'], 'auditNav'],
  // 用户组设置
  [['userGroupSetting'], 'userGroupSettingNav'],
  // 敏感等级
  [['sensitivityLevel'], 'sensitivityLevelNav'],
  // 人员模板
  [['memberTemplate'], 'memberTemplateNav'],
  // 管理空间下资源权限管理
  [['resourcePermManage'], 'resourcePermManageNav'],
  // 用户/组织
  [['userOrgPerm'], 'userOrgPermNav'],
  // 续期通知
  [['renewalNotice'], 'renewalNoticeNav']
]);

// 切换管理员身份需要重定向的页面
export const MANAGE_SPACE_REDIRECT_ROUTES = new Map([
  // 权限模板
  [
    ['permTemplateDetail', 'permTemplateCreate', 'permTemplateEdit', 'permTemplateDiff'],
    'permTemplate'
  ],
  // 用户组模块
  [
    ['userGroupDetail', 'createUserGroup', 'cloneUserGroup', 'userGroupPermDetail', 'groupPermRenewal', 'addGroupPerm'],
    'userGroup'
  ],
  // 管理空间
  [
    ['gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit'],
    'ratingManager'
  ],
  // 授权边界
  [
    ['authorBoundaryEditFirstLevel', 'authorBoundaryEditSecondLevel'],
    'authorBoundary'
  ],
  // 二级管理员
  [
    ['secondaryManageSpaceCreate', 'secondaryManageSpaceClone', 'secondaryManageSpaceDetail', 'secondaryManageSpaceEdit'],
    'secondaryManageSpace'
  ]
]);

// 用户组属性枚举
export const USER_GROUP_ATTRIBUTES = [
  {
    id: 'apply_disable',
    name: '不可被申请',
    disabled: false
  }
];

// 用户组成员复制属性枚举
export const COPY_KEYS_ENUM = [
  {
    id: 'copy-checked',
    name: il8n('userGroup', '复制已选'),
    children: [
      {
        id: 'user-selected',
        name: il8n('userGroup', '成员')
      },
      {
        id: 'userAndOrg-selected',
        name: il8n('userGroup', '成员和组织架构')
      }
    ]
  },
  {
    id: 'copy-all',
    name: il8n('userGroup', '复制所有'),
    children: [
      {
        id: 'user-all',
        name: il8n('userGroup', '成员')
      },
      {
        id: 'userAndOrg-all',
        name: il8n('userGroup', '成员和组织架构')
      }
    ]
  }
];

// 敏感等级选项枚举
export const SENSITIVITY_LEVEL_ENUM = [
  {
    name: '不敏感',
    id: 'L1',
    theme: '',
    disabled: false
  },
  {
    name: '低',
    id: 'L2',
    theme: 'success',
    disabled: false
  },
  {
    name: '中',
    id: 'L3',
    theme: 'warning',
    disabled: false
  },
  {
    name: '高',
    id: 'L4',
    theme: 'danger',
    disabled: false
  },
  {
    name: '极高',
    id: 'L5',
    theme: 'danger',
    disabled: false
  }
];

// 人员模板配置项表格
export const MEMBERS_TEMPLATE_FIELDS = [
  {
    id: 'name',
    label: il8n('memberTemplate', '模板名称'),
    sortable: true,
    disabled: true,
    fixed: true
  },
  {
    id: 'description',
    label: il8n('common', '描述'),
    disabled: false
  },
  {
    id: 'group_count',
    label: il8n('memberTemplate', '关联用户组'),
    disabled: false
  },
  {
    id: 'creator',
    label: il8n('memberTemplate', '创建人'),
    disabled: false
  },
  {
    id: 'created_time',
    label: il8n('common', '创建时间'),
    disabled: false
  }
];

// 续期通知日期
export const SEND_DAYS_LIST = [
  {
    label: '周一',
    value: 'monday'
  },
  {
    label: '周二',
    value: 'tuesday'
  },
  {
    label: '周三',
    value: 'wednesday'
  },
  {
    label: '周四',
    value: 'thursday'
  },
  {
    label: '周五',
    value: 'friday'
  },
  {
    label: '周六',
    value: 'saturday'
  },
  {
    label: '周日',
    value: 'sunday'
  }
];

// 只显示角色名称的审计类型
export const ONLY_ROLE_TYPE = [
  'template.create',
  'subject.template.create',
  'subject.template.delete'
];

// 没有详情的审计类型
export const NO_DETAIL_TYPE = [
  'group.create',
  'group.delete',
  // 'template.create',
  'template.update',
  'role.create'
];

// 只有描述字段的审计类型
export const ONLY_DESCRIPTION_TYPE = [
  'group.update',
  'role.update',
  'role.member.policy.create',
  'role.member.policy.delete',
  'approval.global.update'
];

// 只有子对象的审计类型
export const ONLY_SUB_TYPE = [
  'action.sensitivity.level.update',
  'group.template.create',
  'group.member.create',
  'group.member.delete',
  'group.member.renew',
  'group.transfer',
  'user.group.delete',
  'department.group.delete',
  'user.role.delete',
  'role.member.create',
  'role.member.delete',
  'role.member.update',
  'role.commonaction.create',
  'role.commonaction.delete',
  'subject.template.group.delete',
  'subject.template.member.create',
  'subject.template.member.delete'
];

// 只有附加信息的审计类型
export const ONLY_EXTRA_INFO_TYPE = [
  'group.policy.create',
  'group.policy.delete',
  'group.policy.update',
  'user.policy.delete',
  'user.policy.create',
  'user.policy.update',
  'user.temporary.policy.create',
  'user.temporary.policy.delete',
  'user.blacklist.member.create',
  'user.blacklist.member.delete',
  'user.permission.clean',
  'role.group.renew',
  'template.version.sync'
];

// 既有 description 又有 extra_info
export const DE_TYPR = ['template.update'];

// 既有 sub_objects 又有 extra_info
export const SE_TYPE = [
  'template.member.create',
  'template.member.delete',
  'template.version.update'
];

// 既有 description 又有 sub_objects
export const DS_TYPE = [
  'approval.action.update',
  'approval.group.update',
  'template.preupdate.create'
];

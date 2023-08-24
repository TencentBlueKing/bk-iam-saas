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

const SITE_URL = window.SITE_URL;

// 系统接入
const SystemAccess = () => import(/* webpackChunkName: 'system-access' */ '../views/system-access');
const SystemAccessAccess = () => import(/* webpackChunkName: 'system' */ '../views/system-access/access');
const SystemAccessRegistry = () => import(/* webpackChunkName: 'system-access' */ '../views/system-access/registry');
const SystemAccessOptimize = () => import(/* webpackChunkName: 'system-access' */ '../views/system-access/optimize');
const SystemAccessComplete = () => import(/* webpackChunkName: 'system-access' */ '../views/system-access/complete');

// 申请自定义权限
const ApplyCustomPerm = () => import(/* webpackChunkName: 'perm-apply' */ '../views/perm-apply/apply-custom-perm');

// 申请临时权限
const applyProvisionPerm = () =>
  import(/* webpackChunkName: 'perm-apply' */ '../views/tempora-perm-apply/apply-custom-perm');

// 申请加入用户组
const ApplyJoinUserGroup = () =>
  import(/* webpackChunkName: 'perm-apply' */ '../views/perm-apply/apply-join-user-group');

// 我的申请
const Apply = () => import(/* webpackChunkName: 'my-apply' */ '../views/apply');

// 我的权限
const MyPerm = () => import(/* webpackChunkName: 'my-perm' */ '../views/perm');

// 申请权限外链页面
const ApplyPerm = () => import(/* webpackChunkName: 'my-perm' */ '../views/perm/apply-perm');

// 我的管理空间
const MyManageSpace = () => import(/* webpackChunkName: 'my-manage-space' */ '../views/my-manage-space');

// 新建我的管理空间
const MyManageSpaceCreate = () => import(/* webpackChunkName: 'my-manage-space' */ '../views/my-manage-space/create');

// 我的管理空间二级管理员授权边界
const MyManageSpaceSubDetail = () =>
  import(/* webpackChunkName: 'my-manage-space' */ '../views/my-manage-space/detail');

// 最大可授权人员边界
const AddMemberBoundary = () =>
  import(/* webpackChunkName: 'my-manage-space' */ '../views/my-manage-space/add-member-boundary');

// 用户组
const UserGroup = () => import(/* webpackChunkName: 'user-group' */ '../views/group');

// 用户组新建
const CreateUserGroup = () => import(/* webpackChunkName: 'user-group' */ '../views/group/create');

// 用户组克隆
const CloneUserGroup = () => import(/* webpackChunkName: 'user-group' */ '../views/group/clone');

// 用户组详情
const UserGroupDetail = () => import(/* webpackChunkName: 'user-group' */ '../views/group/detail');

// 用户组组权限详情
const UserGroupPermDetail = () =>
  import(/* webpackChunkName: 'user-group' */ '../views/group/detail/group-perm-detail');

// 用户组添加权限
const AddGroupPerm = () => import(/* webpackChunkName: 'user-group' */ '../views/group/add-perm');

// 权限模板
const PermTemplate = () => import(/* webpackChunkName: 'perm-template' */ '../views/perm-template/index');

// 权限模板详情
const PermTemplateDetail = () => import(/* webpackChunkName: 'perm-template' */ '../views/perm-template/detail');

// 权限模板新建
const PermTemplateCreate = () => import(/* webpackChunkName: 'perm-template' */ '../views/perm-template/create/index');

// 权限模板编辑
const PermTemplateEdit = () => import(/* webpackChunkName: 'perm-template' */ '../views/perm-template/edit');

// 权限模板编辑差异
const PermTemplateDifference = () =>
  import(/* webpackChunkName: 'perm-template' */ '../views/perm-template/edit/difference');

// 用户
const User = () => import(/* webpackChunkName: 'user' */ '../views/user');

// 管理空间
const GradingAdmin = () => import(/* webpackChunkName: 'grading-admin' */ '../views/grading-admin');

// 管理空间新建
const GradingAdminCreate = () => import(/* webpackChunkName: 'grading-admin' */ '../views/grading-admin/create');

// 管理空间详情
const GradingAdminDetail = () => import(/* webpackChunkName: 'grading-admin' */ '../views/grading-admin/detail');

// 管理空间编辑
const GradingAdminEdit = () => import(/* webpackChunkName: 'grading-admin' */ '../views/grading-admin/edit');

// 管理空间更新权限模板
const GradingAdminUpdateTemplate = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/grading-admin/update-template');

// // 管理空间
// const FirstManageSpace = () =>
//     import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/first-manage-space');

// // 管理空间新建
// const FirstManageSpaceCreate = () =>
//     import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/first-manage-space/create');

// 授权边界
const AuthorizationBoundary = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/authorization-boundary');

// 授权边界管理空间编辑
const AuthorizationBoundaryEditFirstLevel = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/authorization-boundary/edit/first-level');

// 授权边界二级管理空间编辑
const AuthorizationBoundarySecondLevel = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/authorization-boundary/edit/second-level');

// 二极管理空间
const SecondaryManageSpace = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/secondary-manage-space');

// 二极管理空间新建
const SecondaryManageSpaceCreate = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/secondary-manage-space/create');

// 二极管理空间编辑
const SecondaryManageSpaceEdit = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/secondary-manage-space/edit');

// 二极管理空间详情
const SecondaryManageSpaceDetail = () =>
  import(/* webpackChunkName: 'grading-admin' */ '../views/manage-spaces/secondary-manage-space/detail');

// 资源权限管理
const ResourcePermiss = () => import(/* webpackChunkName: 'grading-admin' */ '../views/resource-permiss');

// 设置
const Setting = () => import(/* webpackChunkName: 'set' */ '../views/set');

// 审批流程设置
const ApprovalProcess = () => import(/* webpackChunkName: 'approvalProcess' */ '../views/approval-process');

// 用户组设置
const UserGroupSetting = () => import(/* webpackChunkName: 'userGroupSetting' */ '../views/user-group-setting');

// 权限续期
const PermRenewal = () => import(/* webpackChunkName: 'PermRenewal' */ '../views/perm/perm-renewal');

// 组织权限续期
const GroupPermRenewal = () => import(/* webpackChunkName: 'PermRenewal' */ '../views/perm/group-perm-renewal');

// 审计
const Audit = () => import(/* webpackChunkName: 'audit' */ '../views/audit');

const TemplatePermDetail = () =>
  import(/* webpackChunkName: 'my-perm-template-perm' */ '../views/perm/template-perm/detail');
const GroupPermDetail = () => import(/* webpackChunkName: 'my-perm-group-perm' */ '../views/perm/group-perm/detail');
const OrgPermDetail = () => import(/* webpackChunkName: 'my-perm-org-perm' */ '../views/perm/organization-perm/detail');

const PermTransfer = () => import(/* webpackChunkName: 'perm-transfer' */ '../views/transfer');

const PermTransferHistory = () => import(/* webpackChunkName: 'perm-transfer' */ '../views/transfer/history');

// no-perm
const NoPerm = () => import(/* webpackChunkName: 'no-perm' */ '../views/no-perm');

// 403
const NotAccessPermPage = () => import(/* webpackChunkName: 'none' */ '../views/403');

// 404
const NotFound = () => import(/* webpackChunkName: 'none' */ '../views/404');

// Main
const MainEntry = () => import(/* webpackChunkName: 'index' */ '../views');

export const routes = [
  {
    path: SITE_URL,
    name: 'iamMain',
    component: MainEntry,
    children: [
      {
        path: 'system-access',
        name: 'systemAccess',
        meta: {
          headerTitle: il8n('nav', '系统接入')
        },
        component: SystemAccess
      },
      {
        path: 'system-access/access',
        name: 'systemAccessCreate',
        meta: {
          headerTitle: il8n('nav', '系统接入'),
          backRouter: 'systemAccess'
        },
        component: SystemAccessAccess
      },
      {
        path: 'system-access/access/:id',
        name: 'systemAccessAccess',
        meta: {
          headerTitle: il8n('nav', '系统接入'),
          backRouter: 'systemAccess'
        },
        component: SystemAccessAccess
      },
      {
        path: 'system-access/registry/:id',
        name: 'systemAccessRegistry',
        meta: {
          headerTitle: il8n('nav', '系统接入'),
          backRouter: 'systemAccessAccess'
        },
        component: SystemAccessRegistry
      },
      {
        path: 'system-access/optimize/:id',
        name: 'systemAccessOptimize',
        meta: {
          headerTitle: il8n('nav', '系统接入'),
          backRouter: 'systemAccessRegistry'
        },
        component: SystemAccessOptimize
      },
      {
        path: 'system-access/complete/:id',
        name: 'systemAccessComplete',
        meta: {
          headerTitle: il8n('nav', '系统接入'),
          backRouter: 'systemAccessRegistry'
        },
        component: SystemAccessComplete
      },
      {
        path: 'my-perm',
        name: 'myPerm',
        alias: '',
        meta: {
          headerTitle: il8n('nav', '我的权限')
          // hasPageTab: true
        },
        component: MyPerm
      },
      {
        path: 'my-perm/apply-perm',
        name: 'applyPerm',
        meta: {
          headerTitle: il8n('nav', '申请权限')
        },
        component: ApplyPerm
      },
      {
        path: 'my-manage-space',
        name: 'myManageSpace',
        meta: {
          headerTitle: il8n('nav', '我的管理空间')
        },
        component: MyManageSpace
      },
      {
        path: 'my-manage-space/create',
        name: 'myManageSpaceCreate',
        meta: {
          headerTitle: il8n('levelSpace', '新建我的管理空间'),
          backRouter: 'myManageSpace'
        },
        component: MyManageSpaceCreate
      },
      {
        path: 'my-manage-space/sub-detail',
        name: 'myManageSpaceSubDetail',
        meta: {
          backRouter: 'myManageSpace'
        },
        component: MyManageSpaceSubDetail
      },
      {
        path: 'add-member-boundary',
        name: 'addMemberBoundary',
        meta: {
          backRouter: -1
        },
        props: (route) => ({ ...route.query, ...route.params }),
        component: AddMemberBoundary
      },
      {
        path: 'perm-renewal',
        name: 'permRenewal',
        meta: {
          headerTitle: il8n('renewal', '申请续期'),
          backRouter: 'myPerm'
        },
        component: PermRenewal
      },
      {
        path: 'group-perm-renewal',
        name: 'groupPermRenewal',
        meta: {
          headerTitle: il8n('renewal', '用户组成员续期'),
          backRouter: 'myPerm'
        },
        component: GroupPermRenewal
      },
      {
        path: 'audit',
        name: 'audit',
        meta: {
          headerTitle: il8n('nav', '审计')
        },
        component: Audit
      },
      {
        path: 'my-perm/template-perm/:id',
        name: 'templatePermDetail',
        meta: {
          headerTitle: ''
        },
        component: TemplatePermDetail
      },
      {
        path: 'my-perm/group-perm/:id',
        name: 'groupPermDetail',
        meta: {
          headerTitle: ''
        },
        component: GroupPermDetail
      },
      {
        path: 'my-perm/organization-perm/:id',
        name: 'orgPermDetail',
        meta: {
          headerTitle: ''
        },
        component: OrgPermDetail
      },
      {
        path: 'manage-spaces/authorization-boundary',
        name: 'authorBoundary',
        meta: {
          // headerTitle: il8n('nav', '授权边界')
        },
        component: AuthorizationBoundary
      },
      {
        path: 'manage-spaces/authorization-boundary/first-level/:id',
        name: 'authorBoundaryEditFirstLevel',
        meta: {
          headerTitle: '',
          backRouter: 'authorBoundary'
        },
        component: AuthorizationBoundaryEditFirstLevel
      },
      {
        path: 'manage-spaces/authorization-boundary/second-level/:id',
        name: 'authorBoundaryEditSecondLevel',
        meta: {
          headerTitle: '',
          backRouter: 'authorBoundary'
        },
        component: AuthorizationBoundarySecondLevel
      },
      {
        path: 'manage-spaces/secondary-manage-space',
        name: 'secondaryManageSpace',
        meta: {
          headerTitle: il8n('nav', '二级管理空间')
        },
        component: SecondaryManageSpace
      },
      {
        path: ':id/manage-spaces/secondary-manage-space/create',
        name: 'secondaryManageSpaceCreate',
        meta: {
          headerTitle: '',
          backRouter: -1
        },
        props: true,
        component: SecondaryManageSpaceCreate
      },
      {
        path: ':id/manage-spaces/secondary-manage-space/edit',
        name: 'secondaryManageSpaceEdit',
        meta: {
          backRouter: -1
        },
        props: true,
        component: SecondaryManageSpaceEdit
      },
      {
        path: ':id/manage-spaces/secondary-manage-space/detail',
        name: 'secondaryManageSpaceDetail',
        meta: {
          backRouter: -1
        },
        component: SecondaryManageSpaceDetail
      },
      {
        path: 'user-group',
        name: 'userGroup',
        meta: {
          headerTitle: il8n('nav', '用户组')
        },
        component: UserGroup
      },
      {
        path: 'create-user-group',
        name: 'createUserGroup',
        meta: {
          headerTitle: il8n('userGroup', '新建用户组'),
          backRouter: 'userGroup'
        },
        component: CreateUserGroup
      },
      {
        path: 'clone-user-group',
        name: 'cloneUserGroup',
        meta: {
          headerTitle: il8n('userGroup', '用户组克隆'),
          backRouter: 'userGroup'
        },
        component: CloneUserGroup
      },
      {
        path: 'user-group-detail/:id',
        name: 'userGroupDetail',
        meta: {
          headerTitle: '',
          backRouter: 'userGroup',
          hasPageTab: true
        },
        component: UserGroupDetail
      },
      {
        path: 'user-group-perm-detail/:id/:templateId',
        name: 'userGroupPermDetail',
        meta: {
          headerTitle: '',
          backRouter: -1
        },
        component: UserGroupPermDetail
      },
      {
        path: 'add-group-perm/:id',
        name: 'addGroupPerm',
        meta: {
          headerTitle: il8n('userGroup', '添加组权限'),
          backRouter: -1
        },
        component: AddGroupPerm
      },
      {
        path: 'perm-template',
        name: 'permTemplate',
        meta: {
          headerTitle: il8n('nav', '权限模板')
        },
        component: PermTemplate
      },
      {
        path: 'perm-template-detail/:id/:systemId',
        name: 'permTemplateDetail',
        meta: {
          headerTitle: '',
          backRouter: 'permTemplate',
          hasPageTab: true
        },
        component: PermTemplateDetail
      },
      {
        path: 'perm-template-create',
        name: 'permTemplateCreate',
        meta: {
          headerTitle: il8n('nav', '新建权限模板'),
          backRouter: 'permTemplate'
        },
        component: PermTemplateCreate
      },
      {
        path: 'perm-template-edit/:id/:systemId',
        name: 'permTemplateEdit',
        meta: {
          headerTitle: '',
          backRouter: 'permTemplateDetail'
        },
        component: PermTemplateEdit
      },
      {
        path: 'perm-template-diff/:id/:systemId',
        name: 'permTemplateDiff',
        meta: {
          headerTitle: '',
          backRouter: -1
        },
        component: PermTemplateDifference
      },
      {
        path: 'apply-custom-perm',
        name: 'applyCustomPerm',
        meta: {
          headerTitle: il8n('applyEntrance', '申请自定义权限'),
          backRouter: -1
        },
        component: ApplyCustomPerm
      },
      {
        path: 'apply-provision-perm',
        name: 'applyProvisionPerm',
        meta: {
          headerTitle: il8n('applyEntrance', '申请临时权限'),
          backRouter: -1
        },
        component: applyProvisionPerm
      },
      {
        path: 'apply-join-user-group',
        name: 'applyJoinUserGroup',
        meta: {
          headerTitle: il8n('applyEntrance', '申请加入用户组')
        },
        component: ApplyJoinUserGroup
      },
      {
        path: 'apply',
        name: 'apply',
        meta: {
          headerTitle: il8n('nav', '我的申请')
        },
        component: Apply
      },
      {
        path: 'user',
        name: 'user',
        meta: {
          headerTitle: il8n('nav', '用户')
        },
        component: User
      },
      {
        path: 'rating-manager',
        name: 'ratingManager',
        meta: {
          headerTitle: il8n('grading', '管理空间')
        },
        component: GradingAdmin
      },
      {
        path: ':id/rating-manager-create',
        name: 'gradingAdminCreate',
        meta: {
          headerTitle: il8n('nav', '新建管理空间'),
          backRouter: -1
        },
        props: true,
        component: GradingAdminCreate
      },
      {
        path: ':id/rating-manager-detail',
        name: 'gradingAdminDetail',
        meta: {
          backRouter: 'ratingManager'
        },
        component: GradingAdminDetail
      },
      {
        path: ':id/rating-manager-edit',
        name: 'gradingAdminEdit',
        meta: {
          backRouter: 'gradingAdminDetail'
        },
        component: GradingAdminEdit
      },
      {
        path: ':id/rating-manager-update-template',
        name: 'gradingAdminUpdateTemplate',
        meta: {
          headerTitle: il8n('nav', '编辑管理空间'),
          backRouter: 'gradingAdminEdit'
        },
        component: GradingAdminUpdateTemplate
      },
      // {
      //     path: 'first-manage-space',
      //     name: 'firstManageSpace',
      //     meta: {
      //         headerTitle: il8n('nav', '管理空间')
      //     },
      //     component: FirstManageSpace
      // },
      // {
      //     path: ':id/first-manage-space-create',
      //     name: 'firstManageSpaceCreate',
      //     meta: {
      //         headerTitle: il8n('levelSpace', '新建管理空间'),
      //         backRouter: 'firstManageSpace'
      //     },
      //     props: true,
      //     component: FirstManageSpaceCreate
      // },
      {
        path: 'resource-permiss',
        name: 'resourcePermiss',
        meta: {
          headerTitle: il8n('nav', '资源权限管理')
        },
        component: ResourcePermiss
      },
      {
        path: 'administrator',
        name: 'administrator',
        meta: {
          headerTitle: il8n('common', '管理员')
        },
        component: Setting
      },
      {
        path: 'approval-process',
        name: 'approvalProcess',
        meta: {
          headerTitle: il8n('myApply', '审批流程')
        },
        component: ApprovalProcess
      },
      {
        path: 'user-group-setting',
        name: 'userGroupSetting',
        meta: {
          headerTitle: il8n('nav', '用户组设置')
        },
        component: UserGroupSetting
      },
      {
        path: 'no-perm',
        name: 'noPerm',
        meta: {
          headerTitle: ''
        },
        component: NoPerm
      },
      {
        path: 'perm-transfer',
        name: 'permTransfer',
        meta: {
          headerTitle: il8n('permTransfer', '权限交接'),
          backRouter: 'myPerm'
        },
        component: PermTransfer
      },
      {
        path: 'perm-transfer-history',
        name: 'permTransferHistory',
        meta: {
          headerTitle: il8n('permTransfer', '交接历史'),
          backRouter: 'myPerm'
        },
        component: PermTransferHistory
      }
    ]
  },
  {
    path: '403',
    name: '403',
    component: NotAccessPermPage
  },
  {
    path: '*',
    name: '404',
    component: NotFound
  }
];

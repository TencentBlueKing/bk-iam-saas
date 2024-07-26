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
  
/**
 * 获取不同身份的router差异
 *
 * @param {String} payload 身份类型(staff: 普通用户，super_manager: 超级用户，system_manager: 系统管理员，rating_manager: 管理空间)
 *
 * @return {Array}
 */
export const getRouterDiff = (payload) => {
  if (payload === 'staff' || payload === '') {
    return [
      'userGroup',
      'createUserGroup',
      'cloneUserGroup',
      'userGroupDetail',
      'permTemplate',
      'permTemplateCreate',
      'user',
      'permTemplateDetail',
      'administrator',
      'approvalProcess',
      'groupPermRenewal',
      'audit',
      'permTemplateEdit',
      'permTemplateDiff',
      'addGroupPerm',
      'resourcePermiss',
      'ratingManager',
      'gradingAdminCreate',
      'gradingAdminDetail',
      'gradingAdminEdit',
      'gradingAdminUpdateTemplate',
      'secondaryManageSpace',
      'secondaryManageSpaceCreate',
      'secondaryManageSpaceDetail',
      'authorBoundary',
      'authorBoundaryEditFirstLevel',
      'authorBoundaryEditSecondLevel',
      'userGroupSetting',
      'sensitivityLevel',
      'memberTemplate',
      'resourcePermManage',
      'userOrgPerm',
      'renewalNotice',
      'actionsTemplate',
      'actionsTemplateCreate',
      'actionsTemplateEdit'
    ];
  }
  if (payload === 'super_manager') {
    return [
      'applyCustomPerm',
      'applyProvisionPerm',
      'applyJoinUserGroup',
      'apply',
      'myPerm',
      'templatePermDetail',
      'groupPermDetail',
      'orgPermDetail',
      'ratingManager',
      'gradingAdminCreate',
      'gradingAdminDetail',
      'gradingAdminEdit',
      'gradingAdminUpdateTemplate',
      'user',
      'gradingAdminUpdateTemplate',
      'administrator',
      'approval',
      'permRenewal',
      'audit',
      'systemAccess',
      'systemAccessCreate',
      'systemAccessAccess',
      'systemAccessRegistry',
      'systemAccessOptimize',
      'systemAccessComplete',
      'resourcePermiss',
      'secondaryManageSpace',
      'authorBoundary',
      'authorBoundaryEditFirstLevel',
      'authorBoundaryEditSecondLevel',
      'myManageSpace',
      'myManageSpaceCreate',
      'permTransfer',
      'myManageSpaceSubDetail',
      'sensitivityLevel',
      'resourcePermManage',
      'renewalNotice',
      'userOrgPerm'
    ];
  }
  if (payload === 'system_manager') {
    return [
      'applyCustomPerm',
      'applyProvisionPerm',
      'applyJoinUserGroup',
      'apply',
      'myPerm',
      'templatePermDetail',
      'groupPermDetail',
      'orgPermDetail',
      'ratingManager',
      'gradingAdminCreate',
      'gradingAdminDetail',
      'gradingAdminEdit',
      'gradingAdminUpdateTemplate',
      'user',
      'approval',
      'permRenewal',
      'permTransfer',
      'audit',
      'systemAccess',
      'systemAccessCreate',
      'systemAccessAccess',
      'systemAccessRegistry',
      'systemAccessOptimize',
      'systemAccessComplete',
      'secondaryManageSpace',
      'secondaryManageSpaceCreate',
      'secondaryManageSpaceDetail',
      'authorBoundary',
      'authorBoundaryEditFirstLevel',
      'authorBoundaryEditSecondLevel',
      'myManageSpace',
      'myManageSpaceCreate',
      'renewalNotice',
      'userOrgPerm'
    ];
  }
  if (payload === 'rating_manager') {
    return [
      'applyCustomPerm',
      'applyProvisionPerm',
      'applyJoinUserGroup',
      'apply',
      'myPerm',
      'templatePermDetail',
      'groupPermDetail',
      'orgPermDetail',
      'ratingManager',
      'gradingAdminCreate',
      'gradingAdminDetail',
      'gradingAdminEdit',
      'gradingAdminUpdateTemplate',
      'user',
      'administrator',
      'approval',
      'permRenewal',
      'permTransfer',
      'audit',
      'systemAccess',
      'systemAccessCreate',
      'systemAccessAccess',
      'systemAccessRegistry',
      'systemAccessOptimize',
      'systemAccessComplete',
      'myManageSpace',
      'resourcePermiss',
      'sensitivityLevel',
      'resourcePermManage',
      'renewalNotice'
    ];
  }
  if (payload === 'subset_manager') {
    return [
      'applyCustomPerm',
      'applyProvisionPerm',
      'applyJoinUserGroup',
      'apply',
      'myPerm',
      'templatePermDetail',
      'groupPermDetail',
      'orgPermDetail',
      'ratingManager',
      'gradingAdminCreate',
      'gradingAdminDetail',
      'gradingAdminEdit',
      'gradingAdminUpdateTemplate',
      'user',
      'administrator',
      'approval',
      'permRenewal',
      'permTransfer',
      'audit',
      'systemAccess',
      'systemAccessCreate',
      'systemAccessAccess',
      'systemAccessRegistry',
      'systemAccessOptimize',
      'systemAccessComplete',
      'resourcePermiss',
      'secondaryManageSpace',
      'secondaryManageSpaceCreate',
      'secondaryManageSpaceDetail',
      'myManageSpace',
      'permTemplate',
      'userGroupSetting',
      'sensitivityLevel',
      'memberTemplate',
      'resourcePermManage',
      'userOrgPerm',
      'renewalNotice',
      'actionsTemplate',
      'actionsTemplateCreate',
      'actionsTemplateEdit'
    ];
  }
  // payload其它取值默认返回全部菜单
  return [
    'systemAccess',
    'systemAccessCreate',
    'systemAccessAccess',
    'systemAccessRegistry',
    'systemAccessOptimize',
    'systemAccessComplete',
    'myPerm',
    'templatePermDetail',
    'groupPermDetail',
    'orgPermDetail',
    'userGroup',
    'createUserGroup',
    'cloneUserGroup',
    'userGroupDetail',
    'userGroupPermDetail',
    'permTemplate',
    'permTemplateDetail',
    'permTemplateCreate',
    'applyCustomPerm',
    'applyProvisionPerm',
    'applyJoinUserGroup',
    'apply',
    'user',
    'ratingManager',
    'gradingAdminCreate',
    'gradingAdminDetail',
    'gradingAdminEdit',
    'gradingAdminUpdateTemplate',
    'administrator',
    'approvalProcess',
    'approval',
    'permRenewal',
    'groupPermRenewal',
    'audit',
    'permTemplateEdit',
    'permTemplateDiff',
    'addGroupPerm',
    'authorBoundary',
    'authorBoundaryEditFirstLevel',
    'authorBoundaryEditSecondLevel',
    'secondaryManageSpace',
    'myManageSpace',
    'myManageSpaceCreate',
    'resourcePermManage',
    'resourcePermiss',
    'sensitivityLevel',
    'userOrgPerm',
    'renewalNotice',
    'actionsTemplate',
    'actionsTemplateCreate',
    'actionsTemplateEdit'
  ];
};

// 导航路由
export const getNavRouterDiff = (navIndex, managerPerm = '') => {
  if (navIndex === 0 || navIndex === '') {
    return [
      'userGroup',
      'createUserGroup',
      'cloneUserGroup',
      'userGroupDetail',
      'permTemplate',
      'permTemplateCreate',
      'user',
      'permTemplateDetail',
      'administrator',
      'approvalProcess',
      'groupPermRenewal',
      'audit',
      'permTemplateEdit',
      'permTemplateDiff',
      'addGroupPerm',
      'resourcePermiss',
      'ratingManager',
      'gradingAdminCreate',
      'gradingAdminDetail',
      'gradingAdminEdit',
      'gradingAdminUpdateTemplate',
      'authorBoundary',
      'authorBoundaryEditFirstLevel',
      'authorBoundaryEditSecondLevel',
      'secondaryManageSpace',
      'secondaryManageSpaceCreate',
      'secondaryManageSpaceDetail',
      'userGroupSetting',
      'sensitivityLevel',
      'memberTemplate',
      'resourcePermManage',
      'userOrgPerm',
      'renewalNotice',
      'actionsTemplate',
      'actionsTemplateCreate',
      'actionsTemplateEdit'
    ];
  }

  if (navIndex === 2) {
    return [
      'systemAccess',
      'systemAccessCreate',
      'systemAccessAccess',
      'systemAccessRegistry',
      'systemAccessOptimize',
      'systemAccessComplete',
      'myPerm',
      'templatePermDetail',
      'groupPermDetail',
      'orgPermDetail',
      'userGroup',
      'createUserGroup',
      'cloneUserGroup',
      'userGroupDetail',
      'userGroupPermDetail',
      'permTemplate',
      'permTemplateDetail',
      'permTemplateCreate',
      'applyCustomPerm',
      'applyProvisionPerm',
      'applyJoinUserGroup',
      'apply',
      'user',
      'ratingManager',
      'gradingAdminCreate',
      'gradingAdminDetail',
      'gradingAdminEdit',
      'gradingAdminUpdateTemplate',
      'administrator',
      'approvalProcess',
      'approval',
      'permRenewal',
      'permTransfer',
      'groupPermRenewal',
      'permTemplateEdit',
      'permTemplateDiff',
      'addGroupPerm',
      'resourcePermiss',
      'authorBoundary',
      'authorBoundaryEditFirstLevel',
      'authorBoundaryEditSecondLevel',
      'myManageSpace',
      'myManageSpaceCreate',
      'secondaryManageSpace',
      'secondaryManageSpaceCreate',
      'secondaryManageSpaceDetail',
      'userGroupSetting',
      'sensitivityLevel',
      'memberTemplate',
      'resourcePermManage',
      'userOrgPerm',
      'renewalNotice',
      'actionsTemplate',
      'actionsTemplateCreate',
      'actionsTemplateEdit'
    ];
  }

  if (navIndex === 3) {
    const menuList = [
      'applyCustomPerm',
      'applyProvisionPerm',
      'applyJoinUserGroup',
      'apply',
      'myPerm',
      'templatePermDetail',
      'groupPermDetail',
      'orgPermDetail',
      'approval',
      'permRenewal',
      'permTransfer',
      'systemAccess',
      'systemAccessCreate',
      'systemAccessAccess',
      'systemAccessRegistry',
      'systemAccessOptimize',
      'systemAccessComplete',
      'audit',
      'userGroup',
      'createUserGroup',
      'cloneUserGroup',
      'userGroupDetail',
      'userGroupPermDetail',
      'permTemplate',
      'permTemplateDetail',
      'permTemplateCreate',
      'myManageSpace',
      'myManageSpaceCreate',
      'secondaryManageSpace',
      'secondaryManageSpaceCreate',
      'secondaryManageSpaceDetail',
      'authorBoundary',
      'authorBoundaryEditFirstLevel',
      'authorBoundaryEditSecondLevel',
      'permTemplateEdit',
      'permTemplateDiff',
      'addGroupPerm',
      'groupPermRenewal',
      'userGroupSetting',
      'memberTemplate',
      'resourcePermManage',
      'userOrgPerm',
      'actionsTemplate',
      'actionsTemplateCreate',
      'actionsTemplateEdit'
    ];
    if (['hasSystemNoSuperManager'].includes(managerPerm)) {
      // 非超管用户隐藏的路由
      const hideMenuList = [
        'user',
        'approvalProcess',
        'ratingManager',
        'gradingAdminCreate',
        'gradingAdminDetail',
        'gradingAdminEdit',
        'gradingAdminUpdateTemplate',
        'renewalNotice'
      ];
      const systemManagerMenu = [
        ...menuList,
        ...hideMenuList
      ];
      return systemManagerMenu;
    }
    return menuList;
  }
};

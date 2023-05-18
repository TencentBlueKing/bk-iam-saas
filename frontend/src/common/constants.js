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
    'authorBoundaryEditFirstLevel',
    'secondaryManageSpaceCreate'
];

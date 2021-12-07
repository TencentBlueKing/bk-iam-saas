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

/* eslint-disable no-unused-vars */
import moment from 'moment'
import faker from 'faker'
import chalk from 'chalk'

import { randomInt, sleep } from './util'

export async function response (getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()
    const invoke = getArgs.invoke
    if (invoke === 'getUserInfo') {
        return {
            // 打开下面的注释，模拟 401 的返回，刷新页面会看到页面跳转到登录页
            // statusCode: 401,
            code: 0,
            data: {
                id: '1234567890',
                username: 'admin',
                timestamp: +new Date()
            },
            message: 'ok'
        }
    } else if (invoke === 'enterExample1') {
        const delay = getArgs.delay
        await sleep(delay)
        return {
            // http status code, 后端返回的数据没有这个字段，这里模拟这个字段是为了在 mock 时更灵活的自定义 http status code，
            // 同时热更新即改变 http status code 后无需重启服务，这个字段的处理参见 build/ajax-middleware.js
            // statusCode: 401,
            code: 0,
            data: {
                msg: `我是 enterExample1 请求返回的数据。本请求需耗时 ${delay} ms`
            },
            message: 'ok'
        }
    } else if (invoke === 'enterExample2') {
        const delay = postArgs.delay
        await sleep(delay)
        return {
            // http status code, 后端返回的数据没有这个字段，这里模拟这个字段是为了在 mock 时更灵活的自定义 http status code，
            // 同时热更新即改变 http status code 后无需重启服务，这个字段的处理参见 build/ajax-middleware.js
            // statusCode: 401,
            code: 0,
            data: {
                msg: `我是 enterExample2 请求返回的数据。本请求需耗时 ${delay} ms`
            },
            message: 'ok'
        }
    } else if (invoke === 'btn1') {
        const delay = getArgs.delay
        await sleep(delay)
        return {
            // http status code, 后端返回的数据没有这个字段，这里模拟这个字段是为了在 mock 时更灵活的自定义 http status code，
            // 同时热更新即改变 http status code 后无需重启服务，这个字段的处理参见 build/ajax-middleware.js
            // statusCode: 401,
            code: 0,
            data: {
                msg: `我是 btn1 请求返回的数据。本请求需耗时 2000 ms. ${+new Date()}`
            },
            message: 'ok'
        }
    } else if (invoke === 'btn2') {
        const delay = getArgs.delay
        await sleep(delay)
        return {
            // http status code, 后端返回的数据没有这个字段，这里模拟这个字段是为了在 mock 时更灵活的自定义 http status code，
            // 同时热更新即改变 http status code 后无需重启服务，这个字段的处理参见 build/ajax-middleware.js
            // statusCode: 401,
            code: 0,
            data: {
                msg: `我是 btn2 请求返回的数据。本请求需耗时 2000 ms. ${+new Date()}`
            },
            message: 'ok'
        }
    } else if (invoke === 'del') {
        return {
            code: 0,
            data: {
                msg: `我是 del 请求返回的数据。请求参数为 ${postArgs.time}`
            },
            message: 'ok'
        }
    } else if (invoke === 'getTransferHistory') {
        return {
            data: {
                counts: 3,
                results: [
                    { handover_record_id: 1, created_time: '2021-11-27 06:59:39', transferor: 'lisi', status: 'success' },
                    { handover_record_id: 2, created_time: '2021-11-27 08:20:39', transferor: 'xiaoming', status: 'failed' },
                    { handover_record_id: 3, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 4, created_time: '2021-12-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 5, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'success' },
                    { handover_record_id: 6, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'running' },
                    { handover_record_id: 7, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 8, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 9, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'success' },
                    { handover_record_id: 10, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 11, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 12, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'running' },
                    { handover_record_id: 13, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'success' },
                    { handover_record_id: 14, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 15, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 16, created_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' }
                ]
            },
            result: true,
            code: 0,
            message: 'OK'
        }
    } else if (invoke === 'getTransferHistoryDetail') {
        return {
            message: 'OK',
            code: 0,
            result: 'true',
            data: [
                {
                    object_type: 'group',
                    created_time: '2021-11-27 06:59:39',
                    status: 'succeed',
                    object_detail: {
                        id: '1',
                        name: 'paas用户组',
                        expired_at: 1651663822,
                        expired_at_display: '156 天',
                        department_id: 0
                    },
                    error_info: ''
                },
                {
                    object_type: 'group',
                    created_time: '2021-11-27 06:59:39',
                    status: 'succeed',
                    object_detail: {
                        id: '2',
                        name: '阿萨达是用户组',
                        expired_at: 1651663822,
                        expired_at_display: '156 天',
                        department_id: 0
                    },
                    error_info: ''
                },
                {
                    object_type: 'custom',
                    created_time: '2021-11-27 06:59:39',
                    status: 'succeed',
                    object_detail: {
                        id: 'app-mgmt',
                        name: '应用配置中心',
                        policy_info: {
                            id: 'package_version_create',
                            related_resource_types: [],
                            policy_id: 1408,
                            expired_at: 1651990820,
                            type: 'create',
                            name: '程序包版本新建',
                            description: '',
                            expired_display: '163 天'
                        }
                    },
                    error_info: ''
                },
                {
                    object_type: 'custom',
                    created_time: '2021-11-27 06:59:39',
                    status: 'succeed',
                    object_detail: {
                        id: 'qwqweapp-mgmt',
                        name: '敖德萨多撒所多应用配置中心',
                        policy_info: {
                            id: 'package_version_create',
                            related_resource_types: [],
                            policy_id: 1408,
                            expired_at: 1651990820,
                            type: 'create',
                            name: '程序包版本新建',
                            description: '',
                            expired_display: '163 天'
                        }
                    },
                    error_info: ''
                },
                {
                    created_time: '2021-11-27 06:59:39',
                    object_type: 'super_manager',
                    status: 'succeed',
                    object_detail: {
                        id: 1,
                        name: '超级管理员',
                        members: ['admin', 'jackliang', 'chace']
                    },
                    error_info: ''
                },
                {
                    created_time: '2021-11-27 06:59:39',
                    object_type: 'system_manager',
                    status: 'succeed',
                    object_detail: {
                        id: 2,
                        name: '系统管理员A',
                        members: ['admin', 'jackliang', 'chace']
                    }
                },
                {
                    created_time: '2021-11-27 06:59:39',
                    object_type: 'system_manager',
                    status: 'succeed',
                    object_detail: {
                        id: 3,
                        name: 'asdas系统管理员A',
                        members: ['admin', 'jackliang', 'chace']
                    }
                },
                {
                    object_type: 'rating_manager',
                    created_time: '2021-11-27 06:59:39',
                    status: 'failed',
                    object_detail: {
                        id: 4,
                        name: '分级管理员C'
                    },
                    error_info: 'handover error.'
                },
                {
                    object_type: 'rating_manager',
                    created_time: '2021-11-27 06:59:39',
                    status: 'succeed',
                    object_detail: {
                        id: 5,
                        name: '啊飒飒大多所是分级管理员C'
                    },
                    error_info: 'handover error.'
                }
            ]
        }
    }
    return {
        code: 0,
        data: {}
    }
}

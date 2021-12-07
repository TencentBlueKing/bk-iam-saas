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
                    { handover_record_id: 3, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 4, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 5, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'success' },
                    { handover_record_id: 6, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 7, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 8, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 9, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'success' },
                    { handover_record_id: 10, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 11, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 12, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 13, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'success' },
                    { handover_record_id: 14, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' },
                    { handover_record_id: 15, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'failed' },
                    { handover_record_id: 16, create_time: '2021-11-27 10:20:39', transferor: 'xiaohong', status: 'partial_succeed' }
                ]
            },
            result: true,
            code: 0,
            message: 'OK'
        }
    }
    return {
        code: 0,
        data: {}
    }
}

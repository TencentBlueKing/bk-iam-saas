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

import { extname } from 'path';

export default class ReplaceStaticUrlPlugin {
  apply (compiler, callback) {
    // emit: 在生成资源并输出到目录之前
    compiler.plugin('emit', (compilation, callback) => {
      const assets = Object.keys(compilation.assets);
      const assetsLen = assets.length;

      for (let i = 0; i < assetsLen; i++) {
        const fileName = assets[i];
        if (extname(fileName) === '.js') {
          if (fileName.indexOf('vendor') > -1) {
            const asset = compilation.assets[fileName];

            const minifyFileContent = asset.source().replace(
              // /\"\{\{\s{1}BK_STATIC_URL\s{1}\}\}\"/,
              // /\"\{\{BK_STATIC_URL\}\}\"/g,
              // () => 'window.PROJECT_CONFIG.BK_STATIC_URL + "/"'
              /\"\{\{STATIC_URL\}\}\"/g,
              () => 'window.STATIC_URL + "/"'
            );
            // 设置输出资源
            compilation.assets[fileName] = {
              // 返回文件内容
              source: () => minifyFileContent,
              // 返回文件大小
              size: () => Buffer.byteLength(minifyFileContent, 'utf8')
            };
            break;
          }
        }
      }

      callback();
    });

    // after-emit: 在生成资源并输出到目录之后
    // css 文件由 ExtractTextPlugin 生成，所以需要在 after-emit 钩子里面处理
    // 这里可以获取到 assets 但是无法修改了，只能在之后的插件里的 emit 处理
    /* compiler.plugin('after-emit', (compilation, callback) => {
            const assets = Object.keys(compilation.assets)
            const assetsLen = assets.length

            for (let i = 0; i < assetsLen; i++) {
                const fileName = assets[i]
                if (extname(fileName) !== '.css') {
                    continue
                }

                const asset = compilation.assets[fileName]

                const minifyFileContent = asset.source().replace(
                    // /\"\{\{\s{1}STATIC_URL\s{1}\}\}\"/,
                    /\{\{STATIC_URL\}\}/g,
                    () => '../../../'
                )
                // 设置输出资源
                compilation.assets['fileName.css'] = {
                    // 返回文件内容
                    source: () => minifyFileContent,
                    // 返回文件大小
                    size: () => Buffer.byteLength(minifyFileContent, 'utf8')
                }
            }

            callback()
        })*/
  }
}

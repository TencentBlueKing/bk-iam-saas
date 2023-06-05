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

import path from 'path';
import webpack from 'webpack';
import TerserPlugin from 'terser-webpack-plugin';
import chalk from 'chalk';
import glob from 'glob';
import ora from 'ora';

import config from './config';

const ret = glob.sync('../static/lib**', { mark: true, cwd: __dirname });

const mode = process.env.NODE_ENV === 'production' ? 'production' : 'development';
const configMap = {
  production: config.build,
  development: config.dev
};

if (!ret.length) {
  // 需要打包到一起的 js 文件
  const vendors = [
    'vue/dist/vue.esm.js',
    'vuex',
    'vue-router',
    'axios'
  ];

  const dllConf = {
    mode,
    // 也可设置多个入口，多个 vendor，就可以生成多个 bundle
    entry: {
      lib: vendors
    },
    // 输出文件的名称和路径
    output: {
      filename: '[name].bundle.js',
      path: path.join(__dirname, '..', 'static'),
      // lib.bundle.js 中暴露出的全局变量名
      library: '[name]_[chunkhash]'
    },
    plugins: [
      new webpack.DefinePlugin(configMap[mode].env),
      new webpack.DllPlugin({
        path: path.join(__dirname, '..', 'static', '[name]-manifest.json'),
        name: '[name]_[chunkhash]',
        context: __dirname
      }),

      new TerserPlugin({
        terserOptions: {
          compress: false,
          mangle: true,
          output: {
            comments: false
          }
        },
        cache: true,
        parallel: true,
        sourceMap: true
      }),

      new webpack.LoaderOptionsPlugin({
        minimize: true
      }),
      new webpack.optimize.OccurrenceOrderPlugin()
    ]
  };

  const spinner = ora('building dll...');
  spinner.start();

  webpack(dllConf, (err, stats) => {
    spinner.stop();
    if (err) {
      throw err;
    }
    process.stdout.write(stats.toString({
      colors: true,
      modules: false,
      children: false,
      chunks: false,
      chunkModules: false
    }) + '\n\n');

    if (stats.hasErrors()) {
      console.log(chalk.red('  Build failed with errors.\n'));
      process.exit(1);
    }

    console.log(chalk.cyan('  DLL Build complete.\n'));
  });
}

# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from collections import defaultdict
from typing import List

from celery import Task, current_app
from django.core.paginator import Paginator
from pydantic import parse_obj_as

from backend.api.bkci.models import MigrateData, MigrateTask
from backend.apps.group.models import Group
from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.role.models import RoleRelatedObject
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.component.iam import list_all_subject_member
from backend.service.models.policy import Policy
from backend.service.models.subject import Subject
from backend.util.json import json_dumps


class BKCIMigrateTask(Task):
    name = "backend.api.bkci.tasks.BKCIMigrateTask"

    def run(self):
        # delete all old migrate data
        MigrateData.objects.all().delete()

        # create new migrate data
        self.handle_group_api_policy()
        self.handle_group_web_policy()
        self.handle_user_custom_policy()

        # update status
        MigrateTask.objects.filter(celery_id=self.request.id).update(status="SUCCESS")

    def _handle_policy(self, policy: Policy, subject: Subject, project_subject_path_action):
        if not policy.resource_groups[0].related_resource_types[0].condition:
            return

        for rg in policy.resource_groups:
            for rtt in rg.related_resource_types:
                for condition in rtt.condition:
                    for instance in condition.instances:
                        for path in instance.path:
                            first_node = path.__root__[0]
                            if first_node.type != "project":
                                continue

                            project_subject_path_action[(first_node.type, first_node.id)][subject][path][rtt.type].add(
                                policy.action_id
                            )

    def handle_user_custom_policy(self):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        qs = PolicyModel.objects.filter(system_id="bk_ci", subject_type="user").order_by("id")
        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "user_custom_policy")

    def handle_group_web_policy(self):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        role_ids = [int(_id) for _id in role_id_text.strip().split()]
        exists_group_ids = list(
            RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type="group").values_list(
                "object_id", flat=True
            )
        )

        # 1. 遍历策略分析出所有实例
        qs = (
            PolicyModel.objects.filter(system_id="bk_ci", subject_type="group")
            .exclude(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        # 2. 遍历用户组授权模板权限
        qs = (
            PermTemplatePolicyAuthorized.objects.filter(system_id="bk_ci")
            .exclude(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        for pa in qs:
            policies = parse_obj_as(List[Policy], pa.data["actions"])
            subject = Subject(type=pa.subject_type, id=pa.subject_id)
            for p in policies:
                self._handle_policy(p, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "group_web_policy")

    def handle_group_api_policy(self):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        role_ids = [int(_id) for _id in role_id_text.strip().split()]
        exists_group_ids = list(
            RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type="group").values_list(
                "object_id", flat=True
            )
        )

        # 1. 遍历策略分析出所有实例
        qs = (
            PolicyModel.objects.filter(system_id="bk_ci", subject_type="group")
            .filter(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        # 2. 遍历用户组授权模板权限
        qs = (
            PermTemplatePolicyAuthorized.objects.filter(system_id="bk_ci")
            .filter(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        for pa in qs:
            policies = parse_obj_as(List[Policy], pa.data["actions"])
            subject = Subject(type=pa.subject_type, id=pa.subject_id)
            for p in policies:
                self._handle_policy(p, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "group_api_policy")

    def batch_create_migrate_data(self, project_subject_path_action, handler_type):
        for project, subject_path_action in project_subject_path_action.items():
            for subject, path_type_action in subject_path_action.items():
                subject_dict = subject.dict()
                if subject.type == "group":
                    group = Group.objects.filter(id=subject.id).first()
                    if not group:
                        continue

                    subject_dict["name"] = group.name

                permissions = []
                for path, type_actions in path_type_action.items():
                    for _type, actions in type_actions.items():
                        permissions.append(
                            {
                                "actions": [{"id": _id} for _id in list(actions)],
                                "resources": [{"type": _type, "paths": [[one.dict() for one in path.__root__]]}],
                            }
                        )

                data = {
                    "type": handler_type,
                    "project_id": project[1],
                    "subject": subject_dict,
                    "permissions": permissions,
                }

                if subject.type == "group":
                    data["members"] = list_all_subject_member(subject.type, subject.id)

                migrate_data = MigrateData(
                    project_id=project[1],
                    type=handler_type,
                    data=json_dumps(data),
                )
                migrate_data.save(force_insert=True)


current_app.tasks.register(BKCIMigrateTask())


role_id_text = """
2308
2134
2382
2276
2117
2141
2056
2242
2214
2313
2081
2342
2257
2190
2020
2311
2037
2093
2361
2222
2235
2217
2125
2298
2103
2260
2355
2348
2213
2325
2043
2240
2186
2395
2340
2074
2269
2253
2333
2398
2292
2140
2061
2285
2223
2015
2368
2198
2302
2146
2259
2371
2304
2054
2387
2328
2247
2035
2076
2296
2270
2089
2380
2216
2159
2033
2131
2109
2294
2352
2124
2210
2287
2385
2344
2147
2318
2085
2082
2064
2354
2174
2196
2185
2332
2305
2038
2220
2230
2118
2262
2050
2083
2289
2239
2310
2058
2070
2053
2046
2191
2391
2232
2094
2265
2400
2248
2075
2123
2022
2396
2236
2299
2069
2377
2208
2172
2363
2165
2261
2252
2114
2112
2394
2267
2364
2030
2389
2370
2194
2256
2290
2130
2152
2356
2254
2360
2383
2243
2209
2238
2393
2350
2277
2381
2154
2060
2189
2113
2129
2091
2167
2323
2049
2322
2264
2023
2218
2227
2274
2390
2320
2034
2225
2386
2192
2362
2168
2268
2110
2215
2127
2321
2237
2171
2345
2021
2048
2228
2137
2173
2059
2338
2366
2096
2316
2300
2104
2330
2353
2179
2378
2416
2339
2063
2329
2150
2319
2047
2025
2026
2399
2080
2351
2180
2295
2327
2051
2293
2040
2120
2337
2197
2148
2121
2163
2376
2334
2073
2187
2284
2055
2039
2347
2392
2246
2072
2184
2266
2044
2108
2244
2317
2158
2105
2128
2169
2369
2067
2324
2462
2219
2086
2099
2275
2335
2057
2156
2357
2229
2041
2162
2078
2136
2314
2090
2288
2031
2071
2251
2092
2106
2301
2343
2388
2111
2211
2164
2303
2315
2245
2224
2375
2012
2397
2157
2182
2095
2160
2119
2291
2263
2028
2286
2278
2241
2336
2255
2349
2281
2188
2195
2142
2135
2149
2066
2346
2233
2161
2309
2341
2178
2447
2029
2068
2283
2062
2365
2279
2250
2126
2088
2306
2212
2138
2045
2052
2122
2087
2272
2384
2183
2153
2326
2372
2331
2273
2139
2101
2374
2617
2231
2358
2221
2402
2176
2115
2098
2379
2193
2144
2226
2258
2097
2234
2145
2675
2280
2676
2166
2036
2132
2116
2307
2359
2027
2271
2008
2009
2010
2249
2019
2297
2401
2312
2583
2587
2582
2589
2621
2698
2699
2702
2703
2711
2783
"""

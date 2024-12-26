# -*- coding:utf-8 -*-
# Filename: locust_shape.py
# Description: 
# Author: zhaobing.liu@outlook.com
# Created: 2024/7/11
# Last Modified: 2024/7/11
import math

from locust import LoadTestShape


class MyCustomShape(LoadTestShape):
    # 阶梯层数
    spawn_count = 30
    # 每层阶梯新增用户数
    spawn_rate = 2
    # 每层阶梯持续时间
    step_time = 60 * 2

    # 总时间
    time_limit = step_time * spawn_count

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            current_step = math.floor(run_time / self.step_time) + 1
            return current_step * self.spawn_rate, self.spawn_rate
        return None

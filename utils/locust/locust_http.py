# -*- coding:utf-8 -*-
# Filename: locust_http.py
# Description: 
# Author: zhaobing.liu@outlook.com
# Created: 2024/7/11
# Last Modified: 2024/7/11
import copy
import time

from locust import task

from utils.data import generate_trace_id
from utils.locust.locust_base import *
from api.client.client import HTTPStream


class HTTPStreamUser(HTTPUser):

    @task
    def http_stream_task(self):
        http_stream = HTTPStream(address=self.host, method=self.method, headers=self.headers)
        trace_id = generate_trace_id()
        question = self.questions.get()

        payload = copy.deepcopy(self.request_payload_json)
        _question = self.question if self.question else question
        replace_str(payload, "QUESTION", _question)
        replace_str(payload, "TRACEID", trace_id)
        start_time = time.time()
        response_bytes, costs, e = http_stream(**payload)
        response = []
        buffer = b""
        for r in response_bytes:
            buffer += r
            try:
                resp = buffer.decode("UTF-8")
                response.append(resp)
                buffer = b""
            except Exception as e:
                continue
        if self.record_first:
            if costs:
                self.environment.events.request.fire(
                    request_type=self.method,
                    start_time=start_time,
                    response=response,
                    response_length=len(response),
                    exception=Exception(f"first cost >= {self.first_line} ms") if costs[0] >= self.first_line else None,
                    context=None,
                    name=f"/{self.parent}/{self.title}/first",
                    response_time=costs[0],
                )
            else:
                self.environment.events.request.fire(
                    request_type=self.method,
                    start_time=start_time,
                    response=response,
                    response_length=len(response),
                    exception=Exception(f"no response chunk return"),
                    context=None,
                    name=f"/{self.parent}/{self.title}/first",
                    response_time=0,
                )

        save_locust_log_local(report_filename=self.report, trace_id=trace_id, start_time=start_time,
                              costs=costs, responses_json=response, payload=payload)

        self.questions.put(question)
        return start_time, response, costs

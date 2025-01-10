# -*- coding:utf-8 -*-
# Filename: locust_base.py
# Description: 
# Author: zhaobing.liu@outlook.com
# Created: 2024/7/11
# Last Modified: 2024/7/11
# -*- coding:utf-8 -*-
import logging
import json
import os
import queue
import threading
from asyncio import Semaphore
from pathlib import Path
from datetime import datetime as dt

import random
import jsonlines
import jsonpath
from locust import User
from locust import events
from locust.exception import LocustError

from utils.data import load_data_from_xlsx, get_jsonl, generate_job_instance_id, check_http_url
from main import BASE_DIR, LOG_DIR


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--test-config", type=str, help="测试配置")
    parser.add_argument("--question", type=str, default="", help="问题")
    parser.add_argument("--record-first", type=bool, default=False, help="是否记录测试端首帧响应耗时")
    parser.add_argument("--record-first-chunk", type=bool, default=False, help="是否记录服务端首帧响应耗时")
    parser.add_argument("--record-first-chunk-model", type=bool, default=False, help="是否记录模型端首帧响应耗时")


class ParseUser(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_config = self.environment.parsed_options.test_config
        self.question = self.environment.parsed_options.question
        self.record_first = self.environment.parsed_options.record_first
        self.record_first_chunk = self.environment.parsed_options.record_first_chunk
        self.record_first_chunk_model = self.environment.parsed_options.record_first_chunk_model
        if not self.record_first and not self.record_first_chunk and not self.record_first_chunk_model:
            self.record_first = True
        self.record_all = False

        with open(os.path.join(BASE_DIR, self.test_config), "r") as f:
            self.config = json.load(f)

        self.title = self.config.get("title", "grpc_stream")
        self.parent = self.config.get("parent", "GRPCStreamUser")
        self.method = self.config.get("method", "GRPC")
        self.url = self.config.get("url", "")
        self.first_line = self.config.get("first_line", 300)
        self.all_line = self.config.get("all_line", 1000)
        self.headers = self.config.get("request_headers", {"Content-Type": "application/json; charset=utf-8"})
        self.request_payload_json = self.config.get("request_payload", {})
        self.jsonpath_expression = self.config.get("jsonpath_expression", [])
        self.test_case_file = self.config.get("test_case_file", "")

        self.cases_from_file = self.config.get("test_case_list", [])

        if not self.cases_from_file:
            self.test_case_file = os.path.join(BASE_DIR, self.test_case_file)

            if self.test_case_file.endswith(".jsonl"):
                self.cases_from_file = get_jsonl(self.test_case_file)
            elif self.test_case_file.endswith(".xlsx"):
                self.cases_from_file = load_data_from_xlsx(self.test_case_file, self.config.get("sheet_name", "Sheet1"))
            else:
                self.cases_from_file = []

        self.test_cases = queue.Queue()
        random.shuffle(self.cases_from_file)
        for test_case in self.cases_from_file:
            self.test_cases.put(test_case)

        self.questions = queue.Queue()
        for test_case in self.cases_from_file:
            self.questions.put(generate_query(test_case, self.jsonpath_expression))

        _user_count = self.environment.runner.user_count
        _today = dt.now().strftime("%Y%m%d")
        self.session_id = f"LOCUST.{generate_job_instance_id()}.{self.parent}.{self.title}.{_user_count + 1}"
        self.report = os.path.join(LOG_DIR, "locust", self.parent, self.title, _today, f"{self.session_id}.jsonl")
        Path(self.report).parent.mkdir(parents=True, exist_ok=True)


class HTTPUser(ParseUser):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not check_http_url(self.host):
            raise LocustError(f"You must specify a valid HTTP url. E.g. http://127.0.0.1:50051/api/v1/chat")


def save_locust_log_local(
        report_filename: str,
        trace_id: str,
        start_time: float,
        costs: list,
        responses_json: list | dict,
        payload: dict,
        answers: list = [],
        **kwargs,
):
    _log = dict(
        trace_id=trace_id,
        request_time=dt.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S.%f"),
        response_time=[
            dt.fromtimestamp(start_time + sum(costs[:i + 1]) / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")
            for i, _ in enumerate(costs)
        ],
        costs=costs,
        answers=answers,
        response=responses_json,
        request=payload,
        **kwargs,
    )
    with threading.Lock():
        with jsonlines.open(report_filename, "a") as jf:
            jf.write(_log)
    return _log


@events.test_start.add_listener
def _(environment, **kw):
    print(f"Custom argument supplied: {environment.parsed_options.test_config}")


def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()


all_locusts_spawned = Semaphore()
events.spawning_complete.add_listener(on_hatch_complete)


def get_jsonpath_value(json_obj, jsonpath_expr):
    if result := jsonpath.jsonpath(json_obj, jsonpath_expr):
        return "".join([str(item) for item in result])
    return jsonpath_expr


def generate_query(json_obj, jsonpath_expressions):
    return "".join([get_jsonpath_value(json_obj, jsonpath_expr) for jsonpath_expr in jsonpath_expressions])


def replace_str(data, old_str: str, new_str: str):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                if v == old_str:
                    data[k] = new_str
            else:
                replace_str(v, old_str, new_str)
    elif isinstance(data, list):
        for i in range(len(data)):
            if isinstance(data[i], str):
                if data[i] == old_str:
                    data[i] = new_str
            else:
                replace_str(data[i], old_str, new_str)


def calculate_first_sentence_cost(_responses: list, _costs: list) -> int:
    if not _responses:
        return 0
    for index, item in enumerate(_responses):
        try:
            response_json = json.loads(item.removeprefix("data:"))
            pre_tts = "".join(jsonpath.jsonpath(response_json, "$.choices..delta.content"))
            if pre_tts:
                for tts in pre_tts:
                    if tts in ["。", "？", "！", "，", "；", "：", "、", "”", ",", ".", "!", "?", ";", ":"]:
                        return sum(_costs[:index + 1])
        except Exception as e:
            continue
    return sum(_costs)

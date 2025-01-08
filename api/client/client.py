# -*- coding:utf-8 -*-
import math
import os
import abc
import time
import json
import base64
import logging
import typing as t

import grpc
import requests
from google.protobuf import json_format


def mock_job_instance_id():
    return f'{time_strf_now()}{base64.b32encode(os.urandom(5)).decode("ascii")}'


def mock_trace_id():
    return f'L{mock_job_instance_id()}@ai-test.com.cn'


def time_strf_now():
    """返回当前时间格式"""
    return time.strftime("%Y%m%d%H%M%S")


class GRPC(abc.ABC):
    stub_class = None

    def __init__(self, address: str, insecure: bool = True):
        if not self.stub_class:
            raise ValueError(f"invalid stub class: [{self.stub_class}]")
        self.address = address
        options = [
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ]
        try:
            if insecure:
                self.channel = grpc.insecure_channel(address, options=options)
            else:
                self.channel = grpc.secure_channel(address, credentials=grpc.ssl_channel_credentials(), options=options)
            self.stub = self.stub_class(self.channel)
            logging.info(f"dial grpc address success: {address}")
        except Exception as e:
            logging.error(f"dial grpc address failed: {address} {e}")
            self.channel = None
            self.stub = None

    def __del__(self):
        if self.channel is not None:
            try:
                self.channel.close()
            except Exception as e:
                logging.warning(f"close grpc channel failed: {e}")

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    @staticmethod
    def yield_message(message):
        yield message

    @abc.abstractmethod
    def call(self, *args, **kwargs):
        raise NotImplementedError("call function not implemented")


class HTTP(abc.ABC):
    def __init__(self, address: str):
        self.address = address
        self._headers = None
        self.token = None
        self.cookies = None

    @abc.abstractmethod
    def get_headers(self, *args, **kwargs):
        raise NotImplementedError("get_headers function not implemented")

    @property
    def headers(self):
        if not self._headers:
            self._headers = self.get_headers()
        return self._headers

    def request(self, path: str = "", url: str = "", headers=None, *args, **kwargs) -> t.Tuple[
        t.List | dict | str, int, Exception | None]:
        if p := kwargs.get("params"):
            if isinstance(p, dict):
                logging.info(f'request.params => {json.dumps(p, ensure_ascii=False)}')
            else:
                logging.info(f'request.params => {p}')

        if j := kwargs.get("json"):
            if isinstance(j, dict):
                logging.info(f'request.json => {json.dumps(j, ensure_ascii=False)}')
            else:
                logging.info(f'request.json => {j}')
        if d := kwargs.get("data"):
            if isinstance(d, dict):
                logging.info(f'request.data => {json.dumps(d, ensure_ascii=False)}')
            else:
                logging.info(f'request.data => {d}')
        start_time_perfcount = time.perf_counter()
        response = requests.request(
            url=self.address + path if path else url,
            headers=headers if headers else self.headers,
            *args,
            **kwargs
        )
        end_time_perfcount = time.perf_counter()
        cost = (end_time_perfcount - start_time_perfcount) * 1000
        self.cookies = response.cookies
        logging.info(f'{kwargs.get("method")} {response.status_code} => {path if path else url}')
        logging.info(repr(f'response => {response.text if response.text.__len__() <= 2048 else response.text[:100]}'))
        if response.status_code != 200:
            logging.warning(f'response.code => {response.status_code}')
        try:
            return response.json(), math.floor(cost), None
        except Exception as e:
            return response.content.decode("UTF-8"), math.floor(cost), e


class HTTPStream:
    """单次请求 流式返回"""

    def __init__(self, address: str, method: str, **kwargs):
        self.address = address
        self.method = method.upper()
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs) -> t.Tuple[t.List[bytes], t.List[int], Exception | None]:
        logging.info(f"request [{self.method}] [{kwargs}] to {self.address}")
        response_content, costs = [], []
        try:
            start_perf_counter = time.perf_counter()
            responses = requests.request(method=self.method, url=self.address, stream=True, verify=False, json=kwargs,
                                         **self.kwargs)
            for res in responses.iter_content(chunk_size=10240):
                this_time = time.perf_counter()
                costs.append(int(1000 * (this_time - start_perf_counter)))
                start_perf_counter = this_time
                response_content.append(res)
            return response_content, costs, None
        except Exception as e:
            logging.error(f"request [{self.method}] [{kwargs}] to {self.address} failed: {e}")
            return response_content, costs, e


class GRPCStream:
    """单次请求 流式返回"""

    def __init__(self, address: str, stub_class):
        self.address = address
        self.exception = None
        try:
            self.channel = grpc.insecure_channel(address, options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ])
            self.stub = stub_class(self.channel)
            logging.info(f"dial grpc address success: {address}")
        except Exception as e:
            logging.error(f"dial grpc address failed: {address} {e}")
            self.channel = None
            self.stub = None
            self.exception = e

    def __del__(self):
        if self.channel is not None:
            try:
                self.channel.close()
            except Exception as e:
                logging.warning(f"close grpc channel failed: {e}")

    def __call__(self, request_method: t.Callable, request_message) -> t.Tuple[
        t.List[t.Any], t.List[int], Exception | None]:
        request_message_json = json.dumps(json_format.MessageToDict(request_message), ensure_ascii=False)
        logging.info(f"request [GRPC] [{request_message_json}] to {self.address}")
        response_content, costs = [], []
        if self.exception:
            logging.error(f"request [GRPC] [{request_message_json}] to {self.address} failed: {self.exception}")
            return response_content, costs, self.exception
        try:
            start_perf_counter = time.perf_counter()
            responses = request_method(self.stub, request_message)
            for resp in responses:
                this_time = time.perf_counter()
                costs.append(int(1000 * (this_time - start_perf_counter)))
                start_perf_counter = this_time
                response_content.append(resp)
            return response_content, costs, None
        except Exception as e:
            logging.error(f"request [GRPC] [{request_message_json}] to {self.address} failed: {e}")
            return response_content, costs, e

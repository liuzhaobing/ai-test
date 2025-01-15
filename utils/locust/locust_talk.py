# -*- coding:utf-8 -*-
import copy
import time

from locust import task
from google.protobuf import json_format

import utils.data
import utils.util
from utils.locust.locust_base import *
from utils.locust.locust_grpc import GRPCUser
from api.proto.svpb import talk_pb2, talk_pb2_grpc
from api.client.interceptor_client import StreamStreamGrpcInterceptor


class StreamTalkGrpcUser(GRPCUser):
    interceptor = StreamStreamGrpcInterceptor
    stub_class = talk_pb2_grpc.TalkStub
    insecure = False

    @task
    def grpc_stream_task(self):
        trace_id = utils.util.mock_trace_id()
        question = self.questions.get()

        payload = copy.deepcopy(self.request_payload_json)
        _question = self.question if self.question else question
        replace_str(payload, "QUESTION", _question)
        replace_str(payload, "SESSIONID", self.session_id)
        replace_str(payload, "TRACEID", trace_id)
        req = json_format.ParseDict(payload, talk_pb2.TalkRequest())

        start_time, costs, responses_json, start_perf_counter = time.time(), [], [], time.perf_counter()
        responses = self.stub.StreamingTalk(self.yield_message(req))

        for response in responses:
            this_time = time.perf_counter()
            cost = 1000 * (this_time - start_perf_counter)
            costs.append(cost)
            start_perf_counter = this_time
            response_json = json_format.MessageToDict(response)
            responses_json.append(response_json)

        sources = jsonpath.jsonpath(responses_json, "$..source")
        answers = jsonpath.jsonpath(responses_json, "$..tts..text")

        self.environment.events.request.fire(
            request_type="Receive",
            start_time=start_time,
            response=responses_json,
            response_length=len(sources),
            exception=None,
            context=None,
            name=f"source/{sources[-1] if sources else 'None'}",
            response_time=costs[0] if costs else 0,
        )

        first_exception = Exception(f"first cost >= {self.first_line} ms") if costs[0] >= self.first_line else None
        all_exception = Exception(f"all cost >= {self.all_line} ms") if sum(costs) >= self.all_line else None

        if self.record_first:
            self.environment.events.request.fire(
                request_type=self.method,
                start_time=start_time,
                response=responses_json,
                response_length=len(responses_json),
                exception=first_exception,
                context=None,
                name=f"/{self.parent}/{self.title}/first",
                response_time=costs[0] if costs else 0,
            )

        if self.record_all:
            self.environment.events.request.fire(
                request_type=self.method,
                start_time=start_time,
                response=responses_json,
                response_length=len(responses_json),
                exception=all_exception,
                context=None,
                name=f"/{self.parent}/{self.title}/all",
                response_time=sum(costs),
            )

        if all_exception:
            save_locust_log_local(
                report_filename=self.report.replace(".jsonl", ".error.jsonl"),
                trace_id=trace_id,
                start_time=start_time,
                answers=answers,
                costs=costs,
                responses_json=responses_json,
                payload=payload,
                error="timeout",
            )

        save_locust_log_local(
            report_filename=self.report,
            trace_id=trace_id,
            start_time=start_time,
            answers=answers,
            costs=costs,
            responses_json=responses_json,
            payload=payload,
        )

        self.questions.put(question)
        return start_time, responses_json, costs

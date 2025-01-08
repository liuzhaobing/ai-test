# -*- coding:utf-8 -*-
import copy
import time
import uuid

from locust import task

from utils.locust.locust_base import *
from utils.locust.locust_grpc import GRPCUser
from api.client.interceptor_client import UnaryStreamGrpcInterceptor
from api.client.fragment_tts_client import fragment_tts_pb2_grpc, tts_request


class StreamingSpeechSynthesizeGrpcUser(GRPCUser):
    interceptor = UnaryStreamGrpcInterceptor
    stub_class = fragment_tts_pb2_grpc.FragmentTextToSpeechStub
    insecure = False

    @task
    def grpc_stream_task(self):
        trace_id = uuid.uuid4().hex
        question = self.questions.get()

        payload = copy.deepcopy(self.request_payload_json)
        _question = self.question if self.question else question
        replace_str(payload, "QUESTION", _question)
        replace_str(payload, "TRACEID", trace_id)

        start_time, costs, responses_json, start_perf_counter = time.time(), [], [], time.perf_counter()
        responses = self.stub.StreamingSpeechSynthesize(tts_request(**payload))

        for response in responses:
            if response.body.speech:
                this_time = time.perf_counter()
                cost = 1000 * (this_time - start_perf_counter)
                costs.append(cost)
                start_perf_counter = this_time

        if self.record_first:
            self.environment.events.request.fire(
                request_type=self.method,
                start_time=start_time,
                response=responses_json,
                response_length=len(responses_json),
                exception=Exception(f"first cost >= {self.first_line} ms") if costs[0] >= self.first_line else None,
                context=None,
                name=f"/{self.parent}/{self.title}/first",
                response_time=costs[0],
            )

        if self.record_all:
            self.environment.events.request.fire(
                request_type=self.method,
                start_time=start_time,
                response=responses_json,
                response_length=len(responses_json),
                exception=Exception(f"all cost >= {self.all_line} ms") if sum(costs) >= self.all_line else None,
                context=None,
                name=f"/{self.parent}/{self.title}/all",
                response_time=sum(costs),
            )

        save_locust_log_local(report_filename=self.report, trace_id=trace_id, start_time=start_time,
                              costs=costs, responses_json=responses_json, payload=payload)

        self.questions.put(question)
        return start_time, responses_json, costs

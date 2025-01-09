# -*- coding:utf-8 -*-
import json
import logging
import math
import os.path
import time
import threading

from google.protobuf import json_format
from api.client.client import GRPC
from api.proto.asrctrl import asrctrl_pb2_grpc, asrctrl_pb2
import utils.util as util
from main import BASE_DIR

lock = threading.Lock()


def recognition_request(
        agent_id: int,
        language: str,
        dialect: str,
        vendor: str,
        audio_bytes: bytes,
        stream_flag: int = 0,
        trace_id: str = util.mock_trace_id(),
) -> asrctrl_pb2.RecognitionRequest:
    return asrctrl_pb2.RecognitionRequest(
        common_req_info=asrctrl_pb2.CommonReqInfo(
            guid=trace_id,
            timestamp=math.floor(time.time()),
            version="1.0",
            tenant_id=trace_id,
            user_id=trace_id,
            robot_id=trace_id,
            robot_type="",
            service_code="ginger",
            seq="",
            root_guid=""
        ),
        body=asrctrl_pb2.Body(
            type=asrctrl_pb2.Body.Type.STREAMING,
            sid="",
            app_type="",
            tag="",
            stream_flag=stream_flag,
            option={
                "returnDetail": "true",
                "recognizeOnly": "true",
                "tstAgentId": f"{agent_id}"
            },
            data=asrctrl_pb2.Body.Data(
                rate=16000,
                format="pcm",
                account="",
                language=f"{language}",
                dialect=f"{dialect}",
                vendor=f"{vendor}",
                channel=0,
                duration=0,
                flag=0,
                speech=audio_bytes,
            )
        ),
        extra=asrctrl_pb2.Extra(),
        version=""
    )


def streaming_send_request(
        audio_file: str,
        buffer_size: int = 1280,
        *args,
        **kwargs
):
    with lock:
        with open(audio_file, "rb") as f:
            if audio_file.endswith(".wav"):
                f.read(44)
            cnt = 0
            stream_flag = 0
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                if cnt == 40:
                    stream_flag = 2
                    time.sleep(0.2)
                yield recognition_request(audio_bytes=data, stream_flag=stream_flag, *args, **kwargs)
                cnt += 1


class StreamingRecognizeGRPC(GRPC):
    stub_class = asrctrl_pb2_grpc.SpeechStub

    def call(self, *args, **kwargs):
        try:
            responses = self.stub.StreamingRecognize(streaming_send_request(*args, **kwargs))
            responses_json = [json_format.MessageToDict(response) for response in responses]
            logging.info(json.dumps(responses_json, ensure_ascii=False))
            return responses_json
        except Exception as e:
            logging.info(f"grpc to {self.address} error: {e}")
            return []


if __name__ == '__main__':
    speech = StreamingRecognizeGRPC(address="harix-skill-asr.wispirit.raysengine.com:9443", insecure=False)
    speech_result = speech(
        agent_id=2732,
        language="CH",
        dialect="zh",
        vendor="CloudMinds",
        audio_file=os.path.join(BASE_DIR, "dataset/asr/wav/20241223_863958041682845_20241223232741176.wav"),
    )

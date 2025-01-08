# -*- coding:utf-8 -*-
import time
import typing as t
import logging
import os.path
import uuid
import wave

from google.protobuf import json_format

from api.client.client import GRPC
from api.proto.tts import fragment_tts_pb2, fragment_tts_pb2_grpc
from main import LOG_DIR


def get_common_req_info(
        version: str = "3.2.1",
        tenant_id: str = "cloud_pepper",
        user_id: str = "3038",
        robot_id: str = "862851030073038",
        robot_type: str = "pepper",
        service_code: str = "ginger",
        trace_id: str = uuid.uuid4().hex,
):
    return fragment_tts_pb2.CommonReqInfo(
        guid=trace_id[:16],
        timestamp=int(time.time() * 1000),
        version=version,
        tenant_id=tenant_id,
        user_id=user_id,
        robot_id=robot_id,
        robot_type=robot_type,
        service_code=service_code,
        root_guid=trace_id,
    )


def tts_request(
        text: str = "今天天气真不错",
        vendor: t.Literal["CloudMinds", "Ali"] = "CloudMinds",
        trace_id: str = uuid.uuid4().hex,
        **kwargs,
):
    try:
        if vendor == "Ali":
            return fragment_tts_pb2.FragmentTTSRequest(
                common_req_info=get_common_req_info(trace_id=trace_id),
                body=fragment_tts_pb2.FragmentTTSRequest.Body(
                    text=text,
                    vendor="Ali",
                    speaker="jielidou",
                    volume="50",
                ),
            )
        elif vendor == "CloudMinds":
            return fragment_tts_pb2.FragmentTTSRequest(
                common_req_info=get_common_req_info(trace_id=trace_id),
                body=fragment_tts_pb2.FragmentTTSRequest.Body(
                    text=text,
                    vendor="CloudMinds",
                    language="zh",
                    speaker="DaXiaoQing",
                    rate="16000",
                    pitch="medium",
                    volume="3",
                    speed="2",
                ),
            )
        return None
    except Exception as e:
        logging.error(f"make {__name__} error: {e}")
        return None


class StreamingSpeechSynthesizeGRPC(GRPC):
    stub_class = fragment_tts_pb2_grpc.FragmentTextToSpeechStub

    @staticmethod
    def pcm_to_wav(pcm_data, wav_file, channels=1, bits=16, sample_rate=16000):
        if bits % 8 != 0:
            raise ValueError("bits % 8 must == 0. now bits:" + str(bits))
        with wave.open(wav_file, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(bits // 8)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_data)

    def call(self, *args, **kwargs):
        filename = kwargs.get("filename")
        if not filename:
            raise ValueError("please input a filename to be saved as .wav")
        req = tts_request(*args, **kwargs)
        logging.info(json_format.MessageToDict(req))
        try:
            responses = self.stub.StreamingSpeechSynthesize(req)
            debug_info = ""
            text_after = ""
            pcm = b""
            for r in responses:
                if r.body.text:
                    text_after += r.body.text
                if r.body.speech:
                    pcm += r.body.speech
            self.pcm_to_wav(pcm, filename)
            return debug_info, text_after

        except Exception as e:
            logging.error(f"grpc to {self.address} error: {e}")
            return None


if __name__ == '__main__':
    tts_client = StreamingSpeechSynthesizeGRPC(address="harix-skill-tts.wispirit.raysengine.com:9443", insecure=False)
    res = tts_client(vendor="Ali", text="电话号码：+86 8888 8888", filename=os.path.join(LOG_DIR, "a.wav"))
    print(res)

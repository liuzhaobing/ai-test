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

    def get_common_req_info(
            self,
            version: str = "3.2.1",
            tenant_id: str = "cloud_pepper",
            user_id: str = "3038",
            robot_id: str = "862851030073038",
            robot_type: str = "pepper",
            service_code: str = "ginger",
    ):
        root_guid = uuid.uuid4().hex
        return fragment_tts_pb2.CommonReqInfo(
            guid=root_guid[:16],
            timestamp=int(time.time() * 1000),
            version=version,
            tenant_id=tenant_id,
            user_id=user_id,
            robot_id=robot_id,
            robot_type=robot_type,
            service_code=service_code,
            root_guid=root_guid,
        )

    def tts_request(
            self,
            text: str = "今天天气真不错",
            vendor: t.Literal["CloudMinds", "Ali"] = "CloudMinds",
            language: t.Literal["zh", "en"] = "zh",
            speaker: t.Literal["DaXiaoQing"] = "DaXiaoQing",
            rate: str = "16000",
            pitch: str = "medium",
            volume: str = "3",
            speed: str = "2",
            option: dict = {},
            **kwargs,
    ):
        try:
            return fragment_tts_pb2.FragmentTTSRequest(
                common_req_info=self.get_common_req_info(),
                body=fragment_tts_pb2.FragmentTTSRequest.Body(
                    text=text,
                    vendor=vendor,
                    language=language,
                    speaker=speaker,
                    rate=rate,
                    pitch=pitch,
                    volume=volume,
                    option=option,
                    speed=speed,
                ),
            )
        except Exception as e:
            logging.error(f"make {__name__} error: {e}")
            return None

    def call(self, *args, **kwargs):
        filename = kwargs.get("filename")
        if not filename:
            raise ValueError("please input a filename to be saved as .wav")
        req = self.tts_request(*args, **kwargs)
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
    res = tts_client(text="电话号码：+86 8888 8888", filename=os.path.join(LOG_DIR, "a.wav"))
    print(res)

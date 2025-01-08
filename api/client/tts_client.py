# -*- coding:utf-8 -*-
import logging
import os.path
import wave

from google.protobuf import json_format

from api.client.client import GRPC
from api.proto.tts import tts_pb2, tts_pb2_grpc
from main import LOG_DIR


class TtsGRPC(GRPC):
    stub_class = tts_pb2_grpc.CloudMindsTTSStub

    @staticmethod
    def pcm_to_wav(pcm_data, wav_file, channels=1, bits=16, sample_rate=16000):
        if bits % 8 != 0:
            raise ValueError("bits % 8 must == 0. now bits:" + str(bits))
        with wave.open(wav_file, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(bits // 8)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_data)

    def tts_request(self,
                    text: str = "今天天气真不错",
                    speed: str = "2",
                    volume: str = "3",
                    pitch: str = "medium",
                    emotions: str = "Gentle",
                    parameter_speaker_name: str = "DaXiaoFang",
                    parameter_digital_person: str = "SweetGirl",
                    parameter_flag=None,
                    **kwargs):
        if parameter_flag is None:
            parameter_flag = {
                "expression": "true",
                "mouth": "true",
                "movement": "true"
            }
        try:
            return tts_pb2.TtsReq(text=text,
                                  speed=speed,
                                  volume=volume,
                                  pitch=pitch,
                                  emotions=emotions,
                                  parameter_speaker_name=parameter_speaker_name,
                                  parameter_digital_person=parameter_digital_person,
                                  parameter_flag=parameter_flag)
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
            responses = self.stub.Call(req)
            debug_info = ""
            text_after = ""
            pcm = b""
            for r in responses:
                if r.debug_info.info:
                    if r.debug_info.debug_type == "pron":
                        debug_info += r.debug_info.info
                    elif r.debug_info.debug_type == "norm":
                        text_after += r.debug_info.info
                    elif r.debug_info.debug_type == "word":
                        pass
                    elif r.debug_info.debug_type == "g2pw_pron":
                        pass
                if r.synthesized_audio.pcm:
                    pcm += r.synthesized_audio.pcm

            self.pcm_to_wav(pcm, filename)
            return debug_info, text_after

        except Exception as e:
            logging.error(f"grpc to {self.address} error: {e}")
            return None


if __name__ == '__main__':
    tts_client = TtsGRPC(address="harix-skill-tts.wispirit.raysengine.com:9443", insecure=False)
    res = tts_client(text="电话号码：+86 8888 8888", filename=os.path.join(LOG_DIR, "a.wav"))
    print(res)

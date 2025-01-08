# -*- coding:utf-8 -*-
import json
import logging

from google.protobuf import json_format
from api.client.client import GRPC
from api.proto.svpb import talk_pb2, talk_pb2_grpc
import utils.util as util


class TalkGRPC(GRPC):
    stub_class = talk_pb2_grpc.TalkStub

    def call(self, *args, **kwargs):
        req = self.talk_request(*args, **kwargs)
        logging.info(json.dumps(json_format.MessageToDict(req), ensure_ascii=False))
        try:
            response = self.stub.Talk(req)
            response_json = json_format.MessageToDict(response)
            logging.info(json.dumps(response_json, ensure_ascii=False))
            return response_json
        except Exception as e:
            logging.error(f"grpc to {self.address} error: {e}")
            return {}

    def talk_request(self,
                     is_full: bool = True,
                     lang: str = "CH",
                     text: str = "现在几点了",
                     agent_id: int = 1,
                     session_id: str = util.mock_trace_id(),
                     question_id: str = util.mock_trace_id(),
                     event_type: int = 0,
                     env_info: dict = {"devicetype": "ginger"},
                     robot_id: str = "5C1AEC03573747D",
                     tenant_code: str = "cloudminds",
                     position: str = "104.061,30.5444",
                     version: str = "v3",
                     inputContext: str = "",
                     is_ha: bool = False,
                     test_mode: bool = True):

        try:
            return talk_pb2.TalkRequest(is_full=is_full,
                                        agent_id=agent_id,
                                        session_id=session_id,
                                        question_id=question_id,
                                        event_type=event_type,
                                        env_info=env_info,
                                        robot_id=robot_id,
                                        tenant_code=tenant_code,
                                        position=position,
                                        version=version,
                                        inputContext=inputContext,
                                        is_ha=is_ha,
                                        test_mode=test_mode,
                                        asr=talk_pb2.Asr(lang=lang, text=text))
        except Exception as e:
            logging.error(f"make {__name__} error: {e}")
            return None


class StreamTalkGRPC(TalkGRPC):
    def call(self, *args, **kwargs):

        req = self.talk_request(*args, **kwargs)
        logging.info(json.dumps(json_format.MessageToDict(req), ensure_ascii=False))
        try:
            responses = self.stub.StreamingTalk(self.yield_message(req))
            responses_json = [json_format.MessageToDict(response) for response in responses]
            logging.info(json.dumps(responses_json, ensure_ascii=False))
            return responses_json
        except Exception as e:
            logging.error(f"grpc to {self.address} error: {e}")
            return []


if __name__ == '__main__':
    talk = TalkGRPC(address="sv-grpc.wispirit.raysengine.com:9443", insecure=False)
    talk_result = talk(text="现在几点了", agent_id=1, robot_id="80000000000050")

    stream_talk = StreamTalkGRPC(address="sv-grpc.wispirit.raysengine.com:9443", insecure=False)
    stream_talk_result = stream_talk(text="介绍一下马斯克", agent_id=1, robot_id="80000000000050")

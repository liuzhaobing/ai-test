# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: api/proto/asrctrl/asrctrl.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1f\x61pi/proto/asrctrl/asrctrl.proto\x12\tskill.asr\x1a\x1cgoogle/protobuf/struct.proto\"\xfa\x03\n\x04\x42ody\x12\"\n\x04type\x18\t \x01(\x0e\x32\x14.skill.asr.Body.Type\x12\x0b\n\x03sid\x18\n \x01(\t\x12\x10\n\x08\x61pp_type\x18\x0b \x01(\t\x12\x0b\n\x03tag\x18\x0c \x01(\t\x12\x13\n\x0bstream_flag\x18\r \x01(\x05\x12+\n\x06option\x18\x0e \x03(\x0b\x32\x1b.skill.asr.Body.OptionEntry\x12\"\n\x04\x64\x61ta\x18\x0f \x01(\x0b\x32\x14.skill.asr.Body.Data\x12\x13\n\x0bneed_wakeup\x18\x10 \x01(\x08\x1a-\n\x0bOptionEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a\xd5\x01\n\x04\x44\x61ta\x12\x0c\n\x04rate\x18\x01 \x01(\x05\x12\x0e\n\x06\x66ormat\x18\x02 \x01(\t\x12\x0f\n\x07\x61\x63\x63ount\x18\x03 \x01(\t\x12\x10\n\x08language\x18\x04 \x01(\t\x12\x0f\n\x07\x64ialect\x18\x05 \x01(\t\x12\x0e\n\x06vendor\x18\x06 \x01(\t\x12\x0f\n\x07\x63hannel\x18\x07 \x01(\x05\x12\x10\n\x08\x64uration\x18\x08 \x01(\x05\x12\x0c\n\x04\x66lag\x18\t \x01(\x05\x12\x11\n\x06speech\x18\n \x01(\x0cR\x01-\x12\'\n\nmulAsrLang\x18\x0b \x01(\x0e\x32\x13.skill.asr.AsrsLang\" \n\x04Type\x12\t\n\x05\x42LOCK\x10\x00\x12\r\n\tSTREAMING\x10\x01\"\x98\x01\n\x12RecognitionRequest\x12\x31\n\x0f\x63ommon_req_info\x18\x01 \x01(\x0b\x32\x18.skill.asr.CommonReqInfo\x12\x1d\n\x04\x62ody\x18\x02 \x01(\x0b\x32\x0f.skill.asr.Body\x12\x1f\n\x05\x65xtra\x18\x03 \x01(\x0b\x32\x10.skill.asr.Extra\x12\x0f\n\x07version\x18\x04 \x01(\t\"\xe3\x01\n\x13RecognitionResponse\x12\x31\n\x0f\x63ommon_rsp_info\x18\x01 \x01(\x0b\x32\x18.skill.asr.CommonRspInfo\x12/\n\x0e\x64\x65tail_message\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x10\n\x08is_noise\x18\x03 \x01(\x08\x12\x13\n\x0bquestion_id\x18\x04 \x01(\t\x12\x11\n\tis_wakeup\x18\x05 \x01(\x08\x12.\n\rwakeup_status\x18\x06 \x01(\x0e\x32\x17.skill.asr.WakeupStatus\":\n\x08\x43heckCmd\x12\x0e\n\x06\x61\x63tion\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\x05\x12\x0e\n\x06\x63mdDsc\x18\x03 \x01(\t\"\xa7\x01\n\x14TextRecognizeRequest\x12\x31\n\x0f\x63ommon_req_info\x18\x01 \x01(\x0b\x32\x18.skill.asr.CommonReqInfo\x12*\n\x04\x62ody\x18\x02 \x01(\x0b\x32\x1c.skill.asr.TextRecognizeBody\x12\x1f\n\x05\x65xtra\x18\x03 \x01(\x0b\x32\x10.skill.asr.Extra\x12\x0f\n\x07version\x18\x04 \x01(\t\"U\n\x11TextRecognizeBody\x12\x10\n\x08\x61pp_type\x18\x01 \x01(\t\x12\x0b\n\x03txt\x18\x02 \x01(\t\x12\x10\n\x08language\x18\x03 \x01(\t\x12\x0f\n\x07\x64ialect\x18\x04 \x01(\t\"2\n\x15TextRecognizeResponse\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0b\n\x03msg\x18\x02 \x01(\t\"\xc1\x01\n\rCommonReqInfo\x12\x0c\n\x04guid\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\x12\x0f\n\x07version\x18\x03 \x01(\t\x12\x11\n\ttenant_id\x18\x04 \x01(\t\x12\x0f\n\x07user_id\x18\x05 \x01(\t\x12\x10\n\x08robot_id\x18\x06 \x01(\t\x12\x12\n\nrobot_type\x18\x07 \x01(\t\x12\x14\n\x0cservice_code\x18\x08 \x01(\t\x12\x0b\n\x03seq\x18\t \x01(\t\x12\x11\n\troot_guid\x18\n \x01(\t\"F\n\rCommonRspInfo\x12\x10\n\x08\x65rr_code\x18\x01 \x01(\x05\x12\x0f\n\x07\x65rr_msg\x18\x02 \x01(\t\x12\x12\n\nerr_detail\x18\x03 \x01(\t\"/\n\x05\x45xtra\x12\x12\n\nextra_type\x18\x01 \x01(\t\x12\x12\n\nextra_body\x18\x02 \x01(\t*N\n\x0cWakeupStatus\x12\r\n\tNO_WAKEUP\x10\x00\x12\x12\n\x0eWAKEUP_SUCCESS\x10\x01\x12\x0e\n\nHAD_WAKEUP\x10\x02\x12\x0b\n\x07ONESHOT\x10\x03*U\n\x08\x41srsLang\x12\r\n\tLANG_KEEP\x10\x00\x12\x0b\n\x07LANG_CH\x10\x01\x12\x0b\n\x07LANG_EN\x10\x02\x12\x10\n\x0cLANG_SICHUAN\x10\x03\x12\x0e\n\nLANG_YUEYU\x10\x04\x32\xbe\x02\n\x06Speech\x12L\n\tRecognize\x12\x1d.skill.asr.RecognitionRequest\x1a\x1e.skill.asr.RecognitionResponse\"\x00\x12Y\n\x12StreamingRecognize\x12\x1d.skill.asr.RecognitionRequest\x1a\x1e.skill.asr.RecognitionResponse\"\x00(\x01\x30\x01\x12\x35\n\x07\x44oCheck\x12\x13.skill.asr.CheckCmd\x1a\x13.skill.asr.CheckCmd\"\x00\x12T\n\rTextRecognize\x12\x1f.skill.asr.TextRecognizeRequest\x1a .skill.asr.TextRecognizeResponse\"\x00\x42\x08Z\x06v1/asrb\x06proto3')

_WAKEUPSTATUS = DESCRIPTOR.enum_types_by_name['WakeupStatus']
WakeupStatus = enum_type_wrapper.EnumTypeWrapper(_WAKEUPSTATUS)
_ASRSLANG = DESCRIPTOR.enum_types_by_name['AsrsLang']
AsrsLang = enum_type_wrapper.EnumTypeWrapper(_ASRSLANG)
NO_WAKEUP = 0
WAKEUP_SUCCESS = 1
HAD_WAKEUP = 2
ONESHOT = 3
LANG_KEEP = 0
LANG_CH = 1
LANG_EN = 2
LANG_SICHUAN = 3
LANG_YUEYU = 4


_BODY = DESCRIPTOR.message_types_by_name['Body']
_BODY_OPTIONENTRY = _BODY.nested_types_by_name['OptionEntry']
_BODY_DATA = _BODY.nested_types_by_name['Data']
_RECOGNITIONREQUEST = DESCRIPTOR.message_types_by_name['RecognitionRequest']
_RECOGNITIONRESPONSE = DESCRIPTOR.message_types_by_name['RecognitionResponse']
_CHECKCMD = DESCRIPTOR.message_types_by_name['CheckCmd']
_TEXTRECOGNIZEREQUEST = DESCRIPTOR.message_types_by_name['TextRecognizeRequest']
_TEXTRECOGNIZEBODY = DESCRIPTOR.message_types_by_name['TextRecognizeBody']
_TEXTRECOGNIZERESPONSE = DESCRIPTOR.message_types_by_name['TextRecognizeResponse']
_COMMONREQINFO = DESCRIPTOR.message_types_by_name['CommonReqInfo']
_COMMONRSPINFO = DESCRIPTOR.message_types_by_name['CommonRspInfo']
_EXTRA = DESCRIPTOR.message_types_by_name['Extra']
_BODY_TYPE = _BODY.enum_types_by_name['Type']
Body = _reflection.GeneratedProtocolMessageType('Body', (_message.Message,), {

  'OptionEntry' : _reflection.GeneratedProtocolMessageType('OptionEntry', (_message.Message,), {
    'DESCRIPTOR' : _BODY_OPTIONENTRY,
    '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
    # @@protoc_insertion_point(class_scope:skill.asr.Body.OptionEntry)
    })
  ,

  'Data' : _reflection.GeneratedProtocolMessageType('Data', (_message.Message,), {
    'DESCRIPTOR' : _BODY_DATA,
    '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
    # @@protoc_insertion_point(class_scope:skill.asr.Body.Data)
    })
  ,
  'DESCRIPTOR' : _BODY,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.Body)
  })
_sym_db.RegisterMessage(Body)
_sym_db.RegisterMessage(Body.OptionEntry)
_sym_db.RegisterMessage(Body.Data)

RecognitionRequest = _reflection.GeneratedProtocolMessageType('RecognitionRequest', (_message.Message,), {
  'DESCRIPTOR' : _RECOGNITIONREQUEST,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.RecognitionRequest)
  })
_sym_db.RegisterMessage(RecognitionRequest)

RecognitionResponse = _reflection.GeneratedProtocolMessageType('RecognitionResponse', (_message.Message,), {
  'DESCRIPTOR' : _RECOGNITIONRESPONSE,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.RecognitionResponse)
  })
_sym_db.RegisterMessage(RecognitionResponse)

CheckCmd = _reflection.GeneratedProtocolMessageType('CheckCmd', (_message.Message,), {
  'DESCRIPTOR' : _CHECKCMD,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.CheckCmd)
  })
_sym_db.RegisterMessage(CheckCmd)

TextRecognizeRequest = _reflection.GeneratedProtocolMessageType('TextRecognizeRequest', (_message.Message,), {
  'DESCRIPTOR' : _TEXTRECOGNIZEREQUEST,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.TextRecognizeRequest)
  })
_sym_db.RegisterMessage(TextRecognizeRequest)

TextRecognizeBody = _reflection.GeneratedProtocolMessageType('TextRecognizeBody', (_message.Message,), {
  'DESCRIPTOR' : _TEXTRECOGNIZEBODY,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.TextRecognizeBody)
  })
_sym_db.RegisterMessage(TextRecognizeBody)

TextRecognizeResponse = _reflection.GeneratedProtocolMessageType('TextRecognizeResponse', (_message.Message,), {
  'DESCRIPTOR' : _TEXTRECOGNIZERESPONSE,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.TextRecognizeResponse)
  })
_sym_db.RegisterMessage(TextRecognizeResponse)

CommonReqInfo = _reflection.GeneratedProtocolMessageType('CommonReqInfo', (_message.Message,), {
  'DESCRIPTOR' : _COMMONREQINFO,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.CommonReqInfo)
  })
_sym_db.RegisterMessage(CommonReqInfo)

CommonRspInfo = _reflection.GeneratedProtocolMessageType('CommonRspInfo', (_message.Message,), {
  'DESCRIPTOR' : _COMMONRSPINFO,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.CommonRspInfo)
  })
_sym_db.RegisterMessage(CommonRspInfo)

Extra = _reflection.GeneratedProtocolMessageType('Extra', (_message.Message,), {
  'DESCRIPTOR' : _EXTRA,
  '__module__' : 'api.proto.asrctrl.asrctrl_pb2'
  # @@protoc_insertion_point(class_scope:skill.asr.Extra)
  })
_sym_db.RegisterMessage(Extra)

_SPEECH = DESCRIPTOR.services_by_name['Speech']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\006v1/asr'
  _BODY_OPTIONENTRY._options = None
  _BODY_OPTIONENTRY._serialized_options = b'8\001'
  _WAKEUPSTATUS._serialized_start=1656
  _WAKEUPSTATUS._serialized_end=1734
  _ASRSLANG._serialized_start=1736
  _ASRSLANG._serialized_end=1821
  _BODY._serialized_start=77
  _BODY._serialized_end=583
  _BODY_OPTIONENTRY._serialized_start=288
  _BODY_OPTIONENTRY._serialized_end=333
  _BODY_DATA._serialized_start=336
  _BODY_DATA._serialized_end=549
  _BODY_TYPE._serialized_start=551
  _BODY_TYPE._serialized_end=583
  _RECOGNITIONREQUEST._serialized_start=586
  _RECOGNITIONREQUEST._serialized_end=738
  _RECOGNITIONRESPONSE._serialized_start=741
  _RECOGNITIONRESPONSE._serialized_end=968
  _CHECKCMD._serialized_start=970
  _CHECKCMD._serialized_end=1028
  _TEXTRECOGNIZEREQUEST._serialized_start=1031
  _TEXTRECOGNIZEREQUEST._serialized_end=1198
  _TEXTRECOGNIZEBODY._serialized_start=1200
  _TEXTRECOGNIZEBODY._serialized_end=1285
  _TEXTRECOGNIZERESPONSE._serialized_start=1287
  _TEXTRECOGNIZERESPONSE._serialized_end=1337
  _COMMONREQINFO._serialized_start=1340
  _COMMONREQINFO._serialized_end=1533
  _COMMONRSPINFO._serialized_start=1535
  _COMMONRSPINFO._serialized_end=1605
  _EXTRA._serialized_start=1607
  _EXTRA._serialized_end=1654
  _SPEECH._serialized_start=1824
  _SPEECH._serialized_end=2142
# @@protoc_insertion_point(module_scope)

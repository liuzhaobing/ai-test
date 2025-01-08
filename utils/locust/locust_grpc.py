# -*- coding:utf-8 -*-
# Filename: locust_grpc.py
# Description: 
# Author: zhaobing.liu@outlook.com
# Created: 2024/7/11
# Last Modified: 2024/7/11
import grpc
import grpc.experimental.gevent as grpc_gevent
from locust.exception import LocustError

from utils.data import check_grpc_url
from utils.locust.locust_base import ParseUser

grpc_gevent.init_gevent()


class GRPCUser(ParseUser):
    abstract = True
    interceptor = None  # from api.client.interceptor_client import (StreamStreamGrpcInterceptor, UnaryStreamGrpcInterceptor, StreamUnaryGrpcInterceptor, UnaryUnaryGrpcInterceptor)
    stub_class = None  # from api.proto.grpc_stream_pb2_grpc import GRPCStreamStub
    insecure: bool = True

    @staticmethod
    def yield_message(message):
        yield message

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.stub_class:
            raise LocustError("You must specify a gRPC stub class.")

        if not self.interceptor:
            raise LocustError("You must specify a gRPC interceptor.")

        if not check_grpc_url(self.host):
            raise LocustError("You must specify a valid gRPC host. E.g. 127.0.0.1:50051")

        if self.insecure:
            channel = grpc.insecure_channel(self.host)
        else:
            channel = grpc.secure_channel(self.host, grpc.ssl_channel_credentials())
        self._channel = grpc.intercept_channel(channel, self.interceptor())
        self.stub = self.stub_class(self._channel)

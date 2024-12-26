# -*- coding:utf-8 -*-
import grpc


class StreamStreamGrpcInterceptor(grpc.StreamStreamClientInterceptor):
    """双向数据流"""

    def intercept_stream_stream(
            self,
            continuation,
            client_call_details,
            request_iterator,
            **kwargs
    ):
        response_iterator = continuation(client_call_details, request_iterator, **kwargs)
        for response in response_iterator:
            yield response


class UnaryStreamGrpcInterceptor(grpc.UnaryStreamClientInterceptor):
    """单向返回数据流"""

    def intercept_unary_stream(
            self,
            continuation,
            client_call_details,
            request,
            **kwargs
    ):
        response_iterator = continuation(client_call_details, request, **kwargs)
        for response in response_iterator:
            yield response


class StreamUnaryGrpcInterceptor(grpc.StreamUnaryClientInterceptor):
    """单向请求数据流"""

    def intercept_stream_unary(
            self,
            continuation,
            client_call_details,
            request_iterator,
            **kwargs
    ):
        response = continuation(client_call_details, request_iterator, **kwargs)
        return response


class UnaryUnaryGrpcInterceptor(grpc.UnaryUnaryClientInterceptor):
    """双向文本数据"""

    def intercept_unary_unary(
            self,
            continuation,
            client_call_details,
            request,
            **kwargs
    ):
        response = continuation(client_call_details, request, **kwargs)
        return response

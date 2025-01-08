### Generate pb

```shell
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./api/proto/tts/fragment_tts.proto
```
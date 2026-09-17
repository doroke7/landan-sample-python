# src/config.py
import bootstrap.config as config

n_grpc_http_port = config.config('grpc.port')

print(n_grpc_http_port)


import multiprocessing

ip = "0.0.0.0"
ports = [8001, 8002]
bind = [ip + ":" + str(port) for port in ports]
workers = multiprocessing.cpu_count()*len(ports)
worker_connections = 1000
timeout = 30
keepalive = 2

from cpppo.server.enip import client
from cpppo.server.enip.getattr import attribute_operations

HOST = "192.168.1.100"
TAGS = ["@4/100/3"]

with client.connector(host=HOST) as conn:
    for index, descr, op, reply, status, value in conn.synchronous(
        operations=attribute_operations(
            TAGS, route_path=[], send_path='' )):
        print(": %20s: %s" % (descr, value))
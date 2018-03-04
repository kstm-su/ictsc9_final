from damage_tcp import DamageServer # :8610
from gameover_tcp import GameOverServer # :9090
from ranking_tcp import RankingServer # :8998
from start_tcp import StartingServer # :8609
from sync_udp import GameServer # :8992/udp


import threading
import socketserver

socketserver.ThreadingTCPServer.allow_reuse_address = True

ts = list()

for port, server in [[8610, DamageServer], [9090, GameOverServer], [8998, RankingServer], [8609, StartingServer]]:
    ss = socketserver.ThreadingTCPServer(('0.0.0.0', port), server)
    t = threading.Thread(target=ss.serve_forever)
    ts.append(t)
    t.start()


ss = socketserver.ThreadingUDPServer(('0.0.0.0', 8992), GameServer)
t = threading.Thread(target=ss.serve_forever)
ts.append(t)
t.start()

try:
    for t in ts:
        t.join()
except KeyboardInterrupt:
    print('Got Ctrl-C')
    for t in ts:
        t._stop()

from external.data_manager import main as dm_main
from external.score_calculator import main as sc_main
from server.damage_tcp import DamageServer # :8610
from server.gameover_tcp import GameOverServer # :9090
from server.ranking_tcp import RankingServer # :8998
from server.start_tcp import StartingServer # :8609
from server.sync_udp import GameServer # :8992/udp

import threading
import socketserver


ts = list()

# data_manager
t = threading.Thread(target=dm_main)
ts.append(t)
t.start()

# score_calculator
t = threading.Thread(target=sc_main)
ts.append(t)
t.start()


socketserver.ThreadingTCPServer.allow_reuse_address = True

# tcp server
for port, server in [[8610, DamageServer], [9090, GameOverServer], [8998, RankingServer], [8609, StartingServer]]:
    ss = socketserver.ThreadingTCPServer(('0.0.0.0', port), server)
    t = threading.Thread(target=ss.serve_forever)
    ts.append(t)
    t.start()

# udp server
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

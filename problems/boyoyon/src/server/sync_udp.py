import socketserver
import redis


class GameServer(socketserver.BaseRequestHandler):
    """
    ゲーム中にリアルタイムで更新するパラメータの送受信サーバ
    """
    def handle(self):
        self.data = self.request[0]
        sock = self.request[1]

        player_id, player_data = self.data.split(b':')
        name, type, attack_status, x, y, z, yr = player_data.split(b',')

        db0 = redis.Redis(host='localhost', port=6379, db=0)

        # dbのアクセス順序が保証されないためエラー処理を追加
        try:
            # 自分のパラメータ更新
            # すでにゲームオーバーしていたら処理を飛ばす
            if player_id in db0.keys():
                db0.lset(player_id, 2, attack_status)
                db0.lset(player_id, 4, x)
                db0.lset(player_id, 5, y)
                db0.lset(player_id, 6, z)
                db0.lset(player_id, 7, yr)

            res = b''
            for object_id in db0.keys():
                res += b','.join(db0.lrange(object_id, 0, -1))
                res += b':'

            # ラグ発生時のバグ消し用
            while res[-1] == 58:
                res = res[:-1]

            sock.sendto(res, self.client_address)

        except:
            res = b''
            for object_id in db0.keys():
                res += b','.join(db0.lrange(object_id, 0, -1))
                res += b':'

            # ラグ発生時のバグ消し用
            while res[-1] == 58:
                res = res[:-1]

            sock.sendto(res, self.client_address)



class ThreadedGameServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8992

    server = ThreadedGameServer((HOST, PORT), GameServer)
    server.serve_forever()

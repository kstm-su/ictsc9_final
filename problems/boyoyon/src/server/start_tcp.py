import socketserver
import random
import redis

from server.utils import is_sha1, is_name_safe, is_name_unique


class StartingServer(socketserver.BaseRequestHandler):
    """
    ゲームスタートする際にアクセスするサーバ
    利用したい名前と機体情報を受け取り登録
    """
    def handle(self):
        self.data = self.request.recv(4096).strip().decode("utf-8")

        # :が入っている場合
        if self.data.count(':') >= 3:
            self.request.sendall(b"No")
            return

        player_id, name, type = self.data.split(':')

        r = redis.Redis(host="localhost", port=6379, db=0)

        # 入力値のチェック
        if not is_sha1(player_id):
            self.request.sendall(b"No")
        elif not is_name_safe(name):
            self.request.sendall(b"No")
        elif not is_name_unique(r, name):
            self.request.sendall(b"No")
        elif int(type) > 50:
            self.request.sendall(b"No")


        else:
            position = [(-6, -6), (9, 1), (0, 0)]
            position_tmp = position[random.randint(0,2)]
            if player_id not in map(lambda x: x.decode("utf-8"), r.keys()):
                # store the data
                r.rpush(player_id, name)
                r.rpush(player_id, type)
                r.rpush(player_id, 0)
                r.rpush(player_id, 3)
                r.rpush(player_id, position_tmp[0])
                r.rpush(player_id, 0.5)
                r.rpush(player_id, position_tmp[1])
                r.rpush(player_id, 0)

                # ランキングテーブルに追加
                ranking_db = redis.Redis(host="localhost", port=6379, db=1)
                ranking_db.set(player_id, 0)

            else:
                r.lset(player_id, 0, name)
                r.lset(player_id, 1, type)
                r.lset(player_id, 2, 0)
                r.lset(player_id, 3, 3)
                r.lset(player_id, 4, position_tmp[0])
                r.lset(player_id, 5, 0.5)
                r.lset(player_id, 6, position_tmp[1])
                r.lset(player_id, 7, 0)

            self.request.sendall(b':'.join(r.lrange(player_id, 0, -1)))


class ThreadedStartingServer(socketserver.ThreadingMixIn,
                             socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8609

    server = ThreadedStartingServer((HOST, PORT), StartingServer)
    server.serve_forever()

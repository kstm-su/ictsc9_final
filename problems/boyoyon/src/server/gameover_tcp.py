import socketserver
import redis


class GameOverServer(socketserver.BaseRequestHandler):
    """
    ゲームオーバーしたら通信を受け取るサーバー
    """
    def handle(self):
        self.data = self.request.recv(4096).strip().decode("utf-8")
        player_id = self.data

        db0 = redis.Redis(host="localhost", port=6379, db=0)
        db1 = redis.Redis(host="localhost", port=6379, db=1)

        # ゲームオーバーになったユーザをサーバとランキングから削除
        db1.delete(player_id)
        db0.delete(player_id)
        res = "Success"

        self.request.sendall(res.encode("utf-8"))


class ThreadedGameOverServer(socketserver.ThreadingMixIn,
                             socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9090

    server = ThreadedGameOverServer((HOST, PORT), GameOverServer)
    server.serve_forever()

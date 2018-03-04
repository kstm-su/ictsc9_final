import socketserver
import redis


class RankingServer(socketserver.BaseRequestHandler):
    """
    自分のランキングとスコア＋トップ５のスコアを返す
    レスポンス形式：player_rank, score: name, score:name, score...
    """
    def handle(self):
        self.data = self.request.recv(4096).strip().decode("utf-8")
        player_id = self.data
        
        db0 = redis.Redis(host="localhost", port=6379, db=0)
        db1 = redis.Redis(host="localhost", port=6379, db=1)
        
        res = ''
        
        # 全スコア格納
        
        if db1.keys() == []:
            res = "0,0:{},0".format(db0.lindex(player_id, 0).decode("utf-8"))
            self.request.sendall(res.encode("utf-8"))

        else:
            scores = {}
            try:
                for key in db1.keys():
                    name = db0.lindex(key, 0).decode("utf-8")
                    scores.update({name: int(db1.get(key).decode("utf-8"))})

                # スコアで逆順にソート
                res_scores = sorted(scores.items(),
                                    key=lambda x: x[1],
                                    reverse=True)
                player_info = ''
                ranking = ''

                for i, data in enumerate(res_scores):
                    # トップ5のみ返す
                    if i <= 4:
                        ranking += ':' + data[0] + ',' + str(data[1])

                    # 自分のランキング情報
                    if data[0] == db0.lindex(player_id, 0).decode("utf-8"):
                        player_info = str(i + 1) + ',' + str(data[1])

                res = player_info + ranking
                self.request.sendall(res.encode("utf-8"))                

            except:
                res = "Error"
                self.request.sendall(res.encode("utf-8"))


class ThreadedRankingServer(socketserver.ThreadingMixIn,
                            socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8998

    server = ThreadedRankingServer((HOST, PORT), RankingServer)
    server.serve_forever()

import socketserver
import redis


class DamageServer(socketserver.BaseRequestHandler):
    """
    ダメージ処理をするサーバ
    """
    def handle(self):
        self.data = self.request.recv(4096).strip().decode("utf-8")
        
        # player ID ----atack----> enemy_name
        player_id, enemy_name = self.data.split(',')
        
        db0 = redis.Redis(host="localhost", port=6379, db=0)
        db1 = redis.Redis(host="localhost", port=6379, db=1)
        
        # 敵の名前からIDを検索
        enemy_id = ''
        for key in db0.keys():
            if enemy_name == db0.lindex(key, 0).decode("utf-8"):
                enemy_id = key

        res = "No"
        if enemy_id != '':
            # レスポンス用type
            res = db0.lindex(enemy_id, 1)

            # 自分へのダメージ(ステージ外への落下)処理は即死
            if player_id == enemy_id.decode("utf-8"):
                db1.delete(player_id)
                db0.delete(player_id)                


            # アイテムの場合、自分のhpを回復
            elif int(res.decode("utf-8")) > 100:
                db0.delete(enemy_id)
                my_hp = int(db0.lindex(player_id, 3).decode("utf-8"))
                # HP上限は5
                if my_hp < 5:
                    db0.lset(player_id, 3, my_hp + 1)

            else:
                # 相手のhpを減らす処理
                hp = int(db0.lindex(enemy_id, 3).decode("utf-8")) - 1
                if hp <= 0:
                    db1.delete(enemy_id)
                    db0.delete(enemy_id)
                else:
                    db0.lset(enemy_id, 3, hp)

                # ランキングのスコアを加算
                if player_id is not '' and enemy_name is not '':
                    db1.incr(player_id, 10)

        self.request.sendall(res)


class ThreadedDamageServer(socketserver.ThreadingMixIn,
                           socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8610

    server = ThreadedDamageServer((HOST, PORT), DamageServer)
    server.serve_forever()

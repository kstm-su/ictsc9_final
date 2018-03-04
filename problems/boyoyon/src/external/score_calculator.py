import redis
import time
import random


def add_height_score(db0, db1):
    for player_id in db1.keys():
        height = int(float(db0.lindex(player_id, 5).decode("utf-8")) / 2)
        db1.incr(player_id, height)


def main():
    db0 = redis.Redis(host="localhost", port=6379, db=0)
    db1 = redis.Redis(host="localhost", port=6379, db=1)

    while True:
        try:
            for player_id in db1.keys():
                height = int(float(db0.lindex(player_id, 5).decode("utf-8")))
                db1.incr(player_id, height)

            time.sleep(10)

        # 処理中にプレイヤーが死んだ場合
        except:
            time.sleep(10)


if __name__ == "__main__":
    main()

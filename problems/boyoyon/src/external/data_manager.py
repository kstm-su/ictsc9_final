import redis
import sys
import time
import random
import hashlib


def backup_redis(db):
    """
    kvsバックアップ用関数
    """
    result = db.bgsave()
    time.sleep(10)


def update_player_list(db0):
    """
    player_listのプレイヤー一覧を更新
    {key : x, y, z, xr, yr, zr}
    """
    player_list = {}

    for key in db0.keys():
        type = int(db0.lindex(key, 1).decode("utf-8"))
        if 1 <= type <= 50:
            player_list.update({key: db0.lrange(key, 3, -1)})

    return player_list


def update_item_flags(db0):
    """
    アイテムフラグを初期化し返す
    True -> 欠けてるアイテム
    """
    item_flags = {"item1": False,
                  "item2": False,
                  "item3": False}

    # アイテムフラグを更新
    for object_id in db0.keys():
        ob_name = db0.lindex(object_id, 0).decode("utf-8")
        if "item" in ob_name:
            item_flags[ob_name] = True

    return item_flags


def generate_missing_items(db0, item_flags):
    """
    フラグが立っているアイテムを生成する
    """
    for key in item_flags.keys():
        if not item_flags[key]:
            # ランダムにすることでアイテムのハッシュ漏れによるチートを対策
            random_tmp = str(random.random()).encode("utf-8")
            new_item_id = hashlib.sha1(random_tmp).hexdigest()
            name = key
            type = random.randint(101, 103)

            db0.rpush(new_item_id, name)                   # name
            db0.rpush(new_item_id, type)                   # type
            db0.rpush(new_item_id, 0)                      # attack_status
            db0.rpush(new_item_id, 1)                      # hp
            db0.rpush(new_item_id, random.randint(-5, 0))  # x
            db0.rpush(new_item_id, 0.5)                    # y
            db0.rpush(new_item_id, random.randint(-5, 0))  # z
            db0.rpush(new_item_id, 0)                      # yr


def main():
    """
    バックアップを取り、アイテム補充と放置者追放を行う
    実行感覚は25秒に1回
    """
    db0 = redis.Redis(host='localhost', port=6379, db=0)
    db1 = redis.Redis(host='localhost', port=6379, db=1)

    # player_list作成
    player_list = update_player_list(db0)

    while True:
        # kvsのバックアップ
        backup_redis(db0)
        backup_redis(db1)

        # フラグを更新し，アイテムが欠けていれば作成
        item_flags = update_item_flags(db0)
        generate_missing_items(db0, item_flags)

        # 25秒前のリストと変化がなければ放置と認定
        for key in player_list.keys():
            if player_list[key] == db0.lrange(key, 3, -1):
                db1.delete(key)
                db0.delete(key)

        # プレイヤーリストを更新
        player_list = update_player_list(db0)

        time.sleep(5)


if __name__ == "__main__":
    main()

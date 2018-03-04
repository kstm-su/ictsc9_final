import redis


# sha1の形チェック
def is_sha1(id):
    if len(id) != 40:
        return False
    try:
        sha_int = int(id, 16)
    except ValueError:
        return False
    return True


# 名前の使用文字チェック
def is_name_safe(name):
    if ',' in name or ':' in name or '/' in name:
        return False
    return True


# 名前がユニークかをチェック
def is_name_unique(r, name):
    for key in r.keys():
        if name.encode("utf-8") == r.lindex(key, 0):
            return False
    return True

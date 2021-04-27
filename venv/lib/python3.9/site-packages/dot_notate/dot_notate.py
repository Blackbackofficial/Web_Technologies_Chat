def dot_notate(obj, res, currentKey):
    for k, v in obj.items():
        newKey = currentKey + "." + k if currentKey else k
        if v and isinstance(v, dict):
            dot_notate(v, res, newKey)
        else:
            res[newKey] = v
    return res

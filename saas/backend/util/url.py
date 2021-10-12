def url_join(host: str, path: str) -> str:
    """
    拼接host, path生成url

    处理host, path有多余/的情况
    """
    return "{}/{}".format(host.rstrip("/"), path.lstrip("/"))

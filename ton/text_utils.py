import hashlib


def hash_text(text: str) -> str:
    data = text.encode('utf-8')
    md5 = hashlib.md5(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    sha512 = hashlib.sha512(data).hexdigest()
    hashstring = (md5 + sha256 + sha512).encode('utf-8')
    result = hashlib.sha256(hashstring).hexdigest()
    return result

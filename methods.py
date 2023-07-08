from hashlib import sha256
def valid_char(char):
    if char.isalpha(): return True
    if char.isdigit(): return True
    if char in {'-', '_', '.'}: return True
    return False

def sha_hash(s):
    return sha256(s.encode('utf-8')).hexdigest()



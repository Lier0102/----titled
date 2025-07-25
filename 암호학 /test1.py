# from pwn import *
# from Crypto.Cipher import DES
# from tqdm import trange

# io = process(["python3", "prob.py"])

# io.recvuntil(b":> ")
# hint = bytes.fromhex(io.recvline().decode())

# for i in trange(2**32):
#     key = b'Dream_' + i.to_bytes(4, "big") + b'Hacker'
#     key1 = key[:8]
#     key2 = key[8:]
#     cipher1 = DES.new(key1, DES.MODE_ECB)
#     cipher2 = DES.new(key2, DES.MODE_ECB)
#     if cipher2.encrypt(cipher1.encrypt(b'DreamHack_blocks')) == hint:
#         print("Success")
#         break

from pwn import *
from Crypto.Cipher import DES

io = process(["python3", "prob.py"])
# io = remote("host3.dreamhack.games", 18664)

io.recvuntil(b":> ")
hint = bytes.fromhex(io.recvline().decode())

conflict = dict()

for i in range(65536):
    b = i.to_bytes(2, "big")
    cipher = DES.new(b"Dream_" + b, DES.MODE_ECB)
    enc = cipher.encrypt(b"DreamHack_blocks")
    conflict[enc] = b"Dream_" + b

for i in range(65536):
    b = i.to_bytes(2, "big")
    cipher = DES.new(b + b"Hacker", DES.MODE_ECB)
    dec = cipher.decrypt(hint)

    if dec in conflict:
        key1 = conflict[dec]
        key2 = b + b"Hacker"
        break

cipher1 = DES.new(key1, DES.MODE_ECB)
cipher2 = DES.new(key2, DES.MODE_ECB)
encrypt = lambda x: cipher2.encrypt(cipher1.encrypt(x))
assert encrypt(b"DreamHack_blocks") == hint

io.sendlineafter(b'> ', encrypt(b"give_me_the_flag").hex().encode())

flag = eval(io.recvline())
io.close()

print(flag.decode())
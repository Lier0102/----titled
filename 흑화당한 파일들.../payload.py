from pwn import *

p = process("./house_of_force")
e = ELF("./house_of_force")

p.sendlineafter("> ") # 크기 



p.sendlineafter("> ") # 값 
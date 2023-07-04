from security.main import hash_pass,add_user
import sys

args = sys.argv
username = args[1]
passwd = args[2]

hashpass = hash_pass(passwd)
add_user(username,hashpass)

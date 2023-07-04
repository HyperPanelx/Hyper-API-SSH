from security.main import hash_pass,add_user

username = input('Set username Panel: ')
passwd = input('Set Password Panel: ')
hashpass = hash_pass(passwd)
add_user(username,hashpass)
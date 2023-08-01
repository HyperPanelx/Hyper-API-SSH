from ops.main import sshtnl
from collections import Counter

obj=sshtnl()
print(obj.get_user_tun_all('sara'))
# a=['sara', 'mahya', 'user04', 'shiva01', 'sara', 'test', 'test', 'mehdi01', 'shuku', 'sara', 'mehdi01']
# counts = Counter(a)
# print(counts)
# import subprocess
# import re

# for count in range(1,6):
#     print(count)
# command=f"lsof -i -n | egrep '\<ssh\>' | grep test"
# try:
#     result=self.multi.ssh_main__(command,ipaddress)
#     est = re.findall(f'ssh->(\b(?:\d{1,3}\.){3}\d{1,3}\b)',result)
#     print(est)
#     lenuser=(len(est))
# except:
#     pass
# if lenuser > 0:
#     list.append({'username':user,'lenuser':lenuser,'ipaddress':ipaddress})
# lenuser = 0
# result=subprocess.getoutput(command)
# # print(result)
# pattern = r'ssh->(\b(?:\d{1,3}\.){3}\d{1,3}\b)'
# est = re.findall(pattern,result)
# print(est)
# list=[]
# for dict in est:
#     list.append(dict)
# list2=[]
# for dict2 in list:
#     if dict2 == dict:
#         list2.append(dict2)
# print(list2)


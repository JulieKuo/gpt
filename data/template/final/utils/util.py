import os
import platform
import uuid


def getSysMacAddr():
    macaddr = uuid.UUID(int=uuid.getnode()).hex[-12:]
    macaddr_list = []
    for i in range(0, 11, 2):
        macaddr_list.append(macaddr[i:i + 2])
    return ':'.join(macaddr_list).upper()


def update_chmod():
    if not platform.system() == 'Windows':
        os.system('chmod +x ../inference/*')
        os.system('chmod +x ./type/*')

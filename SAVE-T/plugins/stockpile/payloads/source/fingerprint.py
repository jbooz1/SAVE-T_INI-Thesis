import argparse
import requests
import nmap

SUCCESS = 0
timeout = 2
URIS = ['', 'strutswebapp', 'struts']
webPorts = ['80', '8080', '443']


def fingerprint_asus(req):
    try:
        return 'RT-N56U' in req.headers['WWW-Authenticate']
    except:
        return False


def fingerprint_trendnet(req):
    try:
        return 'netcam' in req.headers['WWW-Authenticate']
    except:
        return False


def fingerprint_thinkphp(req):
    try:
        return 'thinkphp' in req.text
    except:
        return False


def fingerprint_struts(req):
    success = False
    try:
        if 'Tomcat' in req.text:
            for uri in URIS:
                try:
                    req = requests.get(f'http://{req.url}/{uri}')
                    break
                except requests.HTTPError:
                    continue
            if 'Struts' in req.text:
                success = True
        if 'struts' in req.text:
            success = True
    finally:
        return success


def fingerprint_eternalBlue(target):
    nm = nmap.PortScanner()
    nm.scan(hosts=target, ports='445', arguments='--script smb-vuln-ms17-010')

    if "VULNERABLE" in nm.get_nmap_last_output():
        return True
    else:
        return False


parser = argparse.ArgumentParser('homemade port scanner')
parser.add_argument('-s', '--socket', required=True, default='127.0.0.1:80', help='Send me an IP and Port to fingerprint')
parser.add_argument('-c', '--service', required=True, default=None, help='Pass a service that I know how to fingerprint')
args = parser.parse_args()

split = args.socket.split(':')

found = False

# eternalBlue Fingerprint
if split[1] == '445':
    if args.service == 'eternalBlue':
        found = fingerprint_eternalBlue(split[0])
    elif args.service == 'smb':
        found = True

# true if 22 and looking for ssh
elif split[1] == '22':
    if args.service == 'ssh':
        found = True

# true if 23 and looking for telnet
elif split[1] == '23':
    if args.service == 'telnet':
        found = True

# true if 21 and looking for ftp
elif split[1] == '21':
    if args.service == 'ftp':
        found = True

# web fingerprint
elif split[1] in webPorts:
    try:
        req = requests.get(f'http://{args.socket}', timeout=timeout)
    except requests.exceptions.ReadTimeout:
        exit(0)
    except requests.exceptions.ConnectionError:
        exit(0)
    except requests.HTTPError:
        req = requests.get(f'http://{args.socket}/public')

    if args.service == 'Asus':
        found = fingerprint_asus(req)

    elif args.service == 'ThinkPHP':
        found = fingerprint_thinkphp(req)

    elif args.service == 'ApacheStruts':
        found = fingerprint_struts(req)

    elif args.service == 'Trendnet':
        found = fingerprint_trendnet(req)

    elif args.service == 'IIS':
        found = 'IIS' in req.text


if found:
    print(args.socket)




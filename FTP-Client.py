#65010801 ภวัต ประกายทิพย์
import socket
import time
from getpass import getpass

cmd_sock = None
host = None

NOT_NEED_CONNECTION = (
    "bye",
    "open",
    "quit"
)

NEED_CONNECTION = (
    "ascii",
    "binary",
    "cd",
    "close",
    "delete",
    "disconnect",
    "get",
    "ls",
    "put",
    "pwd",
    "rename",
    "user"
)


def ftp_send_cmd(socket: socket, str: str): #format string and send to ftp server
    socket.sendall(f"{str}\r\n".encode())
    return

def get_resp(socket: socket) -> str:
    #TODO: return status code
    return socket.recv(1024).decode().strip()

def close_cmd_sock():
    global cmd_sock
    try:
        cmd_sock.close()
        cmd_sock = None
    except:
        cmd_sock = None

def ftp_open_data_conn() -> socket:
    global host
    #bind listing socket
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock.bind((host, 0))
    data_sock.listen()
    host_part = host.replace('.', ',')

    port = data_sock.getsockname()[1] #get port number
    port = f"{port:016b}" #convert port number to bianry
    port_1 = int(port[0:8], 2) #first part of the port
    port_2 = int(port[8:16], 2) #second part of the port
    
    ftp_send_cmd(cmd_sock, f"PORT {host_part},{port_1},{port_2}")
    print(get_resp(cmd_sock))
    #TODO: add exception if fail
    return data_sock

def measure(text: str):
    def inner(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()

            result = func(*args, **kwargs)

            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time == 0: #prevent very fast transfer(start_time = end_time) from causeing devide by 0
                elapsed_time = 0.0001
            
            speed = result[0] / (elapsed_time * 1000) #result[0] = size of data
            status = f"ftp: {result[0]} bytes {text} in {elapsed_time:.3f}Seconds {speed:.2f}Kbytes/sec."
            return status, result
        return wrapper
    return inner

@measure("received")
def recv_data(data_sock: socket):
    data_conn, data_addr = data_sock.accept()
    size = 0
    data = ""
    while True:
        data_part = data_conn.recv(1024)
        if data_part:
            data += data_part.decode()
        else:
            break
    size = len(data)
    return size + 3, data #Plus 3 because of IDK

@measure("sent")
def send_data(data_sock, file):
    data_conn, data_addr = data_sock.accept()
    size = 0

    while True:
        bytes_read = file.read(1024)
        if not bytes_read:
            break
        size += len(bytes_read)
        data_conn.sendall(bytes_read)
    
    return (size + 3,) #Plus 3 because of IDK



def ascii():
    ftp_send_cmd(cmd_sock, "TYPE A")
    print(get_resp(cmd_sock))
    return

def binary():
    ftp_send_cmd(cmd_sock, "TYPE I")
    print(get_resp(cmd_sock))
    return

def bye():
    try:
        ftp_send_cmd(cmd_sock, "QUIT")
        print(get_resp(cmd_sock))
        close_cmd_sock()
    except:
        pass
    exit()

def cd(remote_dir: str, *argv):
    ftp_send_cmd(cmd_sock, f"CWD {remote_dir}")
    print(get_resp(cmd_sock))
    return

def close():
    try:
        ftp_send_cmd(cmd_sock, "QUIT")
    except:
        print("Not connected.")
        return

    print(get_resp(cmd_sock))
    close_cmd_sock()

def delete(remote_file: str = "", *argv):
    if not remote_file:
        remote_file = input("Remote file ")
        if not remote_file:
            print("delete remote file.")
            return
    
    ftp_send_cmd(cmd_sock, f"DELE {remote_file}")
    print(get_resp(cmd_sock))

def get(remote_file: str = "", local_file: str = "", *argv):
    if not remote_file:
        remote_file = input("Remote file ")
        if not remote_file:
            print("Remote file get [ local-file ].")
            return
        
        local_file = input("Local file ")

    if not local_file:
        local_file = remote_file

    data_sock = ftp_open_data_conn()
    ftp_send_cmd(cmd_sock, f"RETR {remote_file}")
    resp = get_resp(cmd_sock) #Note: double \r\n in "550 This function is not supported on this system.\r\n\r\n"
    print(resp)

    if resp.startswith("550"):
        return

    status, result = recv_data(data_sock)
    file = open(local_file, 'w')
    file.write(result[1])
    file.close()
    print(get_resp(cmd_sock))
    if result[0] == 3: #if file is empty
        return
    print(status)


def ls(remote_dir: str = "", *argv) -> None:
    data_sock = ftp_open_data_conn()

    ftp_send_cmd(cmd_sock, f"NLST {remote_dir}")
    resp = get_resp(cmd_sock)
    resp_code = resp.split()[0]
    print(resp, end='')

    if resp_code == "550": #Couldn't open the file or directory
        return
    elif resp_code != "150":
        print("Unexpected error, ls command")
        return

    status, result = recv_data(data_sock)
    print(result[1], end="")
    print(get_resp(cmd_sock)) #226 Operation successful
    #TODO: add exception
    print(status)
    return

def ftp_open(host_local: str = None, port: str = "21", *argv):
    global cmd_sock
    global host

    if argv:
        print("Usage: open host name [port]")
        return

    if cmd_sock: #check if already connect
        print(f"Already connected to {host}, use disconnect first.")
        return

    cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not host_local:
        host_local = input("To ")
        if not host_local:
            print("Usage: open host name [port]")
            return
    
    #set recieved host from funciton to global var for future use
    host = host_local 

    #attempt establish connection
    try:
        cmd_sock.connect((host_local, int(port)))
    except ConnectionRefusedError:
        print("> ftp: connect :Connection refused")
        close_cmd_sock()
        return
    except socket.timeout:
        print("> ftp: connect :Connection timed out")
        close_cmd_sock()
        return
    except socket.gaierror:
        print(f"Unknown host {host_local}.")
        close_cmd_sock()
        return
    except Exception as e:
        print(type(e).__name__, e.args)
        return

    print(get_resp(cmd_sock))

    #login
    user = input(f"User ({host_local}:(none)): ")
    ftp_send_cmd(cmd_sock, f"USER {user}")

    resp = get_resp(cmd_sock)#respond for username input
    resp_code = resp.split()[0]
    print(resp)

    if resp_code == "501": #missing user argument
        print("Login failed.")
    
    elif resp_code == "331": #get password
        password = getpass("Password: ")
        print()
        ftp_send_cmd(cmd_sock, f"PASS {password}")
        resp = get_resp(cmd_sock)
        resp_code = resp.split()[0]

        if resp_code == "530": #530 Login incorrect.
            print(resp)
            print("Login failed")
        elif resp_code == "230": #Login successful
            print(resp)
        else:
            print("unexpected error, password")
    
    else:
        print("unexpected error, user")

def put(local_file: str = "", remote_file: str = "", *argv):
    if not local_file:
        local_file = input("Local file ")
        if not local_file:
            print("Local file put: remote file.")
            return
        
        remote_file = input("Remote file ")

    if not remote_file:
        remote_file = local_file
    
    try:
        file = open(local_file, "rb")
    except FileNotFoundError:
        print(f"{local_file}: File not found")
        return
    except PermissionError:
        print(f"Error opening local file {local_file}.")
        return

    data_sock = ftp_open_data_conn()
    ftp_send_cmd(cmd_sock, f"STOR {remote_file}")
    print(get_resp(cmd_sock))
    status, result = send_data(data_sock, file)

    file.close() #TODO: user 'with' statement
    data_sock.close() #TODO: user 'with' statement

    print(get_resp(cmd_sock))
    if result[0] == 3: #if file is empty
        return
    print(status)

def pwd():
    ftp_send_cmd(cmd_sock, f"XPWD")
    print(get_resp(cmd_sock))
    return

def rename(from_name: str = "", to_name: str = "", *argv):
    if not from_name: #no argument specify
        from_name = input("From name ")
    
    if not to_name: #only one argument specify
        to_name = input("To name ")

    ftp_send_cmd(cmd_sock, f"RNFR {from_name}")
    resp = get_resp(cmd_sock)
    if resp.startswith("350"): #directory exists
        print(resp)
        ftp_send_cmd(cmd_sock, f"RNTO {to_name}")
        print(get_resp(cmd_sock))
    else:
        print("Unexpected error, rename command")
    return

def user(user: str = "", password: str ="", *argv):
    if not user:
        user = input("Username: ")
        if not user:
            print("Usage: user username [password] [account]")
            return

    ftp_send_cmd(cmd_sock, f"USER {user}")
    print(get_resp(cmd_sock))

    if not password:
        password = getpass("Password: ")
    
    ftp_send_cmd(cmd_sock, f"PASS {password}")

    resp = get_resp(cmd_sock)
    resp_code = resp.split()[0]

    if resp_code == "530": #530 Login incorrect.
        print(resp)
        print("Login failed")
    elif resp_code == "230": #Login successful
        print(resp)
    else:
        print("unexpected error, password")



while True:
    input_str = input("ftp> ")

    #input sanitization
    input_list = input_str.split()
    if not input_list: #check for empty command
        continue
    
    command = input_list[0]

    arg = input_list[1:]
    
    if command in NOT_NEED_CONNECTION:
        match command:
            case "bye":
                bye()

            case "open":
                ftp_open(*arg)

            case "quit":
                bye()

    elif command in NEED_CONNECTION:
        if not cmd_sock:
            print("Not connected.")
            continue

        match command:
            case "ascii":
                ascii()
            
            case "binary":
                binary()
            
            case "cd":
                cd(*arg)

            case "close":
                close()

            case "delete":
                delete(*arg)

            case "disconnect": # disconnect = close
                close()

            case "get":
                get(*arg)

            case "ls":
                ls(*arg)

            case "put":
                put(*arg)

            case "pwd":
                pwd()

            case "rename":
                rename(*arg)

            case "user":
                user(*arg)

    else:
        print("Invalid command.")



#TODO: Command
        #[x] ascii
        #[x] binary
        #[x] bye
        #[x] cd
        #[x] close
        #[x] delete
        #[x] disconnect
        #[x] get
        #[x] ls
        #[x] open
        #[x] put
        #[x] pwd
        #[x] quit
        #[x] rename
        #[x] user

#TODO: features
        #[x] count transfered data
        #[x] speed
        #[x] fix inaccurate speed
        #[x] fix receive data function
        #[x] fix ls function after fix the above
        #[x] change recv_data func to work with file too
        #[x] make send_data func.
        #[x] fix add another print respond for 150 starting data transfer
        #[x] add new line when enter password
        #[x] get condition for various combination of input
        #[x] get condition for various combination of input
        #[x] exception for file not found in put command
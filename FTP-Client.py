import socket
import time

cmd_sock = None
host = None

not_need_connection = [
    "bye",
    "open",
    "quit"
]

need_connection = [
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
]


def send_ftp(socket, str): #format string and send to ftp server
    socket.sendall(f"{str}\r\n".encode())
    return

def print_resp(socket):
    print(socket.recv(1024).decode(), end='')

def close_sock():
    global cmd_sock
    try:
        cmd_sock.close()
        cmd_sock = None
        return
    except:
        cmd_sock = None
        return

def open_data_conn():
    global host
    #bind listing socket
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock.bind((host, 0))
    data_sock.listen()
    port = data_sock.getsockname()[1] #get port number

    host_part = host.replace('.', ',')
    port = f"{port:016b}" #convert port number to bianry
    port_1 = int(port[0:8], 2) #first part of the port
    port_2 = int(port[8:16], 2) #second part of the port
    send_ftp(cmd_sock, f"PORT {host_part},{port_1},{port_2}")
    print_resp(cmd_sock)
    #TODO: add exception if fail
    return data_sock

def recv_data(data_sock):
    data_conn, data_addr = data_sock.accept()
    size = 0
    start_time = time.time() #time at the start of data transfer
    while True:
        data = data_conn.recv(1024)
        if data:
            print(data.decode(), end='')
            size += len(data)
        else:
            break
        
    end_time = time.time() #time at the end of data transfer
    elapsed_time = end_time - start_time
    if elapsed_time == 0: #prevent very fast transfer(start_time = end_time) from causeing devide by 0
        elapsed_time = 0.001
    #!debug
    print(size,start_time, end_time, elapsed_time)
    speed = size / (elapsed_time * 1000)
    print(f"ftp: {size} bytes received in {elapsed_time:.3f}Seconds {speed:.2f}Kbytes/sec.")
    return


def ascii():
    return

def binary():
    return

def bye():
    try:
        send_ftp(cmd_sock, "QUIT")
        print_resp(cmd_sock)
        close_sock()
    except:
        pass
    exit()


def cd(remote_dir):
    send_ftp(cmd_sock, f"CWD {remote_dir[0]}")
    print_resp(cmd_sock)
    return

def close():
    try:
        send_ftp(cmd_sock, "QUIT")
    except:
        print("Not connected.")
        return;

    print_resp(cmd_sock)
    close_sock()
    return

def delete(remote_file):
    return

def get(*args):
    return

def ls(remote_dir = []):
    data_sock = open_data_conn()
    if remote_dir:
        send_ftp(cmd_sock, f"NLST {remote_dir[0]}")
    else:
        send_ftp(cmd_sock, "NLST")

    resp = cmd_sock.recv(1024).decode()
    print(resp, end='')
    if resp.split()[0] != "150": #If not starting data transfer
        return

    recv_data(data_sock)
    print_resp(cmd_sock)
    return

def open(host_local = None, port = 21):
    global cmd_sock
    global host

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

    #attemp establish connection
    try:
        cmd_sock.connect((host_local, port))
    except ConnectionRefusedError:
        print("> ftp: connect :Connection refused")
        close_sock()
        return
    except socket.timeout:
        print("> ftp: connect :Connection timed out")
        close_sock()
        return
    except socket.gaierror:
        print(f"Unknown host {host_local}.")
        close_sock()
        return
    except Exception as e:
        print(type(e).__name__, e.args)
        return

    print_resp(cmd_sock)

    #login
    user = input(f"User ({host_local}:(none)): ")
    send_ftp(cmd_sock, f"USER {user}")
    print_resp(cmd_sock)
    password = input("Password: ")
    cmd_sock.sendall(f"PASS {password}\r\n".encode())

    login_respond = cmd_sock.recv(1024).decode()
    respond_code = login_respond.split()[0]

    if respond_code == "230":
        print(login_respond, end='')
    elif respond_code == "331":
        print(login_respond)
        print("Login failed.")

    return

def put(*args):
    return

def pwd():
    send_ftp(cmd_sock, f"XPWD")
    print_resp(cmd_sock)
    return

def rename(*args):
    return

def user(*args):
    return

while True:
    input_str = input("ftp> ")

    #input sanitization
    input_list = input_str.split()
    if not input_list: #check for empty command
        continue
    
    command = input_list[0]

    if len(input_list) > 1:
        arg = input_list[1:]
    else:
        arg = ""
    
    if command in not_need_connection:
        match command:
            case "bye":
                bye()

            case "open":
                open(*arg)

            case "quit":
                bye()

    elif command in need_connection:
        if not cmd_sock:
            print("Not connected.")
            continue

        match command:
            case "ascii":
                ascii()
            
            case "binary":
                binary()
            
            case "cd":
                cd(arg)

            case "close":
                close()

            case "delete":
                delete(arg)

            case "disconnect": # disconnect = close
                close()

            case "get":
                get(arg)

            case "ls":
                ls(arg)

            case "put":
                put(arg)

            case "pwd":
                pwd()

            case "rename":
                rename(arg)

            case "user":
                user(arg)

    else:
        print("Invalid command.")



#TODO: Command
        #[ ] ascii
        #[ ] binary
        #[x] bye
        #[x] cd
        #[x] close
        #[ ] delete
        #[x] disconnect
        #[ ] get
        #[x] ls
        #[x] open
        #[ ] put
        #[x] pwd
        #[x] quit
        #[ ] rename
        #[ ] user

#TODO: features
        #[x] count transfered data
        #[x] speed
        #[x] fix inaccurate speed
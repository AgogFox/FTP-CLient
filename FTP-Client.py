import socket

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

def ls(remote_dir = ""):
    data_sock = open_data_conn()
    send_ftp(cmd_sock, f"NLST {remote_dir}")

    resp = cmd_sock.recv(1024).decode()

    if resp.split()[0] != "150":
        print(f"Something when wrong. {resp}")
        return

    print(resp, end='')
    data_conn, data_addr = data_sock.accept()
    while True:
        data = data_conn.recv(1024).decode()
        if data:
            print(data, end='')
        else:
            break
    return

def open(host_local = None, port = 21):
    global cmd_sock
    global host
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

    print(login_respond)

    if respond_code == 230:
        print(login_respond)
    elif respond_code == 331:
        print(login_respond)
        print("Login failed.")

    return

def put(*args):
    return

def pwd():
    return

def rename(*args):
    return

def user(*args):
    return

while True:
    input_str = input("ftp> ")

    #input sanitization
    input_list = input_str.split()
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


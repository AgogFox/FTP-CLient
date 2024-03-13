import socket

s = None
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
    global s
    try:
        s.close()
        s = None
        return
    except:
        s = None
        return

def open_data_conn():
    global host
    #bind listing socket
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock.bind((host, 0))
    port = data_sock.getsockname()[1] #get port number

    host_part = host.replace('.', ',')
    port = f"{port:016b}" #convert port number to bianry
    port_1 = int(port[0:8], 2) #first part of the port
    port_2 = int(port[8:16], 2) #second part of the port
    send_ftp(s, f"PORT {host_part},{port_1},{port_2}")
    print_resp(s)
    return data_sock


def ascii():
    return

def binary():
    return

def bye():
    try:
        send_ftp(s, "QUIT")
        print_resp(s)
        close_sock()
    except:
        pass
    exit()


def cd(remote_dir):
    return

def close():
    try:
        send_ftp(s, "QUIT")
    except:
        print("Not connected.")
        return;

    print_resp(s)
    close_sock()
    return

def delete(remote_file):
    return

def get(*args):
    return

def ls(remote_dir = ""):
    send_ftp(s, f"NLST {remote_dir}")
    print_resp(s)
    return

def open(host_local = None, port = 21):
    global s
    global host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not host_local:
        host_local = input("To ")
    
    if not host_local:
        print("Usage: open host name [port]")
        return
    
    #set recieved host from funciton to global var for future use
    host = host_local 

    #attemp establish connection
    try:
        s.connect((host_local, port))
    except ConnectionRefusedError:
        print("> ftp: connect :Connection refused")
        close_sock()
        return
    except TimeoutError:
        print("> ftp: connect :Connection timed out")
        close_sock()
        return
    except Exception as e:
        if type(e).__name__ == "gaierror":
            print(f"Unknown host {host_local}.")
        #print(type(e).__name__, e.args)
        close_sock()
        return

    print_resp(s)

    #login
    user = input(f"User ({host_local}:(none)): ")
    send_ftp(s, f"USER {user}")
    print_resp(s)
    password = input("Password: ")
    s.sendall(f"PASS {password}\r\n".encode())

    login_respond = s.recv(1024).decode()
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
        arg = []
    
    if command in not_need_connection:
        match command:
            case "bye":
                bye()

            case "open":
                open(*arg)

            case "quit":
                bye()

    elif command in need_connection:
        if not s:
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


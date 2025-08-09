# Basic SSH connection test with paramiko

import paramiko

host = "127.0.0.1"  # Localhost
user = "testsrtest"   # This should be the user you just created
password = "testpass0078"  # This should be the password you just set

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=3)
    print(f"Connected to {host} with {user}:{password}")
except paramiko.AuthenticationException:
    print(f"Failed login for {user}:{password}")
finally:
    client.close()
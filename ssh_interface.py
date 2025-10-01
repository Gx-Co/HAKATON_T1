import paramiko
from bs4 import BeautifulSoup

hostname = "203.81.208.25"
password = "#@~79j0gb2$a"
username = "team06"
port = 22006

address = "http://dvwa.local/"

client = paramiko.SSHClient()


client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, port, username, password)

# stdin, stdout, stderr = client.exec_command(r"""curl -i http://dvwa.local/login.php""")
stdin, stdout, stderr = client.exec_command(r"""curl --user admin:password http://dvwa.local/vulnerabilities/sqli/""")


# soup = BeautifulSoup(stdout.read().decode(), "lxml")
#
# user_token = soup.find_all("input", {"name": "user_token"})[0].attrs["value"]
# csrf_token = soup.find_all("input", {"name": "csrftoken"})[0].attrs["value"]

# print(f"stdin:\n{stderr.read().decode()}\n\n\nstdout:\n{stdout.read().decode()}\n\n\nstderr:\n{stderr.read().decode()}")
# client.exec_command("curl -c http://dvwa.local/login.php")


# stdin, stdout, stderr = client.exec_command(rf"""curl -L -c cookies.txt -b cookies.txt \
#   -d "username=admin&password=password&Login=Login&user_token={user_token}&csrftoken={csrf_token}" {address}""")

client.exec_command(fr"""ssh username@ip_address -p{port}""")

print(f"stdin:\n{stderr.read().decode()}\n\n\nstdout:\n{stdout.read().decode()}\n\n\nstderr:\n{stderr.read().decode()}")

client.close()

# http://dvwa.local/vulnerabilities/sqli/?id=0x27204f5220313d31202d2d&Submit=Submit&csrftoken=186a6ee36ac29700d585f7225e5746cfde5c5dc58d580181e480a684fa92e7c84a5235c1ceae4031#
# http://dvwa.local/index.php
# http://dvwa.local/vulnerabilities/sqli/

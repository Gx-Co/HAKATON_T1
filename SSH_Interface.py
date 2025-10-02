
import paramiko
import requests
from bs4 import BeautifulSoup

class SimpleSSHAuth:
    def __init__(self, ssh_host, ssh_port, ssh_user, ssh_pass, url, site_user, site_pass):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.url = url
        self.site_user = site_user
        self.site_pass = site_pass
        self.ssh = None
        self.session = requests.Session()
    
    def connect_ssh(self):
        """Подключение к VM по SSH"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ssh_host, self.ssh_port, self.ssh_user, self.ssh_pass, timeout=10)
            print("✅ SSH подключение установлено")
            return True
        except Exception as e:
            print(f"❌ Ошибка SSH: {e}")
            return False
    
    def run_ssh_command(self, command):
        """Выполнение команды на VM"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if output:
                print(f"📋 Output: {output.strip()}")
            if error:
                print(f"⚠️ Error: {error.strip()}")
            return output
        except Exception as e:
            print(f"❌ Ошибка команды: {e}")
            return ""
    
    def website_login(self):
        """Авторизация на сайте"""
        try:
            # Получаем страницу логина
            response = self.session.get("http://10.0.1.106", headers={"Host": "dvwa.local"})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем форму
            form = soup.find('form')
            if not form:
                print("❌ Форма не найдена")
                return False
            
            # Ищем поля ввода
            username_field = None
            password_field = None
            
            for input_tag in form.find_all('input'):
                input_type = input_tag.get('type', '').lower()
                name = input_tag.get('name', '').lower()
                
                if input_type == 'text' or 'user' in name or 'login' in name or 'email' in name:
                    username_field = input_tag.get('name')
                elif input_type == 'password':
                    password_field = input_tag.get('name')
            
            if not username_field or not password_field:
                print("❌ Не найдены поля логина/пароля")
                return False
            
            # Подготавливаем данные для отправки
            form_data = {username_field: self.site_user, password_field: self.site_pass}
            
            # Добавляем остальные поля формы
            for input_tag in form.find_all('input'):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name and name not in [username_field, password_field]:
                    form_data[name] = value
            
            # Отправляем форму
            action = form.get('action', '')
            if action.startswith('/'):
                base_url = '/'.join(self.url.split('/')[:3])
                login_url = base_url + action
            else:
                login_url = self.url
            
            method = form.get('method', 'get').lower()
            
            if method == 'post':
                login_response = self.session.post(login_url, data=form_data)
            else:
                login_response = self.session.get(login_url, params=form_data)
            
            # Проверяем успешность авторизации
            if login_response.status_code == 200 and login_response.url != self.url:
                print("✅ Авторизация на сайте успешна")
                return True
            else:
                print("❌ Авторизация не удалась")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка авторизации: {e}")
            return False
    
    def close(self):
        """Закрытие соединений"""
        if self.ssh:
            self.ssh.close()
        self.session.close()
        print("🔌 Соединения закрыты")

def main():
    # === НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ ===
    SSH_HOST = "203.81.208.25"      # IP виртуальной машины
    SSH_PORT = 22006                # SSH порт
    SSH_USER = "team06"               # SSH пользователь
    SSH_PASS = "#@~79j0gb2$a"           # SSH пароль
    
    URL = "http://dvwa.local/"  # URL сайта для авторизации
    SITE_USER = "admin"             # Логин для сайта
    SITE_PASS = "password"          # Пароль для сайта
    # === КОНЕЦ НАСТРАИВАЕМЫХ ПАРАМЕТРОВ ===
    
    # Создаем экземпляр и выполняем
    ssh_auth = SimpleSSHAuth(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS, URL, SITE_USER, SITE_PASS)
    
    try:
        # Подключаемся по SSH
        if ssh_auth.connect_ssh():
            # Выполняем команды на VM
            ssh_auth.run_ssh_command("whoami")
            ssh_auth.run_ssh_command("pwd")
            ssh_auth.run_ssh_command("ls -la")
            
            # Авторизуемся на сайте
            ssh_auth.website_login()
            
    finally:
        # Всегда закрываем соединения
        ssh_auth.close()

if __name__ == "__main__":
    main()


def INIT():
    pass

def Request(request):
    return [0, 0]

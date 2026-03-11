import http.cookiejar, urllib.request, urllib.parse

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
login_url = 'http://127.0.0.1:8000/login/'
creds = {'username':'admin@example.com','password':'AdminPass123'}
data = urllib.parse.urlencode(creds).encode()
req = urllib.request.Request(login_url, data=data)
resp = opener.open(req)
print('Login response code:', resp.getcode())
print('After login URL:', resp.geturl())
students = opener.open('http://127.0.0.1:8000/admin/students/')
print('Students page code:', students.getcode())
content = students.read().decode('utf-8', errors='ignore')
print('--- students page snippet ---')
print(content[:800])

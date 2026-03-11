#!/usr/bin/env python3
import os
import sys
BASE = os.environ.get('SMOKE_BASE', 'http://127.0.0.1:8000')
USER = os.environ.get('SMOKE_USER', 'admin@example.com')
PASS = os.environ.get('SMOKE_PASS', 'AdminPass123')


def using_requests():
    try:
        import requests
    except Exception:
        return False
    s = requests.Session()
    print('GET', BASE + '/login/')
    r = s.get(BASE + '/login/')
    print('login GET', r.status_code)
    csrftoken = s.cookies.get('csrftoken', '')
    data = {'username': USER, 'password': PASS, 'csrfmiddlewaretoken': csrftoken}
    headers = {'Referer': BASE + '/login/'}
    r = s.post(BASE + '/login/', data=data, headers=headers, allow_redirects=True)
    print('login POST =>', r.status_code, r.url)
    pages = ['/admin/students/', '/admin/programs/', '/admin/classes/']
    for p in pages:
        rp = s.get(BASE + p)
        print(p, rp.status_code, 'len=', len(rp.text))
        snippet = rp.text[:200].replace('\n', ' ')
        print('snippet:', snippet)
    return True


def using_urllib():
    import http.cookiejar, urllib.request, urllib.parse
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    print('GET', BASE + '/login/')
    r = opener.open(BASE + '/login/')
    print('login GET', r.getcode())
    csrftoken = None
    for c in cj:
        if c.name == 'csrftoken':
            csrftoken = c.value
    data = {'username': USER, 'password': PASS, 'csrfmiddlewaretoken': csrftoken or ''}
    data_enc = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(BASE + '/login/', data=data_enc, headers={'Referer': BASE + '/login/'})
    r2 = opener.open(req)
    print('login POST =>', r2.getcode(), r2.geturl())
    pages = ['/admin/students/', '/admin/programs/', '/admin/classes/']
    for p in pages:
        rp = opener.open(BASE + p)
        print(p, rp.getcode())
        txt = rp.read(400).decode('utf-8', errors='ignore').replace('\n', ' ')
        print('snippet:', txt)
    return True


if __name__ == '__main__':
    print('Smoke test against', BASE)
    if using_requests():
        sys.exit(0)
    else:
        print('requests not available, falling back to urllib')
        try:
            using_urllib()
            sys.exit(0)
        except Exception as e:
            print('Smoke test failed:', e)
            print('If using requests, install: pip install requests')
            sys.exit(2)

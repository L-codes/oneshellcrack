# 0x00 Oneshellcrack
oneshellcrack 是一个非常快的webshell暴力破解工具，工作原理是多线程并通过一次性发送大量的密码探测POST数据进行爆破，是其他普通webshell密码暴力破解
工具的数千倍

# 0x01 Features
- 速度极快，经过本地服务器测试平均破解可达每秒22万个密码
- 支持python 2.x和3.x
- 支持网络或服务器性能影响，请求失败后的自动重新请求
- 支持批量大密码字典文件
- 支持自动生成常见默认密码和短密码枚举
- 支持自动过滤不合法的密码

# 0x02 Parameter description
```
$ python3 oneshellcrack.py -h

  ___             ____  _          _ _  ____                _    
 / _ \ _ __   ___/ ___|| |__   ___| | |/ ___|_ __ __ _  ___| | __
| | | | '_ \ / _ \___ \| '_ \ / _ \ | | |   | '__/ _` |/ __| |/ /
| |_| | | | |  __/___) | | | |  __/ | | |___| | | (_| | (__|   < 
 \___/|_| |_|\___|____/|_| |_|\___|_|_|\____|_|  \__,_|\___|_|\_\                                                           

               [ Author L       Version 1.0.1 ]

[ Github ] https://github.com/L-codes/oneshellcrack

usage: oneshellcrack.py [-h] [-m] [-n] [-r] [-s] [-t] [-w]
                        [-p FILE [FILE ...]]
                        URL

positional arguments:
  URL                  Target URL

optional arguments:
  -h, --help           show this help message and exit
  -m , --max-threads   specify max threads [default: 200]
  -n , --number        specify max password request [default: auto]
  -r , --retry-nums    specify max retry request [default: 1]
  -s , --shell         specify webshell type
  -t , --timeout       specify request timeout [default: 8]
  -w , --weakpwd-len   specify weak possword lenghts [default: 4]
  -p FILE [FILE ...]   specify possword files [default: Weak passwords]

use examples:
  python oneshellcrack.py http://localhost/shell.php 
  python oneshellcrack.py http://localhost/shell.jsp -n 1000 -m 300
  python oneshellcrack.py http://localhost/shell.asp -p pwd1.lst pwd2.lst
```

# 0x03 Use examples

## Examples 1
```
python3 oneshellcrack.py http://172.16.178.139/a.php     
  ___             ____  _          _ _  ____                _    
 / _ \ _ __   ___/ ___|| |__   ___| | |/ ___|_ __ __ _  ___| | __
| | | | '_ \ / _ \___ \| '_ \ / _ \ | | |   | '__/ _` |/ __| |/ /
| |_| | | | |  __/___) | | | |  __/ | | |___| | | (_| | (__|   < 
 \___/|_| |_|\___|____/|_| |_|\___|_|_|\____|_|  \__,_|\___|_|\_\                                                           

               [ Author L       Version 1.0.1 ]

[ Github ] https://github.com/L-codes/oneshellcrack

 ( Shell:php, Numbers:1500, Threads:200, Retry:1 )

[Crack] No.1751 (0.01s) CODE: 200 - POST Content-Length: 15623                    

[Failed] No password found
[Finish] 2626500 words in 11.922 seconds. (220310 w/s)
```
## Examples 2
```
python3 oneshellcrack.py http://172.16.178.139:8080/1.jsp
  ___             ____  _          _ _  ____                _    
 / _ \ _ __   ___/ ___|| |__   ___| | |/ ___|_ __ __ _  ___| | __
| | | | '_ \ / _ \___ \| '_ \ / _ \ | | |   | '__/ _` |/ __| |/ /
| |_| | | | |  __/___) | | | |  __/ | | |___| | | (_| | (__|   < 
 \___/|_| |_|\___|____/|_| |_|\___|_|_|\____|_|  \__,_|\___|_|\_\                                                           

               [ Author L       Version 1.0.1 ]

[ Github ] https://github.com/L-codes/oneshellcrack

 ( Shell:jsp, Numbers:4000, Threads:200, Retry:1 )

[Crack] No.323  (0.04s) CODE: 200 - POST Content-Length: 28029                    
[INFO] password in No.323, BinaryTree attack...
[Crack] No.327  (0.05s) CODE: 200 - POST Content-Length: 28029                    

[Success] Password: test
[Finish] 1308000 words in 5.811 seconds. (225105 w/s)
```
## Examples 3
```
$ python3 oneshellcrack.py http://172.16.178.133:84/1.asp -p pwd.lst
  ___             ____  _          _ _  ____                _    
 / _ \ _ __   ___/ ___|| |__   ___| | |/ ___|_ __ __ _  ___| | __
| | | | '_ \ / _ \___ \| '_ \ / _ \ | | |   | '__/ _` |/ __| |/ /
| |_| | | | |  __/___) | | | |  __/ | | |___| | | (_| | (__|   < 
 \___/|_| |_|\___|____/|_| |_|\___|_|_|\____|_|  \__,_|\___|_|\_\                                                           

               [ Author L       Version 1.0.1 ]

[ Github ] https://github.com/L-codes/oneshellcrack

 ( Shell:asp, Numbers:1000, Threads:200, Retry:1 )

[Crack] No.607  (0.05s) CODE: 200 - POST Content-Length: 41347                    

[Success] Password: pass&123
[Finish] 607000 words in 5.080 seconds. (119477 w/s)
```

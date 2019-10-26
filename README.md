# web title get

a tool to get title for domain or url

## install

pip3 install --user -r requirements.txt

## use
```
  __           _                  _       _   _ _   _
 / _| __ _ ___| |_  __      _____| |__   | |_(_) |_| | ___
| |_ / _` / __| __| \ \ /\ / / _ \ '_ \  | __| | __| |/ _ \
|  _| (_| \__ \ |_   \ V  V /  __/ |_) | | |_| | |_| |  __/
|_|  \__,_|___/\__|   \_/\_/ \___|_.__/   \__|_|\__|_|\___|

usage: web_title.py [-h] [-d domain.txt] [-u url.txt] [-i ip.txt] [-t 20]
                    [-o result.txt]

A tool that can get title for domains or urls

optional arguments:
  -h, --help            show this help message and exit
  -d domain.txt, --domain domain.txt
                        domain to get title
  -u url.txt, --url url.txt
                        urls to get title
  -i ip.txt, --ip ip.txt
                        ips to get title
  -t 20, --thread 20    threads to get title
  -o result.txt, --outfile result.txt
                        file to result

python3 web_title.py -d domain.txt

python3 web_title.py -u url.txt

python3 web_title.py -i ip.txt

python3 web_title.py -i ip.txt -d domain.txt -u url.txt

python3 web_title.py -u url.txt -t 50
```


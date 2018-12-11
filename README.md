zabbix-lld-sender
===========

`zabbixdiscovery.py` zabbix low level discovery tool
`zabbixsender.py` push hundreds or thousands of item value by one push

`my.vfs.iostat.py` is an example of using zabbixdiscovery.py and zabbixsender.py
`my.cron` put it in the crontab and run it every minute.

Usage
-----

```shell
git clone https://github.com/zgmarx/zabbix-lld-sender

cd zabbix-lld-sender

git clone https://github.com/bsc-s2/pykit

put `my.cron` in the crontab and run it every minute. OR run: iostat -xm 10 2 > /tmp/zbx-iostat-data

python my.vfs.iostat.py

this command will ends with error because we havn't create zabbix LLD on zabbix-server.

`cat /dev/shm/zabbix/my.vfs.iostat`, we'll get something like this:

- my.vfs.iostat[/,%util] 0.23
- my.vfs.iostat[/,avgqu-sz] 0.00
- my.vfs.iostat[/,avgrq-sz] 13.07
- my.vfs.iostat[/,await] 0.05
- my.vfs.iostat[/,r/s] 0.00
- my.vfs.iostat[/,rMB/s] 0.00
- my.vfs.iostat[/,r_await] 0.00
- my.vfs.iostat[/,rrqm/s] 0.00
- my.vfs.iostat[/,svctm] 0.05
- my.vfs.iostat[/,w/s] 48.00
- my.vfs.iostat[/,wMB/s] 0.31
- my.vfs.iostat[/,w_await] 0.05
- my.vfs.iostat[/,wrqm/s] 0.50

```

### Scripts Description

Name     | Description | OS
---------|-------------|----
net.device.stats.py | Exposes network interface info from `/sys/class/net/` | Linux
my.vfs.iostat.py    | Exposes mountpoint(disk) I/O statistics.              | Darwin, Linux

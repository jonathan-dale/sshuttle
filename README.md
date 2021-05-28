# [sshuttle docs](https://sshuttle.readthedocs.io/en/stable/how-it-works.html)

Requires no installation on the server side (only a server with ssh and python), but client modifies IP tables so you must run the process as root.
Install
```bash
sudo pip install sshuttle
```

Tunnel to all networks (0.0.0.0/0)
```bash
sudo sshuttle -r user@server 0/0
```

Tunnel to a particular subnet
```bash
sudo sshuttle -r admin@bastion:31415 192.168.1.1/24
```
To use a particular ssh-key use the `-e CMD` or `--ssh-cmd CMD` options, also `--dns` option to force all requests thorugh the tunnel.
```bash
sudo sshuttle -r admin@bastion:22 --dns 192.168.1.0/24 --ssh-cmd 'ssh -i ~/.ssh/ssh.privatekey'
```



# Creating an sshuttle service
> Give credit where credit is due 
> https://perfecto25.medium.com/using-sshuttle-as-a-service-bec2684a65fe

1. Create a service account for Sshuttle
 on the client:
```bash
groupadd sshuttle
useradd -d /home/sshuttle -g sshuttle sshuttle
mkdir /home/sshuttle/.ssh
chown -R sshuttle:sshuttle /home/sshuttle
chmod 700 /home/sshuttle/.ssh
```

Generate an ssh key pair
```bash
ssh-keygen -o -a 100 -t ed25519 -N "" -C "sshuttle_key" -f /home/sshuttle/.ssh/id_ed25519
```
Create the service account on all servers you want to connect, add the public key to  
the `authorizek_keys` file.

Change users and attempt to ssh to server
```bash
root@client> su sshuttle
sshuttle@client> ssh targetServer
```

2. Sudo access
Sshuttle client needs sudo access to modify firewall ruels (client side)

add to `/etc/sudoers.d/sshuttle` (must have an empty line before and after)
```bash
sshuttle ALL=(root) NOPASSWD: /usr/bin/python /usr/share/sshuttle/main.py /usr/bin/python --firewall 12*** 0
```
That ^^^^ allows non root users (i.e. sshuttle service account) to launch Sshuttle servivce and modify firewall ports.

3. Install Sshuttle
[Instlation instructions](https://github.com/sshuttle/sshuttle#obtaining-sshuttle)
Clone
```bash
git clone https://github.com/sshuttle/sshuttle.git
cd sshuttle
sudo ./setup.py install
```
Debian
```bash
apt-get install sshuttle
```

4. Create service scripts
- SystemD service file to controll sshuttle  
Move `sshuttle.service` to `/etc/systemd/system/sshuttle.service`
Reload systemd after  
```bash
systemctl daemon-reload
```

create directory for sshuttle
```bash
mkdir /etc/sshuttle
chown sshuttle:sshuttle /etc/sshuttle
```

5. Add the sshuttle.py to /etc/sshuttle
```bash
cp sshuttle.py /etc/sshuttle/
chown sshuttle. /etc/sshuttle/*
chmod +x /etc/sshuttle/sshuttle.py
```

You can now start, stop and restart Sshuttle service using systemd
```bash
systemctl status sshuttle
systemctl start sshutle
systemctl stop sshuttle
```

6. Add the config file
```bash
vi /etc/sshuttle/config.json
```
```bash
{
  "HopServerA": [
    "12.182.293.180/32",
    "129.33.78.18/32",
    "129.13.280.0/24",
    "sftp.somehost.com"
  ],
  "HopServerB": [
    "11.38.26.0/24"
  ]
}
```

Now start the tunnel
```bash
systemctl restart sshuttle
```




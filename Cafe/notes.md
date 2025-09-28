# lessons 

[Stack Overflow question - What is the difference between 0.0.0.0, 127.0.0.1 and localhost?](https://stackoverflow.com/questions/20778771/what-is-the-difference-between-0-0-0-0-127-0-0-1-and-localhost)

## binding ip to 0.0.0.0 to have remote acess on the redis server

edit (file /etc/redis/redis.conf) bind 127.0.0.1 to bind 0.0.0.0 and run (sudo service redis-server restart) to restart the server 


Important: If you don't use a firewall (iptables, ufw..) to control who connects to the port in use, ANYONE can connect to this Redis instance. Without using Redis' AUTH that means anyone can access/change/delete your data. Be safe!

^^ after doing this i learned that i needed to binding the flask app not the redis

- Two addresses (`127.0.0.1:5000` & `172.18.0.3:5000`) show up because containers have both **loopback + bridge IPs**. Only host-mapped port works outside.  
- Always check if files like `requirements.txt` are in the **right context** (Docker build fails otherwise).  
- Redis doesn’t need a custom build unless I want to tweak configs.  
- **Volume mounts** = persist Redis data if I want counts/orders to survive container restarts.  
# Proxying BuildBot behing Nginx

In order to provide access to BuildBot via HTTPS we need to setup Reverse Proxy. The whole documentation on how to setup is available from the [official documentation](http://docs.buildbot.net/latest/manual/cfg-www.html#reverse-proxy-configuration).

## BuildBot configuration

In order to configure BuildBot for successful proxying two things must be done:

1. The uri of the server should be set to the front-facing server in order for links to work. In our case it is `https://maxscale-ci.mariadb.com/`:

```python
c['buildbotURL'] = "https://maxscale-ci.mariadb.com/"
```

2. Allow direct connections to BuildBot only via the localhost interface in order to prevent unauthorized connections:

```python
c['www'] = dict(
port="tcp:8010:interface=127.0.0.1",
)
```

After modifying the configuration the BuildBot instance must be restarted.

## Nginx configuration

The configuration file for BuildBot should be placed in `/etc/nginx/sites-available` directory. Then the symbolic link to this file should be added to `/etc/nginx/sites-enabled` directory.

The base of the configuration for the Nginx follows the official guides:

* Official Nginx guide on SSL configuration, [link](http://nginx.org/en/docs/http/configuring_https_servers.html).
* Official Nginx guide on Reverse Proxying, [link](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/).
* Official BuildBot documentation, [link](http://docs.buildbot.net/latest/manual/cfg-www.html#reverse-proxy-configuration)

The noticeable configuration options that should be done include:

* Enable redirection from HTTP port to HTTPS:
```
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        server_name maxscale-ci.mariadb.com _;

        location / {
                return 302 https://$server_name$request_uri;
        }
}
```
* Enable SSL and HTTP2 support on HTTPS port:
```
server {
        listen 443 ssl http2 default_server;
        listen [::]:443 ssl http2 default_server;
}
```
* Configure SSL sertificates:
```
ssl_certificate /etc/path_to_cert;
ssl_certificate_key /etc/path_to_key;
include snippets/ssl-params.conf;
```
* Specify server name:
```
server_name maxscale-ci.mariadb.com _;
```
* Specify proxy settings to the main application. We assume that the application is running on http://localhost:8010 as configured previously:
```
location / {
    include proxy_params;
    proxy_pass http://localhost:8010;
}
```
* Specify proxy settings specific end-points for Web Sockets and other API endpoints:
```
location /sse {
    proxy_buffering off;
    proxy_pass http://localhost:8010;
}

location /ws {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://localhost:8010;
    proxy_read_timeout 6000s;
}
```
When configuration is done, the Nging configuration must be reloaded.

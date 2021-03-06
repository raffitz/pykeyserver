# Pykeyserver

An HKP server built on python.

Not meant for use in production!
Do not use this in production!

## Running

To run this server, execute:

```
python3 server.py
```

By default this will bind to the *loopback* interface (127.0.0.1) and to port 11371.

If, instead, you want to bind to all interfaces on another port, you can do:

```
python3 server.py --address 0.0.0.0 --port 8080
```

## Troubleshooting

### gpg indicates there's no keyserver

Some gpg packages don't include a default configuration for dirmngr.
This may cause the client to be unable to send or receive keys to the server.

In order to solve this, edit the file `~/.gnupg/dirmngr.conf` and add the following line:

```
standard-resolver
```

Do be mindful that in certain environments, this may not be the desired behaviour.
If you are unsure, please contact your network administrator or your IT supervisor before enabling this option.

## More information

This was developed in a classroom environment for a classroom environment: to share temporary keys generated by students amongst themselves, without contaminating or interfering with notable public keyservers.

Due to hardware restrictions, notable alternatives such as [Hockeypuck](https://github.com/hockeypuck/hockeypuck) or [Hagrid](https://gitlab.com/hagrid-keyserver/hagrid) were not suitable.

[SKS](https://github.com/SKS-Keyserver/sks-keyserver)'s lack of post-systemd documentation (every single configuration document I read mentioned initscripts) made it unsuitable as well.

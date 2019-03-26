# How to install mkvirtualenv

If you don't have `mkvirtualenv` but you have `virtualenv`, follow this:

```
$ virtualenv -p python3.7 first-env
$ source first-env/bin/activate
```

```
(first-env)$ pip install virtualenvwrapper
(first-env)$ source first-env/bin/virtualenvwrapper.sh
(first-env)$ mkvirtualenv second-env
```
should throw you into `second-env`.

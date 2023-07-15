### For development
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements_dev.txt
```

### Create required libraries for lambda deployment
```bash
$ pip install -r requirements.txt -t lambda_lib
```

### Disclaimer
- Please don't use this script in production env. Also there will be modifications based on individual env.
#### Prerequisite
- Make sure to have OCI config setup correctly
- Open script.py file and modify line 17 to enter correct compartment OCID
- Assumption is all the stacks are related to compute VM.

#### Run app

- Create virtual env
  - Follow this documentation. Click [here](https://docs.python.org/3/tutorial/venv.html)

- Run following command in terminal to install the dependency
```
pip install -r requirements
```

- Run following command in terminal to execute script
```
python script.py
```



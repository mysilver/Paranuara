# Paranuara
Instructions:
This sample API is written in Python 3.6. Follow the following steps to run the service:
- install requirements by
 ```shell script
pip3 install -r requirements.txt
```
- run service by:
```shell script
python3 service.py
```
- browse the following like to access the swagger documentation of the endpoints
```html
http://127.0.0.1:5000/
```
- Since all operations have been implimented as GET Method, you can run test example by just opening the following linked in your browser:
```html
http://127.0.0.1:5000/companies/1/employees
http://127.0.0.1:5000/people/4/common-friends/5
http://127.0.0.1:5000/people/23/favorite
```
## 
Please be noted that this code will start downloading required corpus for Natural Language Tool Kit (NLTK). NLTK is being used for differentiating between vegetables and fruits.
 
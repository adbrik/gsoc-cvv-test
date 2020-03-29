# Google Summer of Code 2020
This is my selection test for C3G's project proposal for Ingesting the Canadian Common CV
### Installation
* Clone or download the git repository, and open the folder.
```
$ git clone https://github.com/adbrik/gsoc-cvv-test.git
$ cd gsoc-cvv-test
```
* Create and activate a virtual environment:
```
$ python3 -m venv venv
$ . venv/bin/activate
```
* Install the requirements inside the app folder
```
$ pip install -r requirements.txt
```
* Once the process finishes execute app.py
```
$ python app.py
```
If there is no sqlite database, it will be generated.

The api is available at
```
127.0.0.1:5000
```
### Endpoint Documentation
**/**
returns a markdown rendering of this README.

**/posts**
There are two options:
* /posts 
  * returns all posts by the order they went into the database.
* /posts?sortby=\<variable\>
  * __if \<variable\> is view__ this : returns all posts sorted by ViewCount (DESC)
  * __if \<variable\> is score__ this : returns all posts sorted by Score (ASC)

**/postsearch**
* /postsearch?search=\<variable\>
  * returns posts that contain <variable> in the Title or Body.
  * __if \<variable\> is null__, then all posts will be returned.

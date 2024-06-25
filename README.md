1. install requirements
```bash
pip install -r requirements.txt
```

2. start neo4j docker
Ensure you have [Docker](https://www.docker.com) installed.

```python
python neo4j_docker_start.py
```

3. Create user in database
http://localhost:7474
user: neo4j
pass: neo4j

You will be prompted to create a new password. 

4. Add new password to app.py

```python
def main():
    uri = "bolt://localhost:7687"
    user = "neo4j" 
    password = "the_new_password" # <--add password here

    url="http://page-to-graph.com" 
```

5. Add the page you'd like to graph

```python
def main():
    uri = "bolt://localhost:7687"
    user = "neo4j" 
    password = "the_new_password" 

    url="http://page-to-graph.com" # <-- add url here
```

6. Run the app
```python
python app.py
```




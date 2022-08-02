两个字典合并


```python
dict1 = {"user":"zhangsan","age":18}
dict2 = {"user":"lisi","age":15}
dict3 = {}
## 1.update
# dict3.update(dict1)
# dict3.update(dict2)

dict1.update(dict2)
print(dict)
```

    {'user': 'lisi', 'age': 15}



```python
dict1 = {"user":"zhangsan","age":18}
dict2 = {"user":"lisi","age":15}
dict3 = {}

dict3 = dict1.copy()
dict3 = dict2.copy()
print(dict3)
```

    {'user': 'lisi', 'age': 15}



```python
dict1 = {"user":80,"age":18}
dict2 = {"user":90,"age":15}
dict3 = {}

dict3 = {**dict1, **dict2}
print(dict3)
```

    {'user': 90, 'age': 15}



```python

```

两个字典合并
case01:key不同的场景多用 update
case02:


```python
"""
适用合并两个字典（key不能相同否则会被覆盖）
"""
A = {'a': 11, 'b': 22}
B = {'c': 48, 'd': 13}
#update() 把字典B的键/值对更新到A里
A.update(B)
print(A)
```

    {'a': 11, 'b': 22, 'c': 48, 'd': 13}



```python
"""
copy 不是很好用，需结合update
"""
dict1 = {'a': 11, 'b': 22}
dict2 = {'c': 48, 'd': 13}

dict3 = {}

dict3 = dict1.copy()
#dict3 = dict2.copy()

print(dict3)
```

    {'a': 11, 'b': 22}



```python
"""
{**dict1, **dict2} python3.5 之后才支持

多个字典可定义方法传入
"""
dict1 = {'a': 11, 'b': 22}
dict2 = {'c': 48, 'd': 13}

dict3 = {}

dict3 = {**dict1, **dict2}
print(dict3)

## 多个字典定义方法
def merge(dict1, dict2, dict3):
    return {**dict1, **dict2, **dict3}

merge(dict1, dict2, dict3)
```

    {'a': 11, 'b': 22, 'c': 48, 'd': 13}





    {'a': 11, 'b': 22, 'c': 48, 'd': 13}




```python
"""
适用多种场合，多字典存在相同key需要合并相加的场景比较适用
"""
def sum_dict(a,b):
  temp = dict()
  # python3,dict_keys类似set； | 并集
  for key in a.keys()| b.keys():
    temp[key] = sum([d.get(key, 0) for d in (a, b)])
  return temp
 
def test():
  #python3使用reduce需要先导入
  from functools import reduce
  #[a,b,c]列表中的参数可以2个也可以多个，自己尝试。
  return print(reduce(sum_dict,[a,b,c]))
 
a = {'a':1, 'b':2, 'c':3}
b = {'a':1, 'b':3, 'd':4}
c = {'g':3, 'f':5, 'a':10}
test()
```

    {'b': 5, 'g': 3, 'd': 4, 'a': 12, 'f': 5, 'c': 3}



```python

```

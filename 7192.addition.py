Python 3.14.2 (tags/v3.14.2:df79316, Dec  5 2025, 17:18:21) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> class calculator:
...         def addition (self,*args):
...             return sum (args)
... c=calculator()
SyntaxError: invalid syntax
>>>     c= calculator()
...     
SyntaxError: unexpected indent
>>> 
>>> c=calculator
Traceback (most recent call last):
  File "<pyshell#6>", line 1, in <module>
    c=calculator
NameError: name 'calculator' is not defined

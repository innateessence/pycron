# pycron

* Just a fun project for supporting cron syntax for python threads
* In other words, this is a (cron-ish) task scheduler avaliable in pure python

## Quickstart

example usage:

```python

from pycron import PyCron

def my_python_func_to_schedule(foo: str):
    # some interesting code here
    print(f"foo is: {foo}")
    with open("my_py_log", 'a') as f:
        f.write(f"foo is {foo}")

def my_bash_task_to_schedule(foo: str):
    # some system calls to make
    os.system(f"echo foo is {foo}")
    os.system(f"echo foo is {foo} >> my_bash_log")

pycron = PyCron()
pycron.add('* * * * *', my_python_func_to_schedule, "foobar")
pycron.add('* * * * *', my_bash_task_to_schedule, "buzz")
pycron.start()
# Now both functions will run under their own thread whenever
# the system clock hits 00 seconds
# just like how you'd expect a cronjob to behave
```

## Testing

* `python test.py`

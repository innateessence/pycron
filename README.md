# pycron

## What is this

* Just a fun project for supporting cron-ish syntax for python threads
* In other words, this is a (cron-ish) task scheduler avaliable in pure python

## Why does this exist

* Because I wanted cron-like behavior for pure Python threads without pulling in celery
* Because sometimes I find I want something highly niche and custom, that is not supported by the major packages such as celery
* It's a good foundation for a project I may or may not take on in the future

## What this is not
* A replacement for celery.
* Production-grade software

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

* Running the test cases: `python test.py`
* Interactive testing / debugging: `python pycron.py`

## Improvements

* Adding a system unit such as a `systemd` service would probably be a good idea

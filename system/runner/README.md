# pyrunner
Python module for running many programs(modules) using single entry point and code base

# Basic usage
```python
from runner import Runner
def main():
    r = Runner('test_modules')
    r.run('test_run.Main')
```
In code above we created Runner instance with directory with runnables, 
where required modules to run will be searched. 
Then we called method run, and passed to them module name with class name which required to instantiate  and exec.
You can pass only class name to method run, but you need to pass module name, containing this class into Runner constructor

#pysub
Python wrapper for submitting jobs via bsub with the option to do so in a container environment. 

## Setup
```
make install-full
```

This creates a pysub config file ~/.pysub
that contains default parameters that
can be overwritten for each specific run:
```
num_gpus = 1
memory = 25600
working_directory = .
singularity = ""
host = ""
queue = "normal"
environment = ""
batch = False
mount_dirs = ""
```

## Usage
There are three useful ways to use pysub:

1. Direct usage via command line arguments (overwrites config file defaults):
```
python run.py -p "python train.py" -c 5 -g 1 -q normal -s path-to-singularity-container

python run_singularity 
```

2. Indirect call via another script:
```python
from pysub.run import run

run(command="python train.py",
    num_cpus=5,
    num_gpus=1,
    queue=normal,
    execute=True)
```

3. Command creation and subsequent call:
```python
from pysub.run import run
from subprocess import check_call

run_command = run(command="python train.py",
                  num_cpus=5,
                  num_gpus=1,
                  queue=normal,
                  execute=False)

check_call(run_command,
           shell=True)
```

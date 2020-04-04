---
title: Parameter Sweeps
header-includes:
    <link href="styles.css" rel="stylesheet"/>
---

# Overview

This script is a generic way to setup parameter sweeps of system
biology models. The specific application here is Copasi but the
ultimate goal is to work with all types of application. Very
broadly it takes some input data from the user in a specific
format. The input specifies the parameter sweep which is a list
of parameter combinations. This script mainly generates the sweep
space, runs a particular task for each element of the space and
stores the corresponding output in different formats. Any subset
of this space can be selected for plotting or individual
queries. The same setup will also be used for global and local
sensitivity analysis.

# How to Run

This package has been made as self-contained as possible. The required
packages are listed in the file `requirements.txt`. In a new machine
the most convenient way to setup the system is to create a python
virtual environment with the [virtualenv](https://virtualenv.pypa.io/en/latest/)
package. Use the following steps for installation

1. Clone the package using `git clone`.

2. Install virtualenv if not already available using the [instructions](https://virtualenv.pypa.io/en/latest/installation.html)
from the homepage.

3. Create a new virtual environment in the directory using the following command

```
$ virtualenv ./pyenv
```

Note: The required python version is 2.7 so make sure the default system python
is > 2.7.6. If not point to an alternate python 2.7 interpreter using the `--python`
flag for the `virtualenv` command.

4. Switch to the new environment using

```
$ source ./pyenv/bin/activate
(pyenv) $
```

This should change the prompt as above.

5. Install the necessary packages using pip

```
(pyenv) $ pip install -r requirements.txt
```

6. Download the Copasi executable from the [download page](https://github.com/copasi/COPASI/releases/download/Build-104/COPASI-4.16.104-Linux-64bit.tar.gz)
and add the path to the executable file `CopasiSE` in
system PATH environment variable.

6. Make a test run by running the following command

```
(pyenv) $ python visualize.py Sweep_Information.json
```

If this runs without any error then the system has been
setup correctly.

7. (Optionally) Deactivate the environment after completing
run.

```
(pyenv) $ deactivate
$
```

# Code

The code consists of the following modules

## Sweep

This gets model parameter names and values to be altered in a
specific format (necessary to locate the element in xml) and
generates the overall sweep space. An example run is shown below
for a small dictionary

```python
test_sweep = { "a" : [1,2], "b" : [1,2] }
for elem in Generate_Sweeps(test_sweep):
    print elem
```

This produces the following output

```bash
$ python sweep.py
{'a': 1, 'b': 1}
{'a': 1, 'b': 2}
{'a': 2, 'b': 1}
{'a': 2, 'b': 2}
```

Since there are two different values for each of the keys the
code produces four different combinations of the keys as a sweep
space.

## Change

## Run

## Collect

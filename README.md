
# python extension to ZKBoo


## Installation instructions

Step 1. Download the project structure

```sh
$ git clone <this-web-page>
$ cd <this-web-page>
```

We will call the current directory as `<project_root>`.

Step 2. Download and build ZKBOOpp into the project root

```sh
$ git clone https://github.com/vanchope/ZKBOOpp
$ cd ZKBOOpp
$ mkdir target && cd target
$ cmake ../
$ make
$ ls
libzkboopp.so <...>
```

Step 3. Compile ZKBOOpp-python-binding

```sh
$ cd <project_root>/ZKBOOpp-python-binding
$ make
```

(No need to copy "libzkboopp so" from ZKBoo-fork/target to the current directory, as paths are properly configured in Makefile.)

```sh
$ ls
pyzkboo_helper.so pysha256.so pytrivium.so <...>
```


Step 4. Prepare pyZKBOOpp code

```sh
$ cd <project_root>/pyZKBOOpp
```

In the following, we describe how to configure the python project in PyCharm IDE.

Step 4a.  Build relic

Follow instructions at the [relicwrapper](https://projects.cispa.uni-saarland.de/pryvalov/relicwrapper) web-site to build relic library, but instead of cmake ../, specify a local destination:

```sh
$ cmake -DCMAKE_INSTALL_PREFIX=<project_root>/venv_cpp  ../
$ make
$ make install
```


Step 4b. Build relicwrapper

Download relicwrapper:

```sh
$ cd <project_root>
$ git clone https://projects.cispa.uni-saarland.de/pryvalov/relicwrapper
```

Edit LOCAL_HOME variable in Makefile, so that it point out to `<project_root>/venv_cpp`:

```
LOCAL_HOME = ../venv_cpp/
```

Build relicwrapper:

```sh
$ make
$ make python
$ ls
pyrelic.so <...>
```


Step 4c. Adjust project settings in PyCharm

Add  <project_root>/ZKBOOpp-python-binding/ and <project_root>/relicwrapper to "Content Root".

Go to Run/Debug Configurations, then to your python configuration or Defaults->Python, and edit "Environment variables". Add the following:

```
LD_LIBRARY_PATH = <project-root>/ZKBOOpp/target:<project-root>/venv_cpp/lib
```

Specify in IDE the required pip-packages: parsimonious.

Now you should be able to run python files in <project-root>/pyZKBOOpp in the IDE.

The overall folder project structure an the end should look as follows:

```sh
$ ls
pyZKBOOpp  README.md  relic  relicwrapper  venv27  venv_cpp  ZKBOOpp  ZKBOOpp-python-binding
```

## Credit

Contributions from Ivan Pryvalov ```<pryvalov (at) cs.uni-saarland.de>```, 2017.

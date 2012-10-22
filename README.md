rayage
======

A simple web IDE for intro programming students.

Dependencies:
* python 2.7

First run:
```bash
git submodule init
git submodule update
python set_user_permission_level.py potterh 2
```

Replace _potterh_ with your CAS username.

To run:
```bash
git submodule update
python rayage.py
```


Then visit [https://localhost:8080](https://localhost:8080)

##Making Changes:

When you create stub methods, create an issue so we remember to update these.

Whenever you commit code, create a new entry on the [wiki](https://github.com/MorganBorman/rayage/wiki/Current-Status)
annotated with the date and what changes you made. Include issues you've created.

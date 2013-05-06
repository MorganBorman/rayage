rayage
======

A simple web IDE for intro programming students.

Dependencies:

* python 2.7
* sqlalchemy 0.7

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
python main.py
```


Then visit [https://localhost:8080](https://localhost:8080)

The admin system requires the dojo _dgrid_ module and dependencies.

First make sure _cpm_ is installed: https://github.com/kriszyp/cpm

Then run:
```bash
cd static/lib/
cpm install dgrid
rm -rf dojo/
```

##Making Changes:

When you create stub methods, create an issue so we remember to update these.

Whenever you commit code, create a new entry on the [wiki](https://github.com/MorganBorman/rayage/wiki/Current-Status)
annotated with the date and what changes you made. Include issues you've created.

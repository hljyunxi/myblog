#!/usr/bin/env python
#coding: utf8

import sys, os, atexit

def remove_pidfile(pidfile):
    if pidfile:
        os.remove(pidfile)

def daemon(pidfile=None, wkdir='.', stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)

    # decouple from parent environment
    os.chdir(wkdir)
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)

    # redirect standard file descriptors
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)

    pid = str(os.getpid())

    sys.stderr.write("\ndaemonize: %s\n" %  pid)
    sys.stderr.flush()

    if pidfile:
        file(pidfile,'w+').write("%s\n" % pid)

    atexit.register(remove_pidfile, pidfile)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

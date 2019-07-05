# -*- coding: utf-8 -*-
import sys,os,time


def getfenzi():
    fenzi = len(txt2list(os.path.join('temp','errorid.txt'))) + len(txt2list(os.path.join('temp','usedid.txt')))
    return fenzi-2

def txt2list(path_file, break_mark = '\n'):
    with open(path_file, 'r') as f:
        temp = f.read()
    templist = temp.split(break_mark)
    return templist

def report_progress(fenzi):
    fenmu = len(txt2list(os.path.join('input', os.listdir('input')[0])))
    percent = fenzi/fenmu*100
    buf = "|{}|{:.2f}%" .format(('#'*int(percent)).ljust(100,'-'),percent)
    #(('#' * progress).ljust(100, '-'), % (progress))
    sys.stdout.write(buf)
    sys.stdout.write('\r')
    sys.stdout.flush()

while getfenzi()<len(txt2list(os.path.join('input', os.listdir('input')[0]))):
    report_progress(getfenzi())
    time.sleep(0.1)
sys.stdout.write('\nMission completed')





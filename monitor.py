#! /usr/bin/env python
#-*- coding: utf-8 -*-
# File Name: monitor.py
# Author: Chongge
# IPLab705
# Created Time: Thu 16 Oct 2014 08:48:33 PM CST
# V2 is better. Can dynamic add and del interface
########################################################################
from os import system
import sys
import curses
import threading
from time import sleep

f_name = '/proc/net/dev'

running = True

def caculateSpeed():
    f = open('/proc/net/dev','r')
    f_tmp = f.readlines()
    f.close()
    ret = {}
    for i in f_tmp[2:]:
        l = [ x for x in  i.strip().split(' ') if x]
        iface = l[0][:-1]
        ret[iface]={'rb':l[1],'rp':l[2],'sb':l[9],'sp':l[10]}
    return ret

class ThreadFunc(object):
    num = 2
    ret = caculateSpeed()
    for iface in ret:
        num +=1
        ret[iface]['l_num'] = num
    def __init__(self,func,args,name=''):
        self.name = name
        self.func = func
        self.args = args

    def __call__(self):
        apply(self.func,self.args)

def monitorSpeed(identif,nsec):
    '''identif is for func type,nsec is for timer fuc.
    0:count Packets
	1:cacolate rate'''
    global running
    if identif == 0:
        while running:
            sleep(nsec)
            tmp_ret = caculateSpeed()
            global h,w

            if len(ThreadFunc.ret)<len(tmp_ret):
                line = 0
                for item  in ThreadFunc.ret:
                    if line < ThreadFunc.ret[item]['l_num']:
                        line = ThreadFunc.ret[item]['l_num']
                newItem = list(set(tmp_ret).difference(set(ThreadFunc.ret)))
                for i in newItem:

                    '''
                    ThreadFunc.ret[newItem] = tmp_ret[newItem]
                    line = 0
                    for item in ThreadFunc.ret:
                        try:
                            if line < ThreadFunc.ret[item]['l_num']:
                                line = ThreadFunc.ret[item]['l_num']
                        except:
                            continue'''
                    line += 1
                    ThreadFunc.ret[i] = tmp_ret[i]
                    ThreadFunc.ret[i]['l_num'] = line
                    screen.addstr(ThreadFunc.ret[i]['l_num'],2,i.ljust(15),curses.color_pair(3))
                    screen.refresh()
            elif len(ThreadFunc.ret)>len(tmp_ret):
                line = 0
                for item  in ThreadFunc.ret:
                    if line < ThreadFunc.ret[item]['l_num']:
                        line = ThreadFunc.ret[item]['l_num']
                newItem = list(set(ThreadFunc.ret).difference(set(tmp_ret)))
                for item in newItem:
                    del ThreadFunc.ret[item]
                num = 2
                for item in ThreadFunc.ret:
                    num += 1
                    ThreadFunc.ret[item]['l_num'] = num
                    screen.addstr(ThreadFunc.ret[item]['l_num'],2,item.ljust(15),curses.color_pair(3))
                for i in range(len(newItem)):
                    num += 1
                    screen.addstr(num,2,' '.ljust(w-2),curses.color_pair(3))
                    screen.refresh()




            for iface in ThreadFunc.ret:
                ThreadFunc.ret[iface]['r_packet_num'] = str(int(tmp_ret[iface]['rp'])-int(ThreadFunc.ret[iface]['rp']))
                ThreadFunc.ret[iface]['s_packet_num'] = str(int(tmp_ret[iface]['sp'])-int(ThreadFunc.ret[iface]['sp']))
            for iface in ThreadFunc.ret:
                screen.addstr(ThreadFunc.ret[iface]['l_num'],17,ThreadFunc.ret[iface]['r_packet_num'].ljust(15),curses.color_pair(3))
                screen.addstr(ThreadFunc.ret[iface]['l_num'],32,ThreadFunc.ret[iface]['s_packet_num'].ljust(15),curses.color_pair(3))
            screen.refresh()
    elif identif == 1:
        while running:
            sleep(nsec)
            tmp_ret = caculateSpeed()
            last_ret = ThreadFunc.ret
            for iface in last_ret:
                last_ret[iface]['r_packet_sp'] = str("%.2f" % (float(int(tmp_ret[iface]['rb'])-int(last_ret[iface]['rb']))/(nsec*1024)*8))
                last_ret[iface]['rb'] = tmp_ret[iface]['rb']
                last_ret[iface]['s_packet_sp'] = str("%.2f" % (float(int(tmp_ret[iface]['sb'])-int(last_ret[iface]['sb']))/(nsec*1024)*8))
                last_ret[iface]['sb'] = tmp_ret[iface]['sb']
            for iface in last_ret:
                screen.addstr(last_ret[iface]['l_num'],47,last_ret[iface]['r_packet_sp'].ljust(15),curses.color_pair(3))
                screen.addstr(last_ret[iface]['l_num'],62,last_ret[iface]['s_packet_sp'].ljust(15),curses.color_pair(3))
                total_rate = str(float(last_ret[iface]['r_packet_sp'])+float(last_ret[iface]['s_packet_sp']))
                screen.addstr(last_ret[iface]['l_num'],77,total_rate.ljust(15),curses.color_pair(3))
            screen.refresh()

def waitingforend():
    screen.getch()
    global running
    running = False
    exit(0)


speed_time = [0.2,3]

def main():
    threads = []
    nloops = range(len(speed_time))
    nplus = range(len(speed_time)+1)

    for i in nloops:
        t = threading.Thread(target=ThreadFunc(monitorSpeed,(i,speed_time[i]),monitorSpeed.__name__))
        threads.append(t)
    t = threading.Thread(target=waitingforend)
    threads.append(t)

    for i in nplus:
        threads[i].start()

    for i in nplus:
        threads[i].join()


screen = curses.initscr()
'''if curses.can_change_color():
    curses.init_color(1,COLOR_YELLOW,COLOR_GREEN)
else:
    print "can not"'''
curses.start_color()
curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_GREEN)
curses.init_pair(2,curses.COLOR_RED,curses.COLOR_GREEN)
curses.init_pair(3,curses.COLOR_BLACK,curses.COLOR_GREEN)
curses.use_default_colors()
curses.curs_set(0)  #set cursor invisible
screen.attron(curses.color_pair(1))
screen.bkgd(' ',curses.color_pair(1))
(h,w) = screen.getmaxyx()
# for y in range(h-1):
    # for x in range(w-1):
        # screen.move(y,x)
        # screen.addch(' ')
screen.clear()
screen.border(0)
screen.addstr(0,2,"Edit By Chongge",curses.color_pair(2))
screen.addstr(0,w-20,"Made at IPLab705",curses.color_pair(2))
screen.addstr(1,2,"Iface",curses.color_pair(3))
screen.addstr(1,2,"Iface",curses.color_pair(3))
screen.addstr(1,17,"In-Packets",curses.color_pair(3))
screen.addstr(1,32,"Out-Packets",curses.color_pair(3))
screen.addstr(1,47,"In-Rate",curses.color_pair(3))
screen.addstr(1,62,"Out-Rate",curses.color_pair(3))
screen.addstr(1,77,"Total_Rate",curses.color_pair(3))
screen.addstr(1,w-30,"speed unit:kbits/sec",curses.color_pair(3))
for iface in ThreadFunc.ret:
    screen.addstr(ThreadFunc.ret[iface]['l_num'],2,iface.ljust(15),curses.color_pair(3))
#screen.addstr(3,2,"IPLab705")
screen.refresh()
main()
#screen.getch()
curses.endwin()


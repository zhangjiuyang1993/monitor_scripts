#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import re
import time
import logging
import os
import subprocess
import paramiko
from util import Util, Server, QueueManager, Queue, ServerProp

def logInit(workDir):
    # create logger with 'checkMQepth'
    logger = logging.getLogger('checkMQDepth')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(workDir + '/checkMQDepth.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    # logger.addHandler(ch)

    return logger

def runSysCmd(cmd):
    logger.info('-- Method Name: runSystemCmd - run system command: ' + cmd)
    result = ''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        result += line
    retval = p.wait()
    return result

def sshExecCmd(ip, user, password, cmd):
    logger.info('-- Method Name: sshExecCmd: %s ' % cmd)
    result = ''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 22, user, password)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    for line in stdout.readlines():
        result += line
    ssh.close()
    return result

def sshExecCmdDic(ip, user, password, cmdDic):
    logger.info('-- Method Name: sshExecCmdDic')
    resultDic = {}
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 22, user, password)
    for k, v in cmdDic.iteritems():
        result = ''
        stdin, stdout, stderr = ssh.exec_command(v)
        for line in stdout.readlines():
            result += line
        resultDic[k] = result
    ssh.close()
    return resultDic


def checkQueueDepth(hostname, username, password, queueMgr, q, outDir):
    logger.info("-- Method Name: checkQueueDepth")
    cmdDic = {}
    resultDic = {}

    mqscCmd = 'echo "dis q(' + q.getName() + ') curdepth" | runmqsc ' + queueMgr + ' | grep "CURDEPTH("'
    cmdDic[q.getName()] = mqscCmd

    resultDic = sshExecCmdDic(hostname, username, password, cmdDic)
    for keyQName, vResult in resultDic.iteritems():
        threshold = q.getThreshold()
        depthString = vResult
        depthTurble = re.findall(r'[0-9]+', depthString)
        depthInt = eval(depthTurble[0])
        isExceed = 0
        if depthInt > threshold:
            isExceed = 1

        # csv format data: time, queue manager name, queue name, current depth, threshold
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        logfName = outDir + keyQName.replace('/', '.') + '.log'
        f = open(logfName, 'w')
        curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        fcontent = curTime + ',' \
                 + queueMgr + ',' \
                 + keyQName + ',' \
                 + str(depthInt) + ',' \
                 + str(threshold) + ',' \
                 + str(isExceed) + '\n'
        logger.info("Queue depth status: " + fcontent)
        f.write(fcontent)
        f.close()
        localsh = s.getRootDir()+"/pushToGraylogQDepth.sh "+s.getRootDir()+" "+outDir+" "+logfName
        os.system(localsh)


if __name__ == '__main__':

    cfg = Util()
    servers = cfg.getServers()
    for s in servers:
        logger = logInit(s.getRootDir())
        outDir = s.getRootDir() + s.getLogDir()
        logger.info('## Step One: Check current queue depth. Generate queue status log for ELK.')
        qms = s.getQMs()
        for qm in qms:
            queues = qm.getQueues()
            for q in queues:
                checkQueueDepth(s.getHostname(), s.getUsername(), s.getPassword(), qm.getName(), q, outDir)


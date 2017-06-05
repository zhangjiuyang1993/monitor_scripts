import yaml
from enum import Enum, unique

@unique
class ServerProp(Enum):
    USERNAME = "user"
    PASSWORD = "password"
    ROOTDIR = "root_dir"
    LOGDIR = "log_dir"
    QM = "queue_managers"

@unique
class QMProp(Enum):
    QUEUE = "queues"

@unique
class QueueProp(Enum):
    TH = "threshold"


class Util:

    def __init__(self, path="/home/esb2/mon_scripts/config.yml"):
        self.__configFile = path
        self.__cfg = self.__getCfg__()

    def __getCfg__(self):
        with open(self.__configFile, 'r') as ymlfile:
            return yaml.load(ymlfile)

    def setConfigFile(self, path):
        self.__configFile = path

    def getConfigFile(self):
        return self.__configFile

    def getServers(self):
        servers = []
        for server in self.__cfg:
            serverCfg = self.__cfg[server]
            qmsCfg = self.getValByKey(ServerProp.QM.value, serverCfg)
            qms = []
            for qm in qmsCfg:
                queuesCfg = self.getValByKey(QMProp.QUEUE.value, qmsCfg[qm])
                queues = []
                for queue in queuesCfg:
                    queues.append(Queue(queue, self.getValByKey(QueueProp.TH.value, self.getValByKey(queue, queuesCfg))))
                qms.append(QueueManager(qm, tuple(queues)))
            servers.append(Server(server, self.getValByKey(ServerProp.USERNAME.value, serverCfg), self.getValByKey(ServerProp.PASSWORD.value, serverCfg),
                                  self.getValByKey(ServerProp.ROOTDIR.value, serverCfg), self.getValByKey(ServerProp.LOGDIR.value, serverCfg), tuple(qms)))
        return tuple(servers)

    def getValByKey(self, key, cfg):
        if cfg is None:
            return None
        if key in cfg:
            return cfg[key]
        else:
            return None

class Server:
    def __init__(self, hostname, username, password, rootDir, logDir, queueManagers):
        self.__hostname = hostname
        self.__username = username
        self.__password = password
        self.__rootDir = rootDir
        self.__logDir = logDir
        self.__queueManagers = queueManagers

    def getHostname(self):
        return self.__hostname

    def getUsername(self):
        return self.__username

    def getPassword(self):
        return self.__password

    def getRootDir(self):
        return self.__rootDir

    def getLogDir(self):
        return self.__logDir

    def getQMs(self):
        return self.__queueManagers


class QueueManager:
    def __init__(self, name, queues):
        self.__name = name
        self.__queues = queues

    def getName(self):
        return self.__name

    def getQueues(self):
        return self.__queues


class Queue:
    def __init__(self, name, threshold):
        self.__name = name
        self.__threshold = threshold

    def getName(self):
        return self.__name

    def getThreshold(self):
        return self.__threshold





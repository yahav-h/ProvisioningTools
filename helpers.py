import shlex
import psutil
import subprocess
from time import time
from enum import Enum
from hashlib import sha256
from threading import Thread
from yaml import load, Loader
from dataclasses import dataclass, field
from os.path import abspath, dirname, exists, join


AGENT = 'agent'
SERVER = 'server'


def randHexUUID(): return sha256(time().hex().encode()).hexdigest()


def callInThread(target=None, args=None, daemon=True):
    t = Thread(target=target, args=args, daemon=daemon)
    t.start()
    return t


def readCfg(prototype: str):
    data = None
    if prototype.lower() == AGENT:
        file_path = join(dirname(abspath(__file__)), "agent.yml")
    elif prototype.lower() == SERVER:
        file_path = join(dirname(abspath(__file__)), "server.yml")
    else:
        raise NameError(f"prototype {prototype.lower()} is not supported | try 'agent' or 'server'")
    if not exists(file_path):
        raise FileNotFoundError(f"cannot find file : {file_path}")
    with open(file_path, 'r') as stream:
        data = load(stream, Loader)
    return data


class Commands(Enum):
    SQL_STOP = "sudo service mysql stop"
    SQL_START = "sudo service mysql start"
    SQL_RESTART = "sudo service mysql restart"
    SERVICE_STOP = "sudo %s/start_service.sh"
    SERVICE_START = "sudo %s/stop_service.sh"


class ProcessExecutor:
    @staticmethod
    def execute(cmd: str):
        args = shlex.split(cmd)
        sub_proc = subprocess.Popen(
            args, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE
        )
        pub_proc = psutil.Process(pid=sub_proc.pid)
        print("ID", pub_proc.pid, "RUNNING", pub_proc.is_running())

    @staticmethod
    def find(_: str):
        found = None
        proc_list = []
        for proc in psutil.process_iter():
            proc_list.append(proc)
        for proc in proc_list:
            if _ == proc.name():
                print("[FOUND]", proc)
                found = proc
            else:
                print("[PROCESS]", proc)
        return found


@dataclass
class QueueItem:
    id: str = field(init=True)
    metadata: dict = field(init=True)
    def __repr__(self): return '<QueueItem %r>' % self.__dict__


class Queue:
    stack = {}
    def enqueue(self, id, item): self.stack.setdefault(id, item)
    def update(self, id, item): self.stack.update(id, item)
    def peek(self, id): return self.stack.get(id, None)
    def dequeue(self, id): del self.stack[id]

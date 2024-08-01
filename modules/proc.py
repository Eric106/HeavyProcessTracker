from psutil import process_iter, Process
from dataclasses import dataclass, field


class Process_Info:
    pid : str
    name : str
    cpu_percent : float
    memory_percent : float

    def __init__(self, process: Process) -> None:
        self.pid = process.info['pid']
        self.name = process.info['name']
        self.cpu_percent = process.info['cpu_percent']
        self.memory_percent = process.memory_percent()

    def __repr__(self) -> str:
        return f"PID: {self.pid}, NAME: {self.name}, CPU%: {self.cpu_percent}, MEM%: {(self.memory_percent):.2f}"

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass(frozen=False)
class Tasks:
    process_list : list[Process_Info] = field(init=False)
    top_process_names : dict = field(init=False)

    def __post_init__(self):
        self.top_process_names = dict()

    def get_process_list(self):
        self.process_list = list()
        for process in process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            self.process_list.append(Process_Info(process=process))
        if self.process_list[0].pid == 0: self.process_list.pop(0)

    def sort_process_list(self):
        self.process_list.sort(key=lambda process: process.cpu_percent)

    def filter_process_list(self, name:str = None, cpu_percent: float = None, memory_percent: float = None):
        if name:
            self.process_list = list(filter(lambda process: process.name == name, self.process_list))
        if cpu_percent:
            self.process_list = list(filter(lambda process: process.cpu_percent >= cpu_percent , self.process_list))
        if memory_percent:
            self.process_list = list(filter(lambda process: process.memory_percent >= memory_percent, self.process_list))
    
        for process in self.process_list:
            self.top_process_names[process.name] = {'CPU%':process.cpu_percent,'MEM%':process.memory_percent}
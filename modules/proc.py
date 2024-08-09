from psutil import process_iter, Process, cpu_count
from dataclasses import dataclass, field
from platform import platform
from datetime import datetime
from pandas import DataFrame
import tabulate


class Process_Info:
    pid : str
    name : str
    cpu_percent : float
    memory_percent : float
    dt: str

    def __init__(self, process: Process, cpu_count:int, dt: str) -> None:
        self.pid = process.info['pid']
        self.name = process.info['name']
        self.cpu_percent = process.info['cpu_percent']/cpu_count
        self.memory_percent = process.memory_percent()
        self.dt = dt

    def __repr__(self) -> str:
        return f"PID: {self.pid}, NAME: {self.name}, CPU%: {self.cpu_percent:.2f}, MEM%: {self.memory_percent:.2f}"

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass(frozen=False)
class Tasks:
    os_type : str = field(init=False)
    cpu_count : int = field(init=False)
    process_list : list[Process_Info] = field(init=False)
    top_process : DataFrame = field(init=False)

    def __post_init__(self):
        self.os_type = 'windows' if 'windows' in platform().lower() else 'linux'
        self.cpu_count = cpu_count() if self.os_type=='windows' else 1
        self.get_process_list()
        self.top_process = DataFrame({key:list() for key in self.process_list[0].to_dict().keys()})
        self.top_process.set_index(keys='pid',inplace=True)
        self.top_process = self.top_process.astype({
            'name':'str','cpu_percent':'float64',
            'memory_percent':'float64','dt':'str'
        })

    def get_process_list(self):
        self.process_list = list()
        dt = datetime.now()
        for process in process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            self.process_list.append(Process_Info(process=process,
                                                  cpu_count=self.cpu_count,
                                                  dt=dt.strftime('%Y-%m-%d %H:%M:%S')))
        if self.process_list[0].pid == 0: self.process_list.pop(0)

    def sort_process_list(self):
        self.process_list.sort(key=lambda process: process.cpu_percent)

    def filter_process_list(self, name:str = None, cpu_percent: float = None, memory_percent: float = None):
        self.sort_process_list()
        if name:
            self.process_list = list(filter(lambda process: process.name == name, self.process_list))
        if cpu_percent:
            self.process_list = list(filter(lambda process: process.cpu_percent >= cpu_percent , self.process_list))
        if memory_percent:
            self.process_list = list(filter(lambda process: process.memory_percent >= memory_percent, self.process_list))

        for process in self.process_list:
            process_is_in_top = process.pid in self.top_process.index
            last_top_cpu = self.top_process.at[process.pid,'cpu_percent'] if process_is_in_top else 0.0 
            last_top_mem = self.top_process.at[process.pid,'memory_percent'] if process_is_in_top else 0.0
            update_data : bool = False
            if cpu_percent and memory_percent:
                update_data = last_top_cpu < process.cpu_percent and last_top_mem < process.memory_percent
            elif cpu_percent:
                update_data = last_top_cpu < process.cpu_percent
            elif memory_percent:
                update_data = last_top_mem < process.memory_percent
            if update_data:
                for col_name in self.top_process.columns:
                    if col_name != 'pid':
                        self.top_process.at[process.pid, col_name] = process.__getattribute__(col_name)




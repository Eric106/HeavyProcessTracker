from psutil import process_iter, cpu_count, virtual_memory, cpu_percent, Process
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

    def to_list(self) -> list:
        return list(self.to_dict().values())

@dataclass(frozen=False)
class Tasks:
    os_type : str = field(init=False)
    cpu_count : int = field(init=False)
    cpu_usage : float = field(init=False)
    mem_usage : float = field(init=False)
    data_tags : list[str] = field(init=False)
    process_list : DataFrame = field(init=False)
    top_process : DataFrame = field(init=False)
    astype_map : dict = field(init=False)

    def __post_init__(self):
        self.data_tags = ['pid', 'name', 'cpu_percent', 'memory_info']
        self.col_types = {
            'pid':'int64','name':'str','cpu_percent':'float64',
            'memory_percent':'float64','dt':'datetime64[ms]'
        }
        self.os_type = 'windows' if 'windows' in platform().lower() else 'linux'
        self.cpu_count = cpu_count() if self.os_type=='windows' else 1
        self.cpu_usage = cpu_percent()
        self.mem_usage = virtual_memory().available * 100 / virtual_memory().total
        self.get_process_list()
        self.top_process = DataFrame({key:list() for key in self.col_types.keys()})
        self.top_process = self.top_process.astype(self.col_types)
        self.top_process.set_index(keys='pid',inplace=True)

    def get_process_list(self):
        self.cpu_usage = cpu_percent()
        self.mem_usage = virtual_memory().available * 100 / virtual_memory().total
        dt = datetime.now()
        self.process_list = DataFrame({key:list() for key in self.col_types.keys()})
        self.process_list = self.process_list.astype(self.col_types)
        self.process_list.set_index(keys='pid',inplace=True)
        for process in process_iter(self.data_tags):
            proc_info = Process_Info(process=process,
                                     cpu_count=self.cpu_count,
                                     dt=dt.strftime('%Y-%m-%d %H:%M:%S'))
            if proc_info.pid != 0:
                self.process_list.loc[proc_info.pid] = proc_info.to_list()[1:]    

    def sort_process_list(self):
        self.process_list.sort_values(by=['cpu_percent','memory_percent'],inplace=True)

    def filter_process_list(self, name:str = None, cpu_percent: float = None, memory_percent: float = None):
        self.sort_process_list()
        if name:
            self.process_list = self.process_list[self.process_list['name'] == name]
        if cpu_percent:
            self.process_list = self.process_list[self.process_list['cpu_percent'] >= cpu_percent]
        if memory_percent:
            self.process_list = self.process_list[self.process_list['memory_percent'] >= memory_percent]

        for pid, process in self.process_list.iterrows():
            process_is_in_top = pid in self.top_process.index
            last_top_cpu = self.top_process.at[pid,'cpu_percent'] if process_is_in_top else 0.0 
            last_top_mem = self.top_process.at[pid,'memory_percent'] if process_is_in_top else 0.0
            update_data : bool = False
            if cpu_percent and memory_percent:
                update_data = last_top_cpu < process['cpu_percent'] and last_top_mem < process['memory_percent']
            elif cpu_percent:
                update_data = last_top_cpu < process['cpu_percent']
            elif memory_percent:
                update_data = last_top_mem < process['memory_percent']
            if update_data:
                self.top_process.loc[pid] = [values for values in process.to_dict().values()]

        self.top_process.sort_values(by=['cpu_percent','memory_percent'],inplace=True)
        self.top_process.drop_duplicates(subset=['name'],keep='last', inplace=True)


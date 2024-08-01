from time import sleep
from os import system
from pprint import pprint
from argparse import ArgumentParser
from modules.proc import Tasks


def main():
    parser = ArgumentParser(description="Bad Process Tracker")
    parser.add_argument('-n',dest='name',type=str)
    parser.add_argument('-cpu',dest='cpu',type=float)
    parser.add_argument('-mem',dest='mem',type=float)
    parser.add_argument('-sleep',dest='sleep',type=int)
    args = parser.parse_args()
    if args.sleep == None:
        sleep_time = 3
    else:
        sleep_time = args.sleep
    start_scan = True
    tasks = Tasks()
    while start_scan:
        try:
            tasks.get_process_list()
            system('cls')
            tasks.filter_process_list(name=args.name,
                                    cpu_percent=args.cpu,
                                    memory_percent=args.mem)
            pprint(tasks.process_list)
            print('*'*50)
            print(f'Last process info: ')
            pprint(tasks.top_process_names)
        except KeyboardInterrupt:
            start_scan = False
        sleep(sleep_time)

if __name__ == "__main__":
    main()

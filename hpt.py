from time import sleep
from os import system
from pprint import pprint
from argparse import ArgumentParser
from platform import platform
from modules.proc import Tasks


def main():
    parser = ArgumentParser(description="Bad Process Tracker")
    parser.add_argument('-n',dest='name',type=str)
    parser.add_argument('-cpu',dest='cpu',type=float)
    parser.add_argument('-mem',dest='mem',type=float)
    parser.add_argument('-sleep',dest='sleep',type=int)
    parser.add_argument('-csv',dest='csv',type=str)
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
            if tasks.os_type == 'windows': 
                system('cls')
            else:
                system('clear')
            tasks.filter_process_list(name=args.name,
                                    cpu_percent=args.cpu,
                                    memory_percent=args.mem)
            print('='*50)
            print('Process list read: ')
            pprint(tasks.process_list)
            print('*'*50)
            print('*'*50)
            print(f'Last MAX process info: ')
            print(tasks.top_process_to_frame().to_markdown(index=False))
            sleep(sleep_time)
        except KeyboardInterrupt:
            start_scan = False
    if args.csv:
        tasks.top_process_to_frame().to_csv(args.csv, index=False)

if __name__ == "__main__":
    main()

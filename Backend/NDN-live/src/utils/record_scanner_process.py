import time
from status import *
from config import *

from multiprocessing import Process
from ndn.app import NDNApp
from ndn.encoding.name import *
from ndn.utils import timestamp
import glob
import os
import shutil
import re
import json
from collections import OrderedDict
import requests


class RecordScannerProcess(Process):
    def __init__(self, transferQueue=None, convertQueue=None):
        super().__init__()
        self.record_files = os.path.join(RECORD_SCAN_PATH, '**', '*')
        self.transferQueue = transferQueue
        self.convertQueue = convertQueue
        self.new_files = []
        self.cache_files = OrderedDict()
        assert self.transferQueue is not None and self.convertQueue is not None

    def run(self):
        while True:
            self.new_files = []
            if not self.schedule_record_scanning_path():
                time.sleep(RECORD_SCANNING_INTERVAL * 10)
            time.sleep(RECORD_SCANNING_INTERVAL)
            print('*' * 100)
            print(f"cache_files current size: {len(self.cache_files)}")
            cur_time = time.time()
            release_files = []
            for key in self.cache_files.keys():
                # 6 hours later， will clean up cache
                if self.cache_files[key] + 3600 * 6 < cur_time:
                    release_files.append(key)
            for f in release_files:
                self.cache_files.pop(f)


    def schedule_record_scanning_path(self):
        assert self.transferQueue is not None, "self.transferQueue is None"
        self.new_files = set(glob.glob(self.record_files)) - set(self.cache_files.keys())
        if not self.new_files:
            return False
        proc_count = 0
        
        for file in glob.glob(self.record_files):
            if file in self.cache_files:
                self.cache_files[file] = time.time()
        
        for directory in glob.glob(RECORD_SCAN_PATH + os.sep + '*'):
            if not os.listdir(directory):
                shutil.rmtree(directory, ignore_errors=True)
                print('delete dir: ' + directory)

        for file in self.new_files:
            # cache 大于1000就清理一些
            # if len(self.cache_files) > 50000:
            #     self.cache_files.popitem(0)
            if proc_count >= RECORD_TRANSFER_CONCURRENT_COUNT * 2:
                break
            path_1, filename = os.path.split(file)
            path_2, indexed = os.path.split(path_1)

            if file.endswith('0p.mp4'):
                continue

            if not os.path.exists(file):
                print(file + ' file not exists!')
                continue

            print('[schedule_reading_path] indexed: ' + indexed + ', new file: ' + filename)
            if (file.endswith('mp4') or file.endswith('flv')):
                self.cache_files[file] = time.time()
                proc_count += 1
                self.convertQueue.put({
                    'mp4path': file,
                    'target_save_dir': path_1,
                    'tmp_dir': os.sep + 'home' + os.sep + indexed
                })

            if file.endswith('m3u8'):
                self.cache_files[file] = time.time()
                proc_count += 1
                if not os.path.exists(path_1 + os.sep + 'master.m3u8'):
                    self.create_primary_m3u8(
                        m3u8_directory=path_1, m3u8_name=filename)
                self.transferQueue.put({
                    "file_path": file,
                    "prefix": PREFIX + '/record/' + indexed + '/' + filename,
                    "freshness_period": RECORD_FRESHNESS_PERIOD,
                    "version": int(VERSION),
                    "status": RECORD
                })

            if file.endswith('ts'):
                self.cache_files[file] = time.time()
                proc_count += 1
                self.transferQueue.put({
                    "file_path": file,
                    "prefix": PREFIX + '/record/' + indexed + '/' + filename,
                    "freshness_period": RECORD_FRESHNESS_PERIOD,
                    "version": int(VERSION),
                    "status": RECORD
                })
        return True

    def create_primary_m3u8(self, m3u8_directory='/tmp', m3u8_name='play-720p.m3u8'):
        file_name = m3u8_name.split('.')[0]
        file_name = re.sub('-.*', '', file_name)
        master_m3u8_str = PLAY_LIST_M3U8.format(file_name=file_name)

        with open(m3u8_directory + os.sep + 'master.m3u8', 'w') as file:
            file.write(master_m3u8_str)
        print('master_m3u8_str: ' + master_m3u8_str)


if __name__ == '__main__':
    # test
    proc = RecordScannerProcess()
    proc.start()
    proc.join()

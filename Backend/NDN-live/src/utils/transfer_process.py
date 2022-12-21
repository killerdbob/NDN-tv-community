import os
from status import *
from config import *
from multiprocessing import Process
from utils.oss_crud import NDNMinio
import time
from ndn.app import NDNApp
from ndn.encoding.name import *
from ndn.utils import timestamp
from utils.Block import Block

from status import *


class TransferProcess(Process):
    def __init__(self, segment_size=SEGMENT_SIZE, file_path='', prefix='', freshness_period=RECORD_FRESHNESS_PERIOD,
                 version=VERSION, status=RECORD,
                 bucket=OSS_BUCKET, queue=None):
        super().__init__()
        self.SEGMENT_SIZE = segment_size
        self.segment_cache = {}
        self.process_num = 10
        self.file_path = file_path
        self.prefix = prefix
        self.freshness_period = freshness_period
        self.version = version
        self.status = status
        self.miniodb_inst = NDNMinio(OSS_HOST + ":" + str(OSS_PORT),
                                     OSS_USER,
                                     OSS_PASSWORD)
        self.bucket = bucket
        self.queue = queue
        self.Block = None

    def run(self):
        self.Block = Block()
        assert self.queue is not None, "TransferProcess queue is none"
        while True:
            data = None
            if self.queue.empty():
                time.sleep(RECORD_SLEEP)
            if not self.queue.empty():
                data = self.queue.get()
            if data:
                self.file_path = data.get('file_path', '')
                self.prefix = data.get('prefix', '')
                self.freshness_period = data.get(
                    'freshness_period', RECORD_FRESHNESS_PERIOD_M3U8)
                self.version = data.get('version', VERSION)
                self.status = data.get('status', RECORD)
                assert self.file_path != '', "TransferProcess file_path is empty"
                assert self.prefix != '', "TransferProcess prefix is empty"
                if not os.path.exists(self.file_path):
                    continue
                try:
                    self.make_data_from_file_transfer_and_save()
                    os.remove(self.file_path)
                except Exception as e:
                    print(e)

    def make_data_from_file_transfer_and_save(self):
        if not self.file_path:
            print('no file provided')
            return
        print("[schedule_reading_path] " + self.prefix)
        data = None
        with open(self.file_path, 'rb') as f:
            data = f.read()
        path_1, file_name = os.path.split(self.file_path)
        path_2, indexed = os.path.split(path_1)
        seg_cnt = (len(data) + self.SEGMENT_SIZE - 1) // self.SEGMENT_SIZE
        print('#' * 50 + 'start' + '#' * 50)
        print("filename: " + self.file_path)
        print("seg_cnt: " + str(seg_cnt))
        print("file size: " + str(len(data)))
        print('#' * 50 + 'end' + '#' * 50)

        batches = {}
        for i in range(seg_cnt):
            meta_data = self.Block.make_data(prefix=self.prefix,
                                             metadata=data[i * self.SEGMENT_SIZE:(
                                                 i + 1) * self.SEGMENT_SIZE],
                                             freshness_period=self.freshness_period,
                                             current_block=i,
                                             final_block_id=seg_cnt - 1,
                                             status=self.status)
            batches[meta_data['segment_number']] = meta_data
        self.miniodb_inst.write_object(
            indexed + os.sep + file_name + '.ndn', batches)

from config import *
from status import *
from utils.transfer_process import TransferProcess
from utils.record_scanner_process import RecordScannerProcess
from utils.convert_process import ConvertProcess
from multiprocessing import Lock, Queue
from config import *


def run():
    for _ in range(RECORD_TRANSFER_CONCURRENT_COUNT):
        proc = TransferProcess(queue=transferQueue)
        # proc.daemon = True
        proc.start()
        all_proc.append(proc)

    for _ in range(RECORD_CONVERT_CONCURRENT_COUNT):
        proc = ConvertProcess(queue=convertQueue, queue_lock=convertLock)
        # proc.daemon = True
        proc.start()
        all_proc.append(proc)

    record_scanner_proc = RecordScannerProcess(transferQueue=transferQueue, convertQueue=convertQueue)
    record_scanner_proc.start()
    all_proc.append(record_scanner_proc)

    for proc in all_proc:
        proc.join()


if __name__ == '__main__':

    transferQueue = Queue(TRANSFER_QUEUE_SIZE)
    convertQueue = Queue(CONVERT_QUEUE_SIZE)
    convertLock = Lock()

    all_proc = []
    run()

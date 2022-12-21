from status import *
from config import *
from multiprocessing import Process

import time

from ndn.encoding.name import *
import os
import shutil


class ConvertProcess(Process):
    def __init__(self, queue=None, queue_lock=None):
        super().__init__()
        self.queue = queue
        self.lock = queue_lock

    def run(self):
        assert self.queue is not None and self.lock is not None
        while True:
            data = None
            if not self.queue.empty():
                self.lock.acquire()
                data = self.queue.get()
                self.lock.release()
            if self.queue.empty():
                time.sleep(RECORD_SLEEP)
            mp4path = ""
            target_save_dir = ""
            tmp_dir = ""
            if data:
                mp4path = data.get('mp4path', '')
                target_save_dir = data.get('target_save_dir', '')
                tmp_dir = data.get('tmp_dir', '')
                assert mp4path
                assert target_save_dir
                assert tmp_dir
            if not mp4path or not target_save_dir:
                continue
            self.process(mp4path, tmp_dir)
            shutil.copytree(tmp_dir, target_save_dir, dirs_exist_ok=True)
            shutil.rmtree(tmp_dir, ignore_errors=True)
            _, filename = os.path.split(mp4path)
            if not os.path.isdir(TRASH_PATH):
                os.mkdir(TRASH_PATH)
            try:
                if os.path.exists(TRASH_PATH + os.sep + filename):
                    os.remove(TRASH_PATH + os.sep + filename)
                shutil.move(mp4path, TRASH_PATH)
                shutil.rmtree(mp4path, ignore_errors=True)
            except Exception as e:
                print(e)

    def mp4_convert_ts(self, mp4path, savedir):
        """
        :param filepath: mp4文件绝对路径
        :param savedir: 转换后ts文件的保存目录
        :return:
        """
        sep = os.sep
        mp4name = mp4path.split(sep)[-1].split(".")[0]
        if not os.path.isdir(savedir):
            os.mkdir(savedir)
        savename = savedir + sep + mp4name
        print("保存目录：" + savename)

#     command = """ffmpeg -i {mp4path} -f segment -segment_time 4 -segment_format mpegts -segment_list {savename}.m3u8 -max_muxing_queue_size 10000 -c copy -c:v libx264 -preset superfast -x264opts keyint=50 -bsf:v h264_mp4toannexb -map 0 {savename}-%04d.ts
#       """.format(mp4path=mp4path, savename=savename)
        command="""ffmpeg -i {mp4path} -f hls -hls_time 4 -hls_init_time 0.3 -hls_list_size 0 -force_key_frames 0:00:00 -force_key_frames "expr:gte(t,n_forced*2)" {savename}.m3u8 -max_muxing_queue_size 10000 -c copy -c:v libx264 -preset ultrafast -x264opts keyint=50 -bsf:v h264_mp4toannexb -map 0
        """.format(mp4path=mp4path, savename=savename)
        print(command)
        resp = os.popen(command).read()
        print(resp)

    def mp4_scale(self, mp4path, scale, target_save_dir):
        """
        视频缩放
        :param mp4path: MP4视频绝对路径
        :param scale: 缩放尺寸
        :return:
        """
        sep = os.sep
        mp4name = mp4path.split(sep)[-1].split(".")[0]
        #savedir = os.path.dirname(mp4path)
        resolution = scale[0]  # 分辨率
        rate = scale[1]  # 码率
        mp4_out_path = "/tmp/" + mp4name + "-" + resolution + "p.mp4"
        print("mp4_out_path:" + mp4_out_path)
        command = """ffmpeg -i {mp4path}  -acodec aac -vcodec h264 -b:v {rate} {mp4_out_path}
        """.format(mp4path=mp4path, rate=rate, mp4_out_path=mp4_out_path)
        print(command)
        resp = os.popen(command).read()
        m3u8_save_dir = target_save_dir
        print("m3u8:" + m3u8_save_dir)
        self.mp4_convert_ts(mp4_out_path, m3u8_save_dir)
        os.remove(mp4_out_path)
        return resp

    def process(self, mp4path, target_save_dir):
        """
        使用多进程对视频缩放，将视频缩放为1080p，720p,480p,240p
        :param mp4path:
        :return:
        """
        for scale in RECORD_RESOLUTION.items():
            print(scale)
            self.mp4_scale(mp4path, scale, target_save_dir)

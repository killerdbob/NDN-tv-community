import io
from collections import OrderedDict
from logging import FATAL

import os
from minio import Minio
from minio.error import *
import marshal

from config import *


class NDNMinio(Minio):
    def __init__(self, host='127.0.0.1',
                 user=None,
                 password=None,
                 session_token=None,
                 secure=False,
                 region=None,
                 http_client=None,
                 credentials=None,
                 bucket=OSS_BUCKET):
        super().__init__(host, access_key=user,
                         secret_key=password,
                         session_token=session_token,
                         secure=secure,
                         region=region,
                         http_client=http_client,
                         credentials=credentials)
        self.segment_cache = OrderedDict()
        self.process_num = 10
        self.bucket = bucket
        self.create_bucket()

    """
    注：创建桶命名限制：小写字母，句点，连字符和数字是
    唯一允许使用的字符（使用大写字母、下划线等命名会报错），长度至少应为3个字符
    """

    def create_bucket(self):
        try:
            if self.bucket_exists(bucket_name=self.bucket):  # bucket_exists：检查桶是否存在
                print("该存储桶已经存在")
            else:
                self.make_bucket(self.bucket)
                print("存储桶创建成功")
        except Exception as err:
            print(err)

    def fast_get_segment(self, prefix='', version=VERSION, segment_no="0", is_freshness=False):
        # segment_cache = { "/sl/example": { 1: meta_data } }
        print("[fast_get_segment] segment: " + segment_no)
        cache_batches = {}
        res = None
        
        if not is_freshness:
            cache_batches = self.segment_cache.get(prefix, {})
        if cache_batches:
            res = cache_batches.get(segment_no, {})
            if res: return res

        path_1, file_name = os.path.split(prefix)
        path_2, index = os.path.split(path_1)
        print("oss key: " + index + os.sep + file_name)
        batches = self.read_object(index + os.sep + file_name)

        if not batches:
            return {}
        res = batches.get(segment_no, {})
        seg_keys = list(self.segment_cache.keys())

        self.segment_cache[prefix] = dict(batches)
        if len(seg_keys) > 500:
            self.segment_cache.popitem(last=False)
        return res

    def read_object(self, object_name):
        res = b''
        data = None
        try:
            data = self.get_object(self.bucket, object_name)
            for chunk in data.stream(32 * 1024):
                res += chunk
            print("[read_object] success read " + object_name)
            object_res = marshal.loads(res)
            return object_res
        except Exception as err:
            print("[read_object] fail " + object_name)
            print(err)
        finally:
            if data:
                data.close()
                data.release_conn()
        return {}

    def write_object(self, object_name, object_data=None):
        if object_data is None:
            object_data = {}
        marshaled_data = marshal.dumps(object_data)
        for _ in range(5):
            try:
                self.put_object(self.bucket, object_name, io.BytesIO(marshaled_data), len(marshaled_data))
                print("[write_object] success write " + object_name)
                return True
            except MinioException as err:
                print("[write_object] fail ")
                print(err)
        return False


if __name__ == '__main__':
    test = NDNMinio('192.168.236.93:9000', 'ndn', '123456@pcl')
    # test.write_object('hehe/test', {1: b'1'})
    a = test.read_object('weiwei1/weiwei-720p-0024.ts.ndn')

    with open('42.seg', 'wb') as f:
        f.write(a['42']['packet'])
        # data = TlvModel.parse(a['42']['packet'])
    print(len(a['42']['packet']))

## Configuration
```
How to config Prefix in src/config.py?
An example /sl/record/weiwei/weiwei.m3u8

First part: /sl, could be an NLSR prefix, which you registerd into testbed.

Second part：/record, if it is recording video then it is '/record'. If it is live video, such as rtmp, then it should be /live.

Third part：/weiwei, this is the video name 

Fourth part：/playlist.m3u8, it is primary m3u8, it will generate as default.
```

## Note
```
There are four parts：
1、sche_serve_live.py: slice video into segments and store into mongodb.
2、live_serve.py: serving segments.
3、sche_serve_record.py: slice video into segments and store into minio.
4、record_serve.py: serving segments.
```


```

prefix说明，由4部分组成，例子/sl/record/weiwei/weiwei.m3u8
第一部分: /sl 是config.py中PREFIX的第一部分前缀，用于配置nlsr网络环境中的路径。
第二部分：/record 如果是点播就为record，如果是直播则为live，这部分是由视频所在文件夹决定（LIVE_PATH、RECORD_PATH）
第三部分: /name 是播放文件的上一层目录。
第四部分：/playlist.m3u8 是总的播放文件总的m3u8，默认生成。

```

```

程序安装：
1、安装node、pm2、docker、docker-compose
2、安装python包pip install -r src/requirements.txt
3、配置文件src/config.py
4、配置文件src/conf/docker-compose.yml
5、配置文件conf/client.conf,使用远程注册prefix
6、复制服务器上的秘钥到conf中
7、启动，bash deploy.sh --build
8、启动，bash deploy.sh
9、关闭，bash undeploy.sh

```

```

四个主程序：
1、sche_serve_live.py: 提供直播视频切片并存入数据库的功能
2、live_serve.py: 提供直播视频服务的功能
3、sche_serve_record.py: 提供点播视频切片并存入数据库的功能
4、record_serve.py: 提供点播视频服务的功能

```

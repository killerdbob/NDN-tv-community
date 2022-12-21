# NDN视频直播系统部署

## 1. 后端部署

### 1.1 部署环境

须安装python 3.8以上版本和docker，docker-compose。docker-compose须支持3.1及以上版本的`docker-compose.yaml`文件格式。

须安装`nodejs`及`npm`。

### 1.2 部署过程

需要后端和NDN转发平面`nfd`运行在统一太服务器上面。

首先，安装程序运行所需的`python`库：

```shell
pip3 install -r NDN-live/src/requirements.txt
```

安装`pm2`：

```shell
npm install pm2 -g
```

运行`dploy.sh`脚本：

```shell
bash deploy.sh
```

部署完成。等待一段时间后，通过`pm2 ls `命令查看已经启动的进程，如下图表示部署成功：

![](./docs/img/screen-1.png)

运行`docker ps`查看运行的容器，如下图表示部署成功：

![](./docs/img/screen-2.png)

撤销部署则运行命令`bash undeploy.sh`即可。

### 1.3 远程部署

远程部署即视频直播系统与NDN转发平面nfd没有运行在同一台机器上：

```mermaid
graph LR
A[视频直播系统]
B(NDN转发节点)
A ---- B
```

#### 1.3.1 配置NFD

需要配置nfd以支持远程部署。打开需要连接的nfd转发节点上`/usr/local/etc/ndn/nfd.conf`文件（nfd其他安装方式请自行确定配置文件所在路径），在`rib`一节添加如下配置信息：

```
localhop_security
  {
    trust-anchor
    {
      type any
    }
  }
localhop_security
   {
     rule
     {
       id "rib register command"
       for interest
       filter
       {
         type name
         regex ^[<localhop><localhost>]<nfd><rib>[<register><unregister>]<>{1,3}$
       }
       checker
       {
         type customized
         sig-type ecdsa-sha256
         key-locator
         {
           type name
           regex ^<>*<KEY><>{1,3}$
         }
                }
     }
     rule
     {
       id "hierarchy"
       for data
       filter
       {
         type name
         regex ^<>*<KEY><>{3}$
       }
       checker
       {
         type customized
         sig-type ecdsa-sha256
         key-locator
         {
           type name
           hyper-relation
           {
             k-regex ^(<>*)<KEY><>{1,3}$
             k-expand \\1
             h-relation is-prefix-of
             p-regex ^(<>*)$
             p-expand \\1
           }
         }
       }
     }
     trust-anchor
     {
       type any
     }
   }
  prefix_announcement_validation
  {
    trust-anchor
    {
      type any
    }
  }
```

之后重启nfd即可：

```shell
nfd-start 2>&1 | tee /tmp/nfd.log -a
```

#### 1.3.2 连接到NDN转发节点，注册前缀

注册前缀最重要的步骤是生成密钥。可选的生成密钥的方法有：

**使用nfd转发平面密钥：**

将要连接的运行`nfd`的NDN转发节点上的`~/.ndn`文件夹下的`pib.db`文件和`ndnsec-key-file`文件夹拷贝到`NDN-live/conf`文件夹下即可。

**生成自签名密钥：**

首先安装`python-ndn`，要求安装的版本在3.0或以上：

```shell
pip3 install --upgrade python-ndn
```

之后通过`pyndnsec`程序生成自签名密钥。如果终端提示找不到`pyndnsec`，请检查`python-ndn`是否升级到了最新版本。

为`/sl`前缀生成密钥的步骤如下：

```shell
pyndnsec Init-Pib		# 初始化~/.ndn/pib.db文件
pyndnsec New-Item /sl	# 为/sl前缀生成密钥
```

运行以上命令后，生成的密钥保存在`~/.ndn/pib.db`文件中，私钥保存在`~/.ndn/ndnsec-key-file`文件夹下。将`pib.db`文件和`ndnsec-key-file`文件拷贝到`NDN-live/conf`文件夹下：

```shell
cp ~/.ndn/pib.db NDN-live/conf
cp -r ~/.ndn/ndnsec-key-file NDN-live/conf
```

**生成由其他证书签名的密钥：**

参考[颁发NDN证书](https://yoursunny.com/t/2016/ndncert/)。生成证书后将文件拷贝到`NDN-live/conf`文件夹下。

证书生成后需要设置将要连接的NDN转发节点连接信息。打开`NDN-live/conf/client.conf`文件，修改内容为：

```ini
transport=NDN节点连接信息，如tcp4://192.168.102.1
```

#### 1.3.3 修改物理卷

修改`docker-compose.yaml`文件中相关卷的挂载信息。打开`NDN-live/docker-compose.yaml`，修改`mongo`，`oss`和`srs`等服务中的挂载卷中物理主机文件夹的位置信息，将服务器上特定的文件夹挂在到容器上：

```yaml
version: '3.1'
services:
  mongo:
    ...
    volumes:
      - /data/home/zy/mongodb:/data/db	# 需要修改
	...
  oss:
	...
    volumes:
      - /data/home/zy/oss:/data	# 需要修改

  srs:
    ...
    volumes:
      - /data/home/zy/srs/data:/usr/local/srs/objs/nginx/html/live	# 需要修改
      - ./src/conf/hls.conf:/usr/local/srs/conf/hls.conf
  
  live_scanner:
    ...
    volumes:
      - /data/home/zy/srs:/home/srs	# 需要修改
      - ./conf:/root/.ndn

  record_scanner:
    ...
    volumes:
      - /data/home/zy/srs:/home/srs	# 需要修改
      - ./conf:/root/.ndn

  live_server:
    ...
    volumes:
      - /data/home/zy/srs:/home/srs	# 需要修改
      - ./conf:/root/.ndn

  record_server:
    ...
    volumes:
      - /data/home/zy/srs:/home/srs   # 需要修改
      - ./conf:/root/.ndn
```

需要注意的是要保证`srs`容器的`/usr/local/srs/objs/nginx/html/live`文件夹和`live_scanner`，`record_scanner`，`live_server`和`record_server`的文件夹映射到物理主机的同一个文件夹下面以便能相互访问。

#### 1.3.4 启动容器

之后进入`NDN-live`文件夹，运行如下命令部署容器：

```shell
bash deploy.sh --build
```

部署过程中会构建部分容器运行所需的镜像。如已经构建了镜像，不需要再次构建，则不加`--build`参数即可。

运行成功后通过`docker ps`查看运行的容器，如下图所示表示运行成功：

![](./docs/img/remote.png)

登录NFN转发节点，输入命令`nfdc route`，出现前缀`/sl/live`和`/sl/record`即表示前缀注册成功。

#### 1.3.5 撤销部署

使用如下命令撤销部署：

```shell
bash undeploy.sh --clear
```

这会清除已构建的镜像。想要不清楚镜像则运行：

```shell
bash undeploy.sh --stop-service
```

想要清除构建的镜像，运行：

```shell
bash undeploy.sh --delete-image
```

## 2. 前端部署

### 1. 部署环境：

安装有docker，docker-compose的服务器。

### 3. 部署过程

修改`NDNts-video/public/content.json`中的内容，添加/删除视频播放列表。

```json
[
    ...
    {
        "title": "测试直播-CDN-level-1",								// 标题
        "name": "http://192.168.12.1:8080/live/test/playlist.m3u8",		// 播放链接
        "fallback": "https://vimeo.com/channels/ndnvfaq/163047407",
        "date": "2014-09-24T00:00:00",
        "tags": ["VFAQ"]
    }
    ...
]
```

修改`docker-compose.yml`文件，自定义端口号：

```yaml
version: "2.4"
services:
  ndn_client_zy:
    build: .
    ports:
      - "7080:3333"		# 修改端口号
    privileged: true
    tty: true
```

之后通过`docker-compose -f docker-compose.yml up -d`启动容器，前端部署完成。

如果修改了`NDNts-video/public`文件夹下的文件，需要重新构建镜像：`docker-compose -f docker-compose.yml build --no-cache` 。


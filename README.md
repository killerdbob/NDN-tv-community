# NDNtv, an NDN live streaming
- We show a new way of live streaming, and it is under IP layer called Named Data Network, which is a fast and low burden for networking data sharing protocol.
We have an online web, at https://live.pcl.ac.cn. It will demonstrate both live and recorded videos. Feel free to share your videos.

## How to build your live streaming website quick?

### Follow these steps:

- **step 1**，install docker and docker-compose on your computer.
- **step 2**，just run commands `docker-compose up -d` in every subdirectory which contains docker-compose.yml, and everything will be set up for you, of course, you must config those config files.

### Configuration:
- The most difficult part must be the config file, and we provide a default one. You should provide your prefix to register into the global NDN testbed, or you could install NFD locally. 

## How to use？

- **step 1**，make a folder under /home/minio/data/ndn, for instance, '/home/minio/data/ndn/hw'. 
- **step 2**，put your video into folder. Then, the program will convert video into HLS.
- **step 3**，configure 'Frontend/NDNts-video/public/content.json', the video name should be 'ndn:/pcl/video/record/hw/master.m3u8'.
- you could configure as you like.

### ANNOUNCEMENT:
- The front end is mostly derived from `https://github.com/yoursunny/NDNts-video`.

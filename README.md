# not safe for work flask server
## Install docker on server with ubuntu 16.04
See here:
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

## pull caffe docker cpu image
```sudo docker build -t caffe:cpu https://raw.githubusercontent.com/BVLC/caffe/master/docker/cpu/Dockerfile```
## check
```sudo docker run caffe:cpu caffe --version```
## get shell script and flask script
```git clone https://github.com/gundamkeroro/nsfw_flaskAPI.git```
```cd nsfw_flaskAPI```
```chmod +x start.sh```
```cd ..```
## run docker container
```sudo docker run -it -p 9000:5000 -v $PWD/nsfw_flaskAPI:/workspace/nsfw_flaskAPI caffe:cpu /workspace/nsfw_flaskAPI/start.sh ```
## should see terminal shows:
```
...
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
 * Restarting nginx nginx                                                                                                                      [ OK ] 
[2017-12-19 07:46:52 +0000] [412] [INFO] Starting gunicorn 19.7.1
[2017-12-19 07:46:52 +0000] [412] [INFO] Listening at: http://127.0.0.1:4000 (412)
[2017-12-19 07:46:52 +0000] [412] [INFO] Using worker: sync
[2017-12-19 07:46:52 +0000] [417] [INFO] Booting worker with pid: 417
[2017-12-19 07:46:52 +0000] [420] [INFO] Booting worker with pid: 420
[2017-12-19 07:46:52 +0000] [425] [INFO] Booting worker with pid: 425
[2017-12-19 07:46:52 +0000] [430] [INFO] Booting worker with pid: 430
[2017-12-19 07:46:52 +0000] [431] [INFO] Booting worker with pid: 431
[2017-12-19 07:46:52 +0000] [436] [INFO] Booting worker with pid: 436
[2017-12-19 07:46:52 +0000] [440] [INFO] Booting worker with pid: 440
[2017-12-19 07:46:52 +0000] [444] [INFO] Booting worker with pid: 444
...

```
## Iutput:
```
curl -X POST http://52.80.157.30:9000/nsfw -F file=@path/to/image/image.png 
```
## Output:
```
{"probs": [0.84628240267435706, 0.23057639598846433, 0.075187955213629684]}
```
presents confidence interval of [normal, sexy, adult]



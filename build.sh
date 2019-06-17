#!/usr/bin/env bash
git pull
sudo docker build -t stalker .

for cid in `sudo docker ps -a | grep Exited | awk '{print $1}'`
do
    sudo docker rm $cid
done

for iid in `sudo docker images|grep "^<none>" | awk '{print $3}'`
do
    sudo docker rmi $iid
done

#!/usr/bin/env bash
for account in `ls|grep .bak`
do
    mv ${account} "`awk -F. '{print $1}' <<< ${account}`.json"
done
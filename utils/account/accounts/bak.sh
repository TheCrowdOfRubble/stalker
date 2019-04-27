#!/usr/bin/env bash
for account in `ls|grep .json`
do
    mv ${account} "${account}.bak"
done
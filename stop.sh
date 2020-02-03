#!/bin/bash

pid=`ps aux | grep product | grep -e grep | awk '{print $2}'`
kill $pid
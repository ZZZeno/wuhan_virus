#!/bin/bash

pid=`ps aux | grep product | grep -v grep | awk '{print $2}'`
kill $pid
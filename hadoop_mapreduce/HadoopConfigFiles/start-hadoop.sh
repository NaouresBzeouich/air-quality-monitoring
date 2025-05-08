#!/bin/bash

# Start SSH
service ssh start

# Format HDFS only if not formatted yet
if [ ! -d "/tmp/hadoop-root/dfs" ]; then
    $HADOOP_HOME/bin/hdfs namenode -format
fi

# Start Hadoop services
start-dfs.sh
start-yarn.sh

# Keep container running
bash

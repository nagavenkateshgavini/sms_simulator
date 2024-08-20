#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./scale_sender.sh <number_of_instances>"
  exit 1
fi

NUM_INSTANCES=$1
mkdir -p sender_logs
echo "Starting $NUM_INSTANCES sender instances..."
for (( i=1; i<=NUM_INSTANCES; i++ ))
do
  echo "Starting sender instance $i..."
  nohup python3 sms_simulator/sender.py > sender_logs/sender_instance_$i.log 2>&1 &
done

echo "Successfully started $NUM_INSTANCES sender instances."

#!/bin/bash
# This script is used to upload the firmware to the remote device
# Usage: ./remoteFWUpload.sh <remote device IP> <remote device USB device> <firmware file>
echo "Upload firmware $3 to remote device $1 using USB device $2"
echo "---"
echo "Please press any key if the target device is ready"
read -n 1
echo "---"
echo "Mounting the remote device"
uid=$(ssh $1 id -u)
gid=$(ssh $1 id -g)

ssh $1 "sudo mount -t vfat -o nofail,uid=$uid,gid=$gid,umask=007  /dev/$2 /mnt/key"
sleep 2
echo "Copying the firmware to the remote device"
echo "---"
scp $3 $1:/mnt/key
echo "Firmware uploaded successfully"
echo "Please press any key to continue"
read -n 1
echo "Unmounting the remote device"
ssh $1 "sudo umount /mnt/key"
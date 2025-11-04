# zmk-keyboards-lily58

# Upload via unix

1. put master into bootloader
2. use dmesg or fdisk-l to find device
3. execute sudo mount -t vfat -o  nofail,uid=1000,gid=1000,umask=007 /dev/sdd /mnt/greyclaw
4. scp firmware to target
5. execute sudo umount /mnt/greyclaw


#!/bin/bash

if [ -z "$1" ]
then
  echo 'You need to provide a connected device as argument #1! Available:'
  # shellcheck disable=SC2010
  ls /dev/ | grep -v '[0-9]' | grep -E 'sd|blk'
  exit 1
else
  DEV_IN=$1
fi

if [ -z "$2" ]
then
  PATH_OUT=$(pwd)
else
  PATH_OUT=$2
fi

SHRINK='shrink.sh'
IMG='ga.img'
IMG_COMPRESSED='ga.img.zip'

# shellcheck disable=SC2164
cd "$PATH_OUT"

echo ''
echo '### Creating image ###'
echo ''
sudo dd bs=4M if="/dev/$DEV_IN" of=$IMG

echo ''
echo '### Shrinking image ###'
echo ''
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh -O $SHRINK
chmod +x $SHRINK
sudo ./$SHRINK -vd $IMG

echo ''
echo '### Compressing image ###'
echo ''
sudo apt install p7zip-full
7z a -mm=Deflate -mfb=258 -mpass=15 -r $IMG_COMPRESSED $IMG
rm -f $IMG

echo ''
echo '### Finished ###'
echo ''
echo 'Got files:'
ls -l "$PATH_OUT"

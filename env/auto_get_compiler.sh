#! /bin/bash 
echo "obtain compilers now"
cp /etc/apt/sources.list /etc/apt/sources.list.bak

# get apt-key from ubuntu
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 40976EAF437D05B5
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32

echo  "deb http://dk.archive.ubuntu.com/ubuntu/ focal main universe"  >> /etc/apt/sources.list
echo  "deb http://dk.archive.ubuntu.com/ubuntu/ bionic main universe" >> /etc/apt/sources.list
echo  "deb http://dk.archive.ubuntu.com/ubuntu/ xenial main universe" >> /etc/apt/sources.list
echo  'deb http://dk.archive.ubuntu.com/ubuntu/ trusty main universe' >> /etc/apt/sources.list
echo  'deb http://archive.ubuntu.com/ubuntu/ jammy main universe' >> /etc/apt/sources.list

apt-get update
apt-get install clang-12 clang-14 gcc-4.4 gcc-4.9 gcc-7 gcc-12 -y 

# get gcc-4.1.2 binary from a repo
git clone https://github.com/Su1ren/gcc-4.1.2.git
ln -s /cisb_docker/CISB-dataset/gcc-4.1.2/bin/gcc-4.1 /usr/bin

# old gcc runtime
ln -s /usr/lib/x86_64-linux-gnu/crt1.o ./reproduction_material
ln -s /usr/lib/x86_64-linux-gnu/crti.o ./reproduction_material
ln -s /usr/lib/x86_64-linux-gnu/crtn.o ./reproduction_material
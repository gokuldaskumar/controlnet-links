first 


%cd ~/

!git clone https://github.com/gokuldaskumar/controlnet-links

second


paste this code


%cd ~/controlnet-links

!git pull 

!rm -rf ~/tmp/tmp && mkdir -p /tmp/controlnet

%run controlnet_downloader.py

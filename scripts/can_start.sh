sudo ip link set up BackDriveCan type can bitrate 500000
sudo ip link set BackDriveCan txqueuelen 10000

sudo ip link set up FrontDriveCan type can bitrate 500000
sudo ip link set FrontDriveCan txqueuelen 10000
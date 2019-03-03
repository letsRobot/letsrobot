#!/bin/bash

# Clear screen
printf "\ec"
echo -en "\ec"

echo

echo -e "\e[31m**************************************************"
echo -e "\e[31m* \e[39mYou are now about to install everything needed \e[31m*"
echo -e "\e[31m* \e[39mto get your robot connected to letsrobot.tv    \e[31m*"
echo -e "\e[31m* \e[39mBefore we can start, you need to get a robot,  \e[31m*"
echo -e "\e[31m* \e[39mand camera ID. You can get that by pressing    \e[31m*"
echo -e "\e[31m* \e[39mthe \"connect your robot\" button.             \e[31m*"
echo -e "\e[31m**************************************************"

echo

#echo -e "\e[33mPlease enter your Robot ID:\e[39m "
#read input_robot

#re='^[0-9]+$'
#if ! [[ $input_robot =~ $re ]] ; then
#   echo "Error: Robot ID is not a number" >&2; exit 1
#fi

echo

#echo -e "\e[33mPlease enter your Camera ID:\e[39m "
#read input_camera
#
#echo
#echo
#
#if ! [[ $input_camera =~ $re ]] ; then
#   echo "Error: Camera ID is not a number" >&2; exit 1
#fi

#echo -e "\e[33mThank you, sit back and relax, we'll see you on letsrobot.tv\e[39m"

# If start_robot exists, append letsrobot stuff to it otherwise overwrite the whole thing.
if [ -e /home/$USER/start_robot ] 
then
    cat >> /home/$USER/start_robot <<EOF
    
    cd /home/pi/letsrobot
    nohup scripts/repeat_start python letsrobot.py &> /dev/null &
EOF
else
    cat > /home/$USER/start_robot <<EOF
    #!/bin/bash
    # suggested use for this:
    # (1) Put in the id's for your robot, YOURROBOTID and YOURCAMERAID
    # (2) use sudo to create a crontab entry: @reboot /bin/bash /home/pi/start_robot

    cd /home/pi/letsrobot
    nohup scripts/repeat_start python letsrobot.py &> /dev/null &
EOF
fi

echo -e "\e[33mInstalling required software...\e[39m"

# Make sure the system is up to date
sudo apt-get -y update

# This stuff takes forever, therefore not a default, but enable it if you want
#sudo apt-get -y upgrade
#sudo apt-get -y dist-upgrade

# Install required libraries and tools
sudo apt-get install ffmpeg python-serial python-dev libgnutls28-dev espeak python-smbus python-pip libttspico-utils git

# Download letsrobot scripts
git clone https://github.com/letsrobot/letsrobot.git /home/$USER/letsrobot

# Install python requirements
sudo python -m pip install -r /home/$USER/letsrobot/requirements.txt

# Copy letsrobot.sample.conf to letsrobot.conf
cp /home/$USER/letsrobot/letsrobot.sample.conf /home/$USER/letsrobot/letsrobot.conf

echo -e "\e[33mIt is now time to configure the controller. Please go to https://github.com/letsRobot/letsrobot#configure-the-controller for more information.\[e39m"
sleep 3s

nano /home/$USER/letsrobot/letsrobot.conf

(crontab -l 2>/dev/null; echo "@reboot /home/$USER/start_robot") | crontab -

echo -e "\e[33mInstall is now complete. Please reboot your robot. See you on letsrobot.tv!\e[39m"

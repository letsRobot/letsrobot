#!/bin/bash
# Let's Robot installer script
# See LICENSE for copyright and license details
# When editing this file, it is advisable to enable word wrap, and set your line
# endings from CRLF to LF.
# Version 2.0

calc_wt_size() {
    WT_HEIGHT=17
    WT_WIDTH=$(tput cols)

    if [ -z "$WT_WIDTH" ] || [ "$WT_WIDTH" -lt 60 ]; then
        WT_WIDTH=78
    fi

    if [ "$WT_WIDTH" -gt 178 ]; then
        WT_WIDTH=118
    fi

    WT_MENU_HEIGHT=$(($WT_HEIGHT-7))
}

do_robot_owner() {
    ROBOT_OWNER=$(whiptail --inputbox "Please enter your letsrobot.tv username" 20 60 "YourLetsRobotUserName" 20 60 1 3>&1 1>&2 2>&3)
    if [ $? -eq 0 ]; then
        sed -i "/^\[robot]/,/^\[/{s/^owner[[:space:]]*=.*/owner=$ROBOT_OWNER/}" $CONF_FILE
    fi
}

do_robot_id() {
    ROBOT_ID=$(whiptail --inputbox "Please enter your robot ID." 20 60 "YourRobotID" 20 60 1 3>&1 1>&2 2>&3)
    if [ $? -eq 0 ]; then
        sed -i "/^\[robot]/,/^\[/{s/^robot_id[[:space:]]*=.*/robot_id=$ROBOT_ID/}" $CONF_FILE
    fi
}

do_camera_id() {
    CAMERA_ID=$(whiptail --inputbox "Please enter your camera ID." 20 60 "YourCameraID" 20 60 1 3>&1 1>&2 2>&3)
    if [ $? -eq 0 ]; then
        sed -i "/^\[robot]/,/^\[/{s/^camera_id[[:space:]]*=.*/camera_id=$CAMERA_ID/}" $CONF_FILE
    fi
}

do_robot_type() {
    ROBOT_TYPE=$(whiptail --radiolist "Choose a robot type" $WT_HEIGHT $WT_WIDTH $WT_MENU_HEIGHT \
        "serial_board" "Serial" OFF \
        "motor_hat" "Adafruit Motor Hat" OFF \
        "gopigo2" "GoPiGo2" OFF \
        "gopigo3" "GoPiGo3" OFF \
        "l298n" "L298N" OFF \
        "motozero" "Motozero" OFF \
        "pololu" "Pololu" OFF \
        "adafruit_pwm" "Adafruit PWM" OFF \
        "owi_arm" "OWI Arm" OFF \
        "none" "None" ON \
        3>&1 1>&2 2>&3)
    RET=$?
    if [ $RET -eq 1 ]; then
        return 0
    elif [ $RET -eq 0 ]; then
        sed -i "/^\[robot]/,/^\[/{s/^type[[:space:]]*=.*/type=$ROBOT_TYPE/}" $CONF_FILE
    fi
}

do_stream_key() {
    STREAM_KEY=$(whiptail --passwordbox "Please enter your stream key" 20 60 "hello" 20 60 1 3>&1 1>&2 2>&3)
    RET=$?
    if [ $RET -eq 1 ]; then
        return 0
    elif [ $RET -eq 0 ]; then
        sed -i "/^\[robot]/,/^\[/{s/^stream_key[[:space:]]*=.*/stream_key=$STREAM_KEY/}" $CONF_FILE
    fi
}

REPO_DIR="/home/$USER/letsrobot"
CONF_FILE="$REPO_DIR/letsrobot.conf"
whiptail --yesno "You are about to install everything needed to get your robot connected to letsrobot.tv. Before we can start, you need to get a robot ID and camera ID. You can get that by pressing the \"Connect your Robot\" button on the site.

Ready to start?" 20 60 1
if [ $? -eq 1 ]; then   # user pressed no
    
    exit 0
fi

sudo apt-get update
sudo apt-get upgrade --assume-yes
sudo apt-get install ffmpeg python-serial python-dev libgnutls28-dev espeak python-smbus python-pip git --assume-yes

git clone https://github.com/letsrobot/letsrobot.git $REPO_DIR
python -m pip install -r $REPO_DIR/requirements.txt
cp $REPO_DIR/letsrobot.sample.conf $CONF_FILE

do_robot_owner
do_robot_id
do_camera_id
do_robot_type
do_stream_key

cp $REPO_DIR/scripts/start_robot /home/$USER/start_robot
chmod +x /home/$USER/start_robot

(crontab -l 2>/dev/null; echo "@reboot /home/$USER/start_robot") | crontab -

whiptail --msgbox "Installation is now complete. Please reboot your robot. See you on LetsRobot.tv!"  20 60 1
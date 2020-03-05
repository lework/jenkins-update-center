#!/bin/env bash
# 
# lework
# Jenkins mirror update center speed test.


######################################################################################################
# environment configuration
######################################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;36m'
PLAIN='\033[0m'

image_name="library/centos"
image_tag="latest"

declare -A mirrors
mirrors=(
  [tencent]="https://mirrors.cloud.tencent.com/jenkins/"
  [huawei]="https://mirrors.huaweicloud.com/jenkins/"
  [tsinghua]="https://mirrors.tuna.tsinghua.edu.cn/jenkins/"
  [ustc]="https://mirrors.ustc.edu.cn/jenkins/"
  [bit]="http://mirror.bit.edu.cn/jenkins/"
)

file="updates/current/plugin-versions.json"

######################################################################################################
# function
######################################################################################################

speed_test() {
    local output=$(LANG=C wget --header="$3" -4O /dev/null -T300 "$1" 2>&1)
    local speed=$(printf '%s' "$output" | awk '/\/dev\/null/ {speed=$3 $4} END {gsub(/\(|\)/,"",speed); print speed}')
    local ipaddress=$(printf '%s' "$output" | awk -F'|' '/Connecting to .*\|([^\|]+)\|/ {print $2}'| tail -1)
    local time=$(printf '%s' "$output" | awk -F= '/100% / {print $2}')
    local size=$(printf '%s' "$output" | awk '/Length:/ {s=$3} END {gsub(/\(|\)/,"",s); print s}')
    printf "${YELLOW}%-14s${GREEN}%-20s${BLUE}%-14s${PLAIN}%-20s${RED}%-14s${PLAIN}\n" "$2" "${ipaddress}" "${size}" "${time}" "${speed}" 
}


######################################################################################################
# main 
######################################################################################################

if  [ ! -e '/usr/bin/wget' ]; then
    echo "Error: wget command not found. You must be install wget command at first."
    exit 1
fi


clear
echo -e "\n\nJenkins mirror update center speed test"

echo -e "\n[Mirror Site]"
for mirror in ${!mirrors[*]}; do
printf "${PLAIN}%-14s${GREEN}%-20s${PLAIN}\n" ${mirror} ":  ${mirrors[$mirror]}"
done

echo -e "\n[Test]"
echo -e "Test File        : ${YELLOW}${file}${PLAIN}\n"

printf "%-14s%-20s%-14s%-20s%-14s\n" "Site Name" "IPv4 address" "File Size" "Download Time" "Download Speed"
for mirror in ${!mirrors[*]}; do
  speed_test "${mirrors[$mirror]}${file}" ${mirror}
done

echo

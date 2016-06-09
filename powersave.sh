#!/bin/bash

function enable {
    echo ${2:-1} >$1
}

function disable {
    echo ${2:-0} >$1
}

echo 1500 >/proc/sys/vm/dirty_writeback_centisecs
ethtool -s eno1 wol d
ethtool -s wlp3s0 wol d

disable /proc/sys/kernel/nmi_watchdog

find /sys -name power_save | while read -r file; do
    enable $file
done

find /sys -name link_power_management_policy | while read -r file; do
    enable $file "min_power"
done

find /sys -path '*/power/control' | while read -r file; do
    content=$(cat "$file")
    if [[ $content != auto ]]; then
        enable $file "auto"
    fi
done

powertop

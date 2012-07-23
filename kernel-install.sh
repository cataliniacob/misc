#!/bin/bash

sudo make INSTALL_FW_PATH=/lib/firmware/update/ modules_install
sudo make INSTALL_FW_PATH=/lib/firmware/update/ install

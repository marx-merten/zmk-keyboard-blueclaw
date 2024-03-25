#
# Copyright (c) 2022 Darryl deHaan
# SPDX-License-Identifier: MIT
#

if(CONFIG_ZMK_DISPLAY)
  if(CONFIG_CUSTOM_WIDGET_BATTERY_STATUS)
  endif()
  if(CONFIG_CUSTOM_WIDGET_PERIPHERAL_STATUS)
  endif()
  if(CONFIG_CUSTOM_WIDGET_OUTPUT_STATUS)
    zephyr_library_sources(usb.c)
    zephyr_library_sources(bt.c)
  endif()
  if(CONFIG_CUSTOM_WIDGET_LAYER_STATUS)
    zephyr_library_sources(layers.c)
  endif()
  if(NOT CONFIG_ZMK_SPLIT_ROLE_CENTRAL)
  endif()
endif()
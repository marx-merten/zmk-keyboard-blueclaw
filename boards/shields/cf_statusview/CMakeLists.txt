if(CONFIG_ZMK_DISPLAY AND CONFIG_CF_VIEW_WIDGET_STATUS)
  zephyr_library_include_directories(${CMAKE_SOURCE_DIR}/include)
  zephyr_library_sources(custom_status_screen.c)
  zephyr_library_sources(widgets/util.c)

    # target_sources_ifdef(CONFIG_CUSTOM_WIDGET_BATTERY_STATUS app PRIVATE widgets/battery_status.c)
  target_sources_ifdef(CONFIG_CUSTOM_WIDGET_OUTPUT_STATUS app PRIVATE widgets/output_status.c)
  target_sources_ifdef(CONFIG_CUSTOM_WIDGET_LAYER_STATUS app PRIVATE widgets/layer_status.c)
  target_sources_ifdef(CONFIG_CUSTOM_WIDGET_SPLIT_STATUS app PRIVATE widgets/split_status.c)

  # target_sources_ifdef(CONFIG_CUSTOM_WIDGET_PERIPHERAL_STATUS app PRIVATE widgets/peripheral_status.c)

  add_subdirectory_ifdef(CONFIG_ZMK_DISPLAY_STATUS_SCREEN_CUSTOM widgets/icons)


  zephyr_library_sources(widgets/test.c)


endif()



# zephyr_library()


# zephyr_library_include_directories(${ZEPHYR_LVGL_MODULE_DIR})
# zephyr_library_include_directories(${ZEPHYR_BASE}/lib/gui/lvgl/)
# zephyr_library_sources(${ZEPHYR_BASE}/misc/empty_file.c)
# zephyr_library_include_directories(${CMAKE_SOURCE_DIR}/include)
# zephyr_library_include_directories(${ZEPHYR_BASE}/drivers)

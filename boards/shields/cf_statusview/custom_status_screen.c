/*
 *
 * Copyright (c) 2023 The ZMK Contributors
 * SPDX-License-Identifier: MIT
 *
 */



#include "widgets/layer_status.h"
#include "widgets/output_status.h"
#include "widgets/test.h"
#include "widgets/util.h"
#include "widgets/split_status.h"

#include <zephyr/logging/log.h>

#include "./custom_status_screen.h"




#include <zephyr/logging/log.h>
LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_LAYER_STATUS)
LV_IMG_DECLARE(layers);
#endif

#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_OUTPUT_STATUS)
LV_IMG_DECLARE(usb);
#endif

/*
 * Widget Threadsafe Holders
 */
#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_LAYER_STATUS)
static struct zmk_widget_layer_status layer_status_widget;
#endif
#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_OUTPUT_STATUS)
static struct zmk_widget_output_status output_status_widget;
#endif

#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_SPLIT_STATUS)
static struct zmk_widget_split_status split_status_widget;
#endif

lv_obj_t *zmk_display_status_screen() {

    lv_obj_t *screen;
    screen = lv_obj_create(NULL);


    // lv_obj_t * label2 = lv_label_create(screen);
    // lv_label_set_long_mode(label2, LV_LABEL_LONG_SCROLL);     /*Circular scroll*/
    // lv_obj_set_width(label2, 50);
    // lv_obj_set_style_text_font(label2,
    //                            &lv_font_montserrat_16, LV_PART_MAIN);
    // lv_label_set_text(label2, "scrolling text. ");
    // lv_obj_align(label2, LV_ALIGN_TOP_LEFT, 0, 0);


#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_LAYER_STATUS)
    lv_obj_t *LayersHeading;
    LayersHeading = lv_img_create(screen);
    lv_obj_align(LayersHeading, LV_ALIGN_BOTTOM_LEFT, -5, -3);
    lv_img_set_src(LayersHeading, &layers);

    zmk_widget_layer_status_init(&layer_status_widget, screen);
    lv_obj_set_style_text_font(zmk_widget_layer_status_obj(&layer_status_widget),
                               &lv_font_montserrat_16, LV_PART_MAIN);
    lv_obj_align(zmk_widget_layer_status_obj(&layer_status_widget), LV_ALIGN_BOTTOM_LEFT, 9, 0);
#endif

#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_OUTPUT_STATUS)
    // lv_obj_t *OutputHeading;
    // OutputHeading = lv_img_create(screen);
    // lv_obj_align(OutputHeading, LV_ALIGN_TOP_LEFT, 0,0);
    // lv_img_set_src(OutputHeading, &usb);
    zmk_widget_output_status_init(&output_status_widget, screen);
#endif

#if IS_ENABLED(CONFIG_CUSTOM_WIDGET_SPLIT_STATUS)
    zmk_widget_split_status_init(&split_status_widget, screen);
    lv_obj_align(zmk_widget_split_status_obj(&split_status_widget), LV_ALIGN_TOP_RIGHT , 0, 0);

#endif

    // // LV_DRAW_BUF_DEFINE(draw_buf, 50, 16, LV_COLOR_FORMAT_I1);
    // /*Create a canvas and initialize its palette*/
    // tstsandbox(screen);
    return screen;
}

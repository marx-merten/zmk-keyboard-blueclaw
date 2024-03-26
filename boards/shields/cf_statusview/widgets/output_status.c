#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);


#include <zmk/display.h>
#include <zmk/event_manager.h>
#include <zmk/events/ble_active_profile_changed.h>
#include <zmk/events/endpoint_changed.h>
#include <zmk/usb.h>
#include <zmk/ble.h>
#include <zmk/endpoints.h>


#include "output_status.h"

static sys_slist_t widgets = SYS_SLIST_STATIC_INIT(&widgets);

LV_IMG_DECLARE(usb);
LV_IMG_DECLARE(bt);

struct output_status_state {
    struct zmk_endpoint_instance selected_endpoint;
    bool active_profile_connected;
    bool active_profile_bonded;
};

static struct output_status_state get_state(const zmk_event_t *_eh) {
        LOG_DBG("XXX GET output status");

    return (struct output_status_state){.selected_endpoint = zmk_endpoints_selected(),
                                        .active_profile_connected =
                                            zmk_ble_active_profile_is_connected(),
                                        .active_profile_bonded = !zmk_ble_active_profile_is_open()};
    ;
}

static void set_status_symbol(lv_obj_t *icon,lv_obj_t *label, struct output_status_state state) {
    char text[30] = {};

    switch (state.selected_endpoint.transport) {
    case ZMK_TRANSPORT_USB:
        lv_img_set_src(icon, &usb);

        strcat(text,"");

        LOG_DBG("XXX USB");
        break;
    case ZMK_TRANSPORT_BLE:
        if (state.active_profile_bonded) {
            if (state.active_profile_connected) {
                lv_img_set_src(icon, &bt);
                snprintf(text, sizeof(text), "%i", state.selected_endpoint.ble.profile_index + 1);

                LOG_DBG("XXX connected BLUETOOTH %i ", state.selected_endpoint.ble.profile_index + 1);
            } else {
                lv_img_set_src(icon, &bt);
                snprintf(text, sizeof(text), "%i (W)", state.selected_endpoint.ble.profile_index + 1);
                LOG_DBG("XXX bonded BLUETOOTH %i ", state.selected_endpoint.ble.profile_index + 1);
            }
        } else {
                lv_img_set_src(icon, &bt);
                snprintf(text, sizeof(text), "%i (J)", state.selected_endpoint.ble.profile_index + 1);

                LOG_DBG("XXX unbonded BLUETOOTH %i ", state.selected_endpoint.ble.profile_index + 1);
        }
        break;
    }

    lv_label_set_text(label, text);

    // lv_label_set_text(label, text);
}

static void output_status_update_cb(struct output_status_state state) {
    struct zmk_widget_output_status *widget;
    SYS_SLIST_FOR_EACH_CONTAINER(&widgets, widget, node) { set_status_symbol(widget->obj,widget->label, state); }
}

ZMK_DISPLAY_WIDGET_LISTENER(widget_output_status, struct output_status_state,
                            output_status_update_cb, get_state)
ZMK_SUBSCRIPTION(widget_output_status, zmk_endpoint_changed);
// We don't get an endpoint changed event when the active profile connects/disconnects
// but there wasn't another endpoint to switch from/to, so update on BLE events too.
#if defined(CONFIG_ZMK_BLE)
ZMK_SUBSCRIPTION(widget_output_status, zmk_ble_active_profile_changed);
#endif


int zmk_widget_output_status_init(struct zmk_widget_output_status *widget, lv_obj_t *parent) {
    LOG_DBG("XXX INIT output status");

    widget->obj =lv_img_create(parent);
    lv_obj_align(widget->obj, LV_ALIGN_TOP_LEFT, 0,0);
    lv_img_set_src(widget->obj, &usb);

    widget->label = lv_label_create(parent);
    lv_obj_align(widget->label, LV_ALIGN_TOP_LEFT, 18,-2);

    lv_obj_set_style_text_font(widget->label,
                               &lv_font_montserrat_14, LV_PART_MAIN);

    lv_label_set_text(widget->label, "1");

    sys_slist_append(&widgets, &widget->node);

    widget_output_status_init();
    return 0;
}

lv_obj_t *zmk_widget_output_status_obj(struct zmk_widget_output_status *widget) {
    return widget->obj;
}

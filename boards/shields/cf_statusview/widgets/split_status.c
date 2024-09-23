
#include "split_status.h"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

#include <zmk/display.h>
#include <zmk/events/layer_state_changed.h>
#include <zmk/event_manager.h>
#include <zmk/endpoints.h>
#include <zmk/keymap.h>



#include <zmk/display.h>
#include <zmk/split/bluetooth/peripheral.h>
#include <zmk/events/split_peripheral_status_changed.h>
#include <zmk/events/battery_state_changed.h>



static struct split_status_state {
    int battery_level[CONFIG_ZMK_SPLIT_BLE_CENTRAL_PERIPHERALS];
    bool connected[CONFIG_ZMK_SPLIT_BLE_CENTRAL_PERIPHERALS];
} split_state;


static sys_slist_t widgets = SYS_SLIST_STATIC_INIT(&widgets);

void get_state_as_string(char *state) {
    char temp_state[100] = {0};
    sprintf(temp_state + strlen(temp_state), "[");

    for (int i = 0; i < CONFIG_ZMK_SPLIT_BLE_CENTRAL_PERIPHERALS; i++) {
        if (split_state.connected[i]) {
            sprintf(temp_state + strlen(temp_state), " %02d", split_state.battery_level[i]);
        } else {
            sprintf(temp_state + strlen(temp_state), " xx");
        }
    }
    sprintf(temp_state + strlen(temp_state), " ]");

    strncpy(state, temp_state, 100);
    state[99] = '\0'; // Ensure null-termination
}
static void set_split_status(lv_obj_t *label, struct split_status_state state) {
    char msg[100];
    get_state_as_string(msg);
    lv_label_set_text(label, msg);
}

static void split_status_update_cb(struct split_status_state state) {
    struct zmk_widget_split_status *widget;
    SYS_SLIST_FOR_EACH_CONTAINER(&widgets, widget, node) { set_split_status(widget->obj, state); }
}


static struct split_status_state split_status_get_state(const zmk_event_t *ev) {
    const char *name = ev->event->name;
    struct zmk_peripheral_battery_state_changed_event *battery_state = (struct zmk_peripheral_battery_state_changed_event *)ev;
    LOG_DBG("XXXXX %s --> %d :: %d  (%s)", name,battery_state->data.source,
                                             battery_state->data.state_of_charge,
                                             battery_state->data.state_of_charge>0 ? "connected" : "disconnected");
    if (battery_state->data.source < CONFIG_ZMK_SPLIT_BLE_CENTRAL_PERIPHERALS) {
        split_state.battery_level[battery_state->data.source] = battery_state->data.state_of_charge;
        split_state.connected[battery_state->data.source] = (battery_state->data.state_of_charge>0);
    }
    return split_state;
}

// Create the necessary infrastructure to listen for layer state changes and update the widget
// _cb is the callback function that will be called when the event is raised
// _get_state is the function that will be called to get the state of the widget
ZMK_DISPLAY_WIDGET_LISTENER(split_status, struct split_status_state, split_status_update_cb,
                            split_status_get_state)

ZMK_SUBSCRIPTION(split_status, zmk_peripheral_battery_state_changed);






int zmk_widget_split_status_init(struct zmk_widget_split_status *widget, lv_obj_t *parent) {

    // TODO change rendering to icon or bar style rendering
    widget->obj = lv_label_create(parent);
    lv_obj_set_style_text_font(widget->obj ,
                               &lv_font_montserrat_12, LV_PART_MAIN);
    // lv_obj_set_width(widget->obj, 50);

    sys_slist_append(&widgets, &widget->node);

    char msg[100];
    get_state_as_string(msg);
    lv_label_set_text(widget->obj, msg);

    LOG_DBG("split_state (%s) ", msg);

    split_status_init();
    return 0;
}


lv_obj_t *zmk_widget_split_status_obj(struct zmk_widget_split_status *widget) {
    return widget->obj;
}

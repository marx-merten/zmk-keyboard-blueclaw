
#include "test.h"

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


struct test_status_state {
    uint8_t index;
};


static void test_status_update_cb(struct test_status_state state) {
    // struct zmk_widget_layer_status *widget;
    // SYS_SLIST_FOR_EACH_CONTAINER(&widgets, widget, node) { set_layer_symbol(widget->obj, state); }
}


static struct test_status_state test_status_get_state(const zmk_event_t *ev) {
    const char *name = ev->event->name;
    struct zmk_peripheral_battery_state_changed_event *battery_state = (struct zmk_peripheral_battery_state_changed_event *)ev;
    LOG_DBG("XXXXX %s --> %d :: %d", name,battery_state->data.source, battery_state->data.state_of_charge);
    return (struct test_status_state){.index = 7};
}

// Create the necessary infrastructure to listen for layer state changes and update the widget
// _cb is the callback function that will be called when the event is raised
// _get_state is the function that will be called to get the state of the widget
ZMK_DISPLAY_WIDGET_LISTENER(test_status, struct test_status_state, test_status_update_cb,
                            test_status_get_state)

ZMK_SUBSCRIPTION(test_status, zmk_peripheral_battery_state_changed);


int tstsandbox( lv_obj_t *screen){

    LOG_DBG("tstsandbox");

    // Start the event listener
    test_status_init();
    return 0;

}
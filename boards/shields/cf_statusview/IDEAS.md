See Events

zmk-core/app/src/events


See also app/boards/arm/corneish_zen

To see all, search for ZMK_EVENT_IMPL in zmk-core


- [LVG URL](https://docs.zephyrproject.org/latest/samples/subsys/display/lvgl/README.html)
- [LVG API](https://docs.lvgl.io/master/API/core/lv_obj_pos.html#_CPPv416lv_obj_set_widthP8lv_obj_t7int32_t)



```
.. see general status management
static void set_layer_status(struct zmk_widget_status *widget, struct layer_status_state state) {
    widget->state.layer_index = state.index;
    widget->state.layer_label = state.label;

    draw_bottom(widget->obj, widget->cbuf3, &widget->state);
}

static void layer_status_update_cb(struct layer_status_state state) {
    struct zmk_widget_status *widget;
    SYS_SLIST_FOR_EACH_CONTAINER(&widgets, widget, node) { set_layer_status(widget, state); }
}

static struct layer_status_state layer_status_get_state(const zmk_event_t *eh) {
    uint8_t index = zmk_keymap_highest_layer_active();
    return (struct layer_status_state){.index = index, .label = zmk_keymap_layer_name(index)};
}

ZMK_DISPLAY_WIDGET_LISTENER(widget_layer_status, struct layer_status_state, layer_status_update_cb,
                            layer_status_get_state)

ZMK_SUBSCRIPTION(widget_layer_status, zmk_layer_state_changed);
```

This is from nive!view status.c
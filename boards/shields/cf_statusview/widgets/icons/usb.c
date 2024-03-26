#ifdef __has_include
    #if __has_include("lvgl.h")
        #ifndef LV_LVGL_H_INCLUDE_SIMPLE
            #define LV_LVGL_H_INCLUDE_SIMPLE
        #endif
    #endif
#endif

#if defined(LV_LVGL_H_INCLUDE_SIMPLE)
    #include "lvgl.h"
#else
    #include "lvgl/lvgl.h"
#endif


#ifndef LV_ATTRIBUTE_MEM_ALIGN
#define LV_ATTRIBUTE_MEM_ALIGN
#endif

#ifndef LV_ATTRIBUTE_IMG_USB
#define LV_ATTRIBUTE_IMG_USB
#endif

const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST LV_ATTRIBUTE_IMG_USB uint8_t usb_map[] = {
  0x00, 0x00, 0x00, 0x07, 	/*Color of index 0*/
  0x00, 0x00, 0x00, 0xc1, 	/*Color of index 1*/

  0x00, 0x38, 0x00,
  0x00, 0xf8, 0x00,
  0x01, 0xb8, 0x00,
  0x01, 0x00, 0x00,
  0xf3, 0x00, 0x40,
  0xff, 0x7f, 0xf0,
  0xff, 0xd5, 0xe0,
  0x70, 0xc0, 0x40,
  0x00, 0x40, 0x00,
  0x00, 0x6f, 0x00,
  0x00, 0x3f, 0x00,
  0x00, 0x0f, 0x00,
};

const lv_img_dsc_t usb = {
  .header.cf = LV_IMG_CF_INDEXED_1BIT,
  .header.always_zero = 0,
  .header.reserved = 0,
  .header.w = 20,
  .header.h = 12,
  .data_size = 44,
  .data = usb_map,
};

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

#ifndef LV_ATTRIBUTE_IMG_LAYERS
#define LV_ATTRIBUTE_IMG_LAYERS
#endif

const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST LV_ATTRIBUTE_IMG_LAYERS uint8_t layers_map[] = {
  0x00, 0x00, 0x00, 0x00, 	/*Color of index 0*/
  0x00, 0x00, 0x00, 0xdc, 	/*Color of index 1*/

  0xff, 0xe0,
  0xff, 0xe0,
  0x00, 0x00,
  0xff, 0xe0,
  0xff, 0xe0,
  0x00, 0x00,
  0xff, 0xe0,
  0xff, 0xe0,
  0x00, 0x00,
  0xff, 0xe0,
  0xff, 0xe0,
};

const lv_img_dsc_t layers = {
  .header.cf = LV_IMG_CF_INDEXED_1BIT,
  .header.always_zero = 0,
  .header.reserved = 0,
  .header.w = 11,
  .header.h = 11,
  .data_size = 30,
  .data = layers_map,
};

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

#ifndef LV_ATTRIBUTE_IMG_BT
#define LV_ATTRIBUTE_IMG_BT
#endif

const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST LV_ATTRIBUTE_IMG_BT uint8_t bt_map[] = {
  0x00, 0x00, 0x00, 0x1d, 	/*Color of index 0*/
  0x00, 0x00, 0x00, 0xec, 	/*Color of index 1*/

  0x08, 0x00, 
  0x0c, 0x00, 
  0x0f, 0x00, 
  0x89, 0x80, 
  0x4b, 0x00, 
  0x2e, 0x00, 
  0x1c, 0x00, 
  0x1c, 0x00, 
  0x2e, 0x00, 
  0x4b, 0x00, 
  0x89, 0x80, 
  0x0f, 0x00, 
  0x0c, 0x00, 
  0x08, 0x00, 
};

const lv_img_dsc_t bt = {
  .header.cf = LV_IMG_CF_INDEXED_1BIT,
  .header.always_zero = 0,
  .header.reserved = 0,
  .header.w = 9,
  .header.h = 14,
  .data_size = 36,
  .data = bt_map,
};

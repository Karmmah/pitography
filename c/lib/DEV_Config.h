
/***********************************************************************************************************************
			------------------------------------------------------------------------
			|\\\																///|
			|\\\					Hardware interface							///|
			------------------------------------------------------------------------
***********************************************************************************************************************/
#ifndef _DEV_CONFIG_H_
#define _DEV_CONFIG_H_

#include <stdint.h>
#include "Debug.h"

#ifdef USE_BCM2835_LIB
    #include <bcm2835.h>
#elif USE_WIRINGPI_LIB
    #include <wiringPi.h>
    #include <wiringPiSPI.h>
#elif USE_DEV_LIB
    #include "sysfs_gpio.h"
    #include "dev_hardware_SPI.h"
#endif
#include <unistd.h>


/**
 * data
**/
#define UBYTE   uint8_t
#define UWORD   uint16_t
#define UDOUBLE uint32_t


//GPIO config
#define LCD_CS   8
#define LCD_RST  27
#define LCD_DC   25
#define LCD_BL   24

//SPI
#define SPI_MOSI_0		DEV_Digital_Write(SPI_MOSI,0)
#define SPI_MOSI_1		DEV_Digital_Write(SPI_MOSI,1)

#define is_SPI_MISO		DEV_Digital_Read(SPI_MISO)

#define SPI_SCK_0		DEV_Digital_Write(SPI_SCK,0)
#define SPI_SCK_1		DEV_Digital_Write(SPI_SCK,1)

//LCD
#define LCD_CS_0		DEV_Digital_Write(LCD_CS,0)
#define LCD_CS_1		DEV_Digital_Write(LCD_CS,1)

#define LCD_RST_0		DEV_Digital_Write(LCD_RST,0)
#define LCD_RST_1		DEV_Digital_Write(LCD_RST,1)

#define LCD_DC_0		DEV_Digital_Write(LCD_DC,0)
#define LCD_DC_1		DEV_Digital_Write(LCD_DC,1)

#define LCD_BL_0		DEV_Digital_Write(LCD_BL,0)
#define LCD_BL_1		DEV_Digital_Write(LCD_BL,1)

//KEY
#define KEY_UP_PIN      6
#define KEY_DOWN_PIN    19
#define KEY_LEFT_PIN    5
#define KEY_RIGHT_PIN   26
#define KEY_PRESS_PIN   13
#define KEY1_PIN        21
#define KEY2_PIN        20
#define KEY3_PIN        16

#define GET_KEY_UP       DEV_Digital_Read(KEY_UP_PIN)
#define GET_KEY_DOWN     DEV_Digital_Read(KEY_DOWN_PIN)
#define GET_KEY_LEFT     DEV_Digital_Read(KEY_LEFT_PIN)
#define GET_KEY_RIGHT    DEV_Digital_Read(KEY_RIGHT_PIN)
#define GET_KEY_PRESS    DEV_Digital_Read(KEY_PRESS_PIN)
#define GET_KEY1         DEV_Digital_Read(KEY1_PIN)
#define GET_KEY2         DEV_Digital_Read(KEY2_PIN)
#define GET_KEY3         DEV_Digital_Read(KEY3_PIN)
/*------------------------------------------------------------------------------------------------------*/
uint8_t DEV_ModuleInit(void);
void DEV_ModuleExit(void);

void DEV_GPIO_Mode(UWORD Pin, UWORD Mode);
void DEV_Digital_Write(UWORD Pin, UBYTE Value);
UBYTE DEV_Digital_Read(UWORD Pin);

void DEV_SPI_WriteByte(uint8_t value);
void DEV_Delay_ms(uint32_t xms);

#endif

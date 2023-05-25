#define USE_BCM2835_LIB
//#define USE_WIRINGPI_LIB
//#define USE_DEV_LIB

#include <stdio.h>
#include <stdlib.h> //exit()
//#include <bcm2835.h>
//#include <wiringPi.h>
//#include "/home/pi/pitography/c/lib/dev_hardware_SPI.c"
//#include "/home/pi/pitography/c/lib/sysfs_gpio.c"

#include "/home/pi/pitography/c/lib/DEV_Config.c"
#include "/home/pi/pitography/c/lib/LCD_Driver.c"
//#include "/home/pi/pitography/c/lib/LCD_GUI.c"

//#include "/home/pi/pitography/c/res/Fonts/fonts.h"
//#include "/home/pi/pitography/c/res/Fonts/font8.c"
//#include "/home/pi/pitography/c/res/Fonts/font12.c"
//#include "/home/pi/pitography/c/res/Fonts/font16.c"
//#include "/home/pi/pitography/c/res/Fonts/font24.c"


#define GUI_BACKGROUND		WHITE   //Default background color
#define FONT_BACKGROUND		WHITE   //Default font background color
#define FONT_FOREGROUND	    GRED    //Default font foreground color

#define WHITE          0xFFFF
#define BLACK          0x0000
#define BLUE           0x001F
#define BRED           0XF81F
#define GRED 		   0XFFE0
#define GBLUE		   0X07FF
#define RED            0xF800
#define MAGENTA        0xF81F
#define GREEN          0x07E0
#define CYAN           0x7FFF
#define YELLOW         0xFFE0
#define BROWN 		   0XBC40
#define BRRED 		   0XFC07
#define GRAY  		   0X8430



int main()
{
	printf("Hello World\n");

	printf("Module Init\n");
	if(DEV_ModuleInit())
	{
		exit(0);
	}

	printf("LCD Init\n");
	LCD_SCAN_DIR LCD_ScanDir = SCAN_DIR_DFT;
	LCD_Init(LCD_ScanDir);
	printf("LCD w:%d h:%d\n", LCD_WIDTH, LCD_HEIGHT);

//	printf("LCD show test image\n");
//	GUI_Show();
//	DEV_Delay_ms(1000);

	printf("LCD draw custom interface\n");
	LCD_Clear(BLACK);
//	startup_screen_draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
	LCD_SetArealColor(50,50,LCD_WIDTH-50,LCD_HEIGHT-50,GREEN);
	sleep(1);

	printf("LCD draw custom rectangle\n");
	LCD_SetCursor(0,0);
//	LCD_SetColor(GREEN,LCD_WIDTH,LCD_HEIGHT);
//	for(int i = 0; i < 30; i++)
//	{
//		for(int j = 0; j < LCD_WIDTH; j++)
//		{
//			LCD_SetPointlColor(j,i+80,GREEN);
//			LCD_SetCursor(0,80);
//			LCD_SetColor(GREEN,LCD_WIDTH,HEIGHT);
//			LCD_SetCursor(j,i*LCD_WIDTH);
//			LCD_SetColor(GREEN,1,1);
//		}
//	}
//	GUI_DrawRectangle(0,0,128,128, BLUE, DRAW_FULL, DOT_PIXEL_DFT);
	for(int i = 0; i < 100; i++)
	{
		int color;
		if(i%2 == 1){ color = GREEN; }else{ color = BLUE; }
		LCD_SetArealColor(0,0,128,128,color);
//		sleep(1);
	}

	printf("Goodbye World\n");
	DEV_ModuleExit();

	return 0;
}

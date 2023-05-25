#define USE_BCM2835_LIB

#include <stdio.h>
#include <stdlib.h> //exit()
//#include <bcm2835.h>

#include "/home/pi/pitography/c/lib/DEV_Config.c"
#include "/home/pi/pitography/c/lib/LCD_Driver.c"
#include "/home/pi/pitography/c/lib/LCD_GUI.c"

#include "/home/pi/pitography/c/res/Fonts/fonts.h"
#include "/home/pi/pitography/c/res/Fonts/font8.c"
#include "/home/pi/pitography/c/res/Fonts/font12.c"
#include "/home/pi/pitography/c/res/Fonts/font16.c"
#include "/home/pi/pitography/c/res/Fonts/font24.c"

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
//	LCD_Clear(GUI_BACKGROUND);
	LCD_Clear(GBLUE);
	sleep(1);
//	startup_screen_draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
//	GUI_DrawRectangle(0,40, sLCD_DIS.LCD_Dis_Column, 40, RED, LINE_SOLID, DOT_PIXEL_2X2);
//	GUI_DrawRectangle(0,40, LCD_WIDTH, 70, RED, LINE_SOLID, DOT_PIXEL_2X2);
//	GUI_DrawRectangle(0,40, LCD_WIDTH, 70, RED, LINE_SOLID, DOT_PIXEL_1X1);
//	GUI_DrawRectangle(1,40, LCD_WIDTH, 70, RED, LINE_SOLID, DOT_PIXEL_DFT);
	GUI_DrawRectangle(1,40, LCD_WIDTH, 70, RED, DRAW_FULL, DOT_PIXEL_DFT);
	GUI_DrawCircle( 60,80,40, YELLOW, DRAW_FULL, DOT_PIXEL_DFT);

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
	GUI_DrawRectangle(0,0, 128, 128, BLUE, DRAW_FULL, DOT_PIXEL_DFT);
	LCD_SetArealColor(0,0,128,128,GREEN);

	printf("Goodbye World\n");
	DEV_ModuleExit();

	return 0;
}

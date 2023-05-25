#include "LCD_GUI.h"
#include <stdio.h>

extern LCD_DIS sLCD_DIS;

void GUI_Swop(POINT Point1, POINT Point2)
{
    POINT Temp;
    Temp = Point1;
    Point1 = Point2;
    Point2 = Temp;
}

/********************************************************************************
function:	Draw Point(Xpoint, Ypoint) Fill the color
parameter:
			Xpoint		:   The x coordinate of the point
			Ypoint		:   The y coordinate of the point
			Color		:   Set color
			Dot_Pixel	:	point size
********************************************************************************/
void GUI_DrawPoint(POINT Xpoint, POINT Ypoint, COLOR Color,
                   DOT_PIXEL Dot_Pixel, DOT_STYLE DOT_STYLE)
{
    if(Xpoint > sLCD_DIS.LCD_Dis_Column || Ypoint > sLCD_DIS.LCD_Dis_Page) {
        return;
    }

    uint16_t XDir_Num ,YDir_Num;
    if(DOT_STYLE == DOT_STYLE_DFT) {
        for(XDir_Num = 0; XDir_Num < 2 * Dot_Pixel - 1; XDir_Num++) {
            for(YDir_Num = 0; YDir_Num < 2 * Dot_Pixel - 1; YDir_Num++) {
                LCD_SetPointlColor(Xpoint + XDir_Num - Dot_Pixel, Ypoint + YDir_Num - Dot_Pixel, Color);
            }
        }
    } else {
        for(XDir_Num = 0; XDir_Num <  Dot_Pixel; XDir_Num++) {
            for(YDir_Num = 0; YDir_Num <  Dot_Pixel; YDir_Num++) {
                LCD_SetPointlColor(Xpoint + XDir_Num - 1 , Ypoint + YDir_Num -1 , Color);
            }
        }
    }
}

/********************************************************************************
function:	Draw a line of arbitrary slope
parameter:
			Xstart ：Starting x point coordinates
			Ystart ：Starting x point coordinates
			Xend   ：End point x coordinate
			Yend   ：End point y coordinate
			Color  ：The color of the line segment
********************************************************************************/
void GUI_DrawLine(POINT Xstart, POINT Ystart, POINT Xend, POINT Yend,
                  COLOR Color, LINE_STYLE Line_Style, DOT_PIXEL Dot_Pixel)
{

    if(Xstart > sLCD_DIS.LCD_Dis_Column || Ystart > sLCD_DIS.LCD_Dis_Page ||
       Xend > sLCD_DIS.LCD_Dis_Column || Yend > sLCD_DIS.LCD_Dis_Page) {
        return;
    }

    if(Xstart > Xend)
        GUI_Swop(Xstart,Xend);
    if(Ystart > Yend)
        GUI_Swop(Ystart,Yend);

    POINT Xpoint = Xstart;
    POINT Ypoint = Ystart;
    int32_t dx =(int32_t)Xend -(int32_t)Xstart >= 0 ? Xend - Xstart : Xstart - Xend;
    int32_t dy =(int32_t)Yend -(int32_t)Ystart <= 0 ? Yend - Ystart : Ystart - Yend;

    // Increment direction, 1 is positive, -1 is counter;
    int32_t XAddway = Xstart < Xend ? 1 : -1;
    int32_t YAddway = Ystart < Yend ? 1 : -1;

    //Cumulative error
    int32_t Esp = dx + dy;
    int8_t Line_Style_Temp = 0;

    for(;;) {
        Line_Style_Temp++;
        //Painted dotted line, 2 point is really virtual
        if(Line_Style == LINE_DOTTED && Line_Style_Temp %3 == 0) {
            //printf("LINE_DOTTED\r\n");
            GUI_DrawPoint(Xpoint, Ypoint, GUI_BACKGROUND, Dot_Pixel, DOT_STYLE_DFT);
            Line_Style_Temp = 0;
        } else {
            GUI_DrawPoint(Xpoint, Ypoint, Color, Dot_Pixel, DOT_STYLE_DFT);
        }
        if(2 * Esp >= dy) {
            if(Xpoint == Xend) break;
            Esp += dy;
            Xpoint += XAddway;
        }
        if(2 * Esp <= dx) {
            if(Ypoint == Yend) break;
            Esp += dx;
            Ypoint += YAddway;
        }
    }
}

/********************************************************************************
function:	Draw a rectangle
parameter:
			Xstart ：Rectangular  Starting x point coordinates
			Ystart ：Rectangular  Starting x point coordinates
			Xend   ：Rectangular  End point x coordinate
			Yend   ：Rectangular  End point y coordinate
			Color  ：The color of the Rectangular segment
			Filled : Whether it is filled--- 1 solid 0：empty
********************************************************************************/
void GUI_DrawRectangle(POINT Xstart, POINT Ystart, POINT Xend, POINT Yend,
                       COLOR Color, DRAW_FILL Filled, DOT_PIXEL Dot_Pixel )
{
    if(Xstart > sLCD_DIS.LCD_Dis_Column || Ystart > sLCD_DIS.LCD_Dis_Page ||
       Xend > sLCD_DIS.LCD_Dis_Column || Yend > sLCD_DIS.LCD_Dis_Page) {
        return;
    }
	// printf("sLCD_DIS.LCD_Dis_Column = %d\r\n",sLCD_DIS.LCD_Dis_Column);
	// printf("sLCD_DIS.LCD_Dis_Page = %d\r\n",sLCD_DIS.LCD_Dis_Page);
    if(Xstart > Xend)
        GUI_Swop(Xstart,Xend);
    if(Ystart > Yend)
        GUI_Swop(Ystart,Yend);

    POINT Ypoint;
    if(Filled ) {
        for(Ypoint = Ystart; Ypoint < Yend; Ypoint++) {
            GUI_DrawLine(Xstart, Ypoint, Xend, Ypoint, Color , LINE_SOLID, Dot_Pixel);
        }
    } else {
        GUI_DrawLine(Xstart, Ystart, Xend, Ystart, Color , LINE_SOLID, Dot_Pixel);
        GUI_DrawLine(Xstart, Ystart, Xstart, Yend, Color , LINE_SOLID, Dot_Pixel);
        GUI_DrawLine(Xend, Yend, Xend, Ystart, Color , LINE_SOLID, Dot_Pixel);
        GUI_DrawLine(Xend, Yend, Xstart, Yend, Color , LINE_SOLID, Dot_Pixel);
    }
}

/********************************************************************************
function:	Use the 8-point method to draw a circle of the
				specified size at the specified position.
parameter:
			X_Center ：Center X coordinate
			Y_Center ：Center Y coordinate
			Radius   ：circle Radius
			Color  ：The color of the ：circle segment
			Filled : Whether it is filled: 1 filling 0：Do not
********************************************************************************/
void GUI_DrawCircle(POINT X_Center, POINT Y_Center, LENGTH Radius,
                    COLOR Color, DRAW_FILL  Draw_Fill , DOT_PIXEL Dot_Pixel)
{
    if(X_Center > sLCD_DIS.LCD_Dis_Column || Y_Center >= sLCD_DIS.LCD_Dis_Page) {
        return;
    }

    //Draw a circle from(0, R) as a starting point
    int16_t XCurrent, YCurrent;
    XCurrent = 0;
    YCurrent = Radius;

    //Cumulative error,judge the next point of the logo
    int16_t Esp = 3 -(Radius << 1 );

    int16_t sCountY;
    if(Draw_Fill == DRAW_FULL) {
        while(XCurrent <= YCurrent ) { //Realistic circles
            for(sCountY = XCurrent; sCountY <= YCurrent; sCountY ++ ) {
                GUI_DrawPoint(X_Center + XCurrent, Y_Center + sCountY, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );             //1
                GUI_DrawPoint(X_Center - XCurrent, Y_Center + sCountY, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );             //2
                GUI_DrawPoint(X_Center - sCountY, Y_Center + XCurrent, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );             //3
                GUI_DrawPoint(X_Center - sCountY, Y_Center - XCurrent, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );             //4
                GUI_DrawPoint(X_Center - XCurrent, Y_Center - sCountY, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );             //5
                GUI_DrawPoint(X_Center + XCurrent, Y_Center - sCountY, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );             //6
                GUI_DrawPoint(X_Center + sCountY, Y_Center - XCurrent, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );             //7
                GUI_DrawPoint(X_Center + sCountY, Y_Center + XCurrent, Color, DOT_PIXEL_DFT, DOT_STYLE_DFT );
            }
            if(Esp < 0 )
                Esp += 4 * XCurrent + 6;
            else {
                Esp += 10 + 4 *(XCurrent - YCurrent );
                YCurrent --;
            }
            XCurrent ++;
        }
    } else { //Draw a hollow circle
        while(XCurrent <= YCurrent ) {
            GUI_DrawPoint(X_Center + XCurrent, Y_Center + YCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //1
            GUI_DrawPoint(X_Center - XCurrent, Y_Center + YCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //2
            GUI_DrawPoint(X_Center - YCurrent, Y_Center + XCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //3
            GUI_DrawPoint(X_Center - YCurrent, Y_Center - XCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //4
            GUI_DrawPoint(X_Center - XCurrent, Y_Center - YCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //5
            GUI_DrawPoint(X_Center + XCurrent, Y_Center - YCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //6
            GUI_DrawPoint(X_Center + YCurrent, Y_Center - XCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //7
            GUI_DrawPoint(X_Center + YCurrent, Y_Center + XCurrent, Color, Dot_Pixel, DOT_STYLE_DFT );             //0

            if(Esp < 0 )
                Esp += 4 * XCurrent + 6;
            else {
                Esp += 10 + 4 *(XCurrent - YCurrent );
                YCurrent --;
            }
            XCurrent ++;
        }
    }
}

/********************************************************************************
function:	Show English characters
parameter:
			Xpoint ：X coordinate
			Ypoint ：Y coordinate
			Acsii_Char   ：To display the English characters
			Font  ：A structure pointer that displays a character size
			Color_Background : Select the background color of the English character
			Color_Foreground : Select the foreground color of the English character
********************************************************************************/
void GUI_DisChar(POINT Xpoint, POINT Ypoint, const char Acsii_Char,
                 sFONT* Font, COLOR Color_Background, COLOR Color_Foreground)
{
    POINT Page, Column;

    if(Xpoint >= sLCD_DIS.LCD_Dis_Column || Ypoint >= sLCD_DIS.LCD_Dis_Page) {
        return;
    }

    uint32_t Char_Offset =(Acsii_Char - ' ') * Font->Height *(Font->Width / 8 +(Font->Width % 8 ? 1 : 0));
    const unsigned char *ptr = &Font->table[Char_Offset];

    for(Page = 0; Page < Font->Height; Page ++ ) {
        for(Column = 0; Column < Font->Width; Column ++ ) {

            //To determine whether the font background color and screen background color is consistent
            if(FONT_BACKGROUND == Color_Background) { //this process is to speed up the scan
                if(*ptr &(0x80 >>(Column % 8)))
                    GUI_DrawPoint(Xpoint + Column, Ypoint + Page, Color_Foreground, DOT_PIXEL_DFT, DOT_STYLE_DFT);
            } else {
                if(*ptr &(0x80 >>(Column % 8))) {
                    GUI_DrawPoint(Xpoint + Column, Ypoint + Page, Color_Foreground, DOT_PIXEL_DFT, DOT_STYLE_DFT);
                } else {
                    GUI_DrawPoint(Xpoint + Column, Ypoint + Page, Color_Background, DOT_PIXEL_DFT, DOT_STYLE_DFT);
                }
            }
            //One pixel is 8 bits
            if(Column % 8 == 7)
                ptr++;
        }/* Write a line */
        if(Font->Width % 8 != 0)
            ptr++;
    }/* Write all */
}

/********************************************************************************
function:	Display the string
parameter:
			Xstart    ：X coordinate
			Ystart    ：Y coordinate
			pString   ：The first address of the English string to be displayed
			Font      ：A structure pointer that displays a character size
			Color_Background : Select the background color of the English character
			Color_Foreground : Select the foreground color of the English character
********************************************************************************/
void GUI_DisString_EN(POINT Xstart, POINT Ystart, const char * pString,
                      sFONT* Font,COLOR Color_Background, COLOR Color_Foreground )
{
    POINT Xpoint = Xstart;
    POINT Ypoint = Ystart;

    if(Xstart >= sLCD_DIS.LCD_Dis_Column || Ystart >= sLCD_DIS.LCD_Dis_Page) {
        return;
    }

    while(* pString != '\0') {
        //if X direction filled , reposition to(Xstart,Ypoint),Ypoint is Y direction plus the height of the character
        if((Xpoint + Font->Width ) > sLCD_DIS.LCD_Dis_Column ) {
            Xpoint = Xstart;
            Ypoint += Font->Height;
        }

        // If the Y direction is full, reposition to(Xstart, Ystart)
        if((Ypoint  + Font->Height ) > sLCD_DIS.LCD_Dis_Page ) {
            Xpoint = Xstart;
            Ypoint = Ystart;
        }
        GUI_DisChar(Xpoint, Ypoint, * pString, Font, Color_Background, Color_Foreground);

        //The next character of the address
        pString ++;

        //The next word of the abscissa increases the font of the broadband
        Xpoint += Font->Width + 1;
    }
}

/****************************************WHITE****************************************
function:	Display the string
parameter:
			Xstart ：X coordinate
			Ystart : Y coordinate
			Nummber: The number displayed
			Font  ：A structure pointer that displays a character size
			Color_Background : Select the background color of the English character
			Color_Foreground : Select the foreground color of the English character
********************************************************************************/
#define  ARRAY_LEN 255
void GUI_DisNum(POINT Xpoint, POINT Ypoint, int32_t Nummber,
                sFONT* Font,COLOR Color_Background, COLOR Color_Foreground )
{

    int16_t Num_Bit = 0, Str_Bit = 0;
    uint8_t Str_Array[ARRAY_LEN] = {0},Num_Array[ARRAY_LEN] = {0};
    uint8_t *pStr = Str_Array;

    if(Xpoint >= sLCD_DIS.LCD_Dis_Column || Ypoint >= sLCD_DIS.LCD_Dis_Page) {
        return;
    }

    //Converts a number to a string
    while(Nummber) {
        Num_Array[Num_Bit] = Nummber % 10 + '0';
        Num_Bit++;
        Nummber /= 10;
    }

    //The string is inverted
    while(Num_Bit > 0) {
        Str_Array[Str_Bit] = Num_Array[Num_Bit -1];
        Str_Bit ++;
        Num_Bit --;
    }

    //show
    GUI_DisString_EN(Xpoint, Ypoint, (const char*)pStr, Font, Color_Background, Color_Foreground );
}

void GUI_Disbitmap(POINT Xpoint, POINT Ypoint, const unsigned char *pBmp,
						POINT Width, POINT Height)
{
    POINT i, j, byteWidth = (Width + 7)/8;
    for(j = 0; j < Height; j++) {
        for(i = 0; i <Width; i ++) {
            if(*(pBmp + j*byteWidth + i/8) & (128 >> (i & 7))) {
                GUI_DrawPoint(Xpoint+i, Ypoint+j, WHITE, DOT_PIXEL_DFT, DOT_STYLE_DFT);
            }
        }
    }
}

/********************************************************************************
function:	LCD_Show
parameter:
********************************************************************************/
void GUI_Show(void)
{	
	printf("clear lcd background\n"); //debug
	LCD_Clear(GUI_BACKGROUND);
	
	printf("GUI Draw Line \r\n");
	GUI_DrawLine(0, 10, sLCD_DIS.LCD_Dis_Column, 10, RED,LINE_SOLID, DOT_PIXEL_2X2);
	//GUI_DrawLine(0, sLCD_DIS.LCD_Dis_Page - 10, sLCD_DIS.LCD_Dis_Column, sLCD_DIS.LCD_Dis_Page - 10, RED,LINE_SOLID, DOT_PIXEL_2X2);	
	GUI_DrawLine(0, 20, sLCD_DIS.LCD_Dis_Column, 20, RED,LINE_DOTTED, DOT_PIXEL_DFT);
	//GUI_DrawLine(0, sLCD_DIS.LCD_Dis_Page - 20, sLCD_DIS.LCD_Dis_Column, sLCD_DIS.LCD_Dis_Page - 20, RED,LINE_DOTTED, DOT_PIXEL_DFT);

	printf("GUI Draw Rectangle \r\n");
	GUI_DrawRectangle(0,0,128,9,BLUE, DRAW_FULL, DOT_PIXEL_1X1);
	//GUI_DrawRectangle(1,1,128,128,RED,DRAW_EMPTY,DOT_PIXEL_2X2);
	
	printf("GUI Draw Olympic Rings\r\n");
	uint16_t Cx1 = 40, Cy1 = 85, Cr = 12;
	uint16_t Cx2 = Cx1 + (2.5 * Cr), Cy2 = Cy1;
	uint16_t Cx3 = Cx1 + (5 * Cr), Cy3 = Cy1;
	uint16_t Cx4 = ( Cx1 + Cx2 )/2, Cy4 = Cy1 + Cr;
	uint16_t Cx5 = ( Cx2 + Cx3 )/2, Cy5 = Cy1 + Cr;

	GUI_DrawCircle( Cx1, Cy1, Cr, BLUE, DRAW_EMPTY, DOT_PIXEL_DFT);
	GUI_DrawCircle( Cx2, Cy2, Cr, BLACK, DRAW_EMPTY, DOT_PIXEL_DFT);
	GUI_DrawCircle( Cx3, Cy3, Cr, RED, DRAW_EMPTY, DOT_PIXEL_DFT);
	GUI_DrawCircle( Cx4, Cy4, Cr, YELLOW, DRAW_EMPTY, DOT_PIXEL_DFT);
	GUI_DrawCircle( Cx5, Cy5, Cr, GREEN, DRAW_EMPTY, DOT_PIXEL_DFT);

	printf("GUI Draw Realistic circles\r\n");
	GUI_DrawCircle(15, 110, 10, BRRED, DRAW_FULL, DOT_PIXEL_DFT);
	GUI_DrawCircle(sLCD_DIS.LCD_Dis_Column - 15, 110, 10, BRRED, DRAW_FULL, DOT_PIXEL_DFT);

	printf("GUI Display String \r\n");
	GUI_DisString_EN(35,20,"WaveShare",&Font12,GUI_BACKGROUND,BLUE);
	GUI_DisString_EN(32,33,"Electronic",&Font12,GUI_BACKGROUND,BLUE);
	GUI_DisString_EN(28,45,"1.44inch TFTLCD",&Font8,RED,GRED);

	printf("GUI Display Nummber \r\n");
	GUI_DisNum(28,55,1234567890,&Font12,GUI_BACKGROUND,BLUE);
}



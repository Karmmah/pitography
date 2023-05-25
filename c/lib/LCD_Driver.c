
/***********************************************************************************************************************
* | file      	:	LCD_Driver.c
* |	version		:	V1.0
* | date		:	2017-10-16
* | function	:	On the ST7735S chip driver and clear screen, drawing lines, drawing, writing
					and other functions to achieve
***********************************************************************************************************************/

#include "LCD_Driver.h"
#include "DEV_Config.h"

#include <stdlib.h>		//itoa()
#include <stdio.h>

LCD_DIS sLCD_DIS;

/***********************************************************************************************************************
			------------------------------------------------------------------------
			|\\\																///|
			|\\\						Drive layer								///|
			------------------------------------------------------------------------
***********************************************************************************************************************/
/*******************************************************************************
function:
			Hardware reset
*******************************************************************************/
static void LCD_Reset(void)
{
    LCD_RST_1;
    DEV_Delay_ms(100);
    LCD_RST_0;
    DEV_Delay_ms(100);
    LCD_RST_1;
    DEV_Delay_ms(100);
}

/*******************************************************************************
function:
		Write register address and data
*******************************************************************************/
static void LCD_WriteReg(uint8_t Reg)
{
    LCD_DC_0;
    //LCD_CS_0;
    DEV_SPI_WriteByte(Reg);
    //LCD_CS_1;
}

static void LCD_WriteData_8Bit(uint8_t Data)
{
    LCD_DC_1;
    //LCD_CS_0;
    DEV_SPI_WriteByte(Data);
    //LCD_CS_1;
}
/*
static void LCD_WriteData_16Bit(uint16_t Data)
{
    LCD_DC_1;
    //LCD_CS_0;
    DEV_SPI_WriteByte(Data >> 8);
    DEV_SPI_WriteByte(Data & 0XFF);
    //LCD_CS_1;
}*/

static void LCD_WriteData_NLen16Bit(uint16_t Data,uint32_t DataLen)
{
    uint32_t i;
    LCD_DC_1;
    //LCD_CS_0;
    for(i = 0; i < DataLen; i++) {
        DEV_SPI_WriteByte( (uint8_t)(Data >> 8) );
        DEV_SPI_WriteByte( (uint8_t)(Data & 0XFF) );
    }
    //LCD_CS_1;
}

/*******************************************************************************
function:
		Common register initialization
*******************************************************************************/
static void LCD_InitReg(void)
{
    //ST7735R Frame Rate
    LCD_WriteReg(0xB1);
    LCD_WriteData_8Bit(0x01);
    LCD_WriteData_8Bit(0x2C);
    LCD_WriteData_8Bit(0x2D);

    LCD_WriteReg(0xB2);
    LCD_WriteData_8Bit(0x01);
    LCD_WriteData_8Bit(0x2C);
    LCD_WriteData_8Bit(0x2D);

    LCD_WriteReg(0xB3);
    LCD_WriteData_8Bit(0x01);
    LCD_WriteData_8Bit(0x2C);
    LCD_WriteData_8Bit(0x2D);
    LCD_WriteData_8Bit(0x01);
    LCD_WriteData_8Bit(0x2C);
    LCD_WriteData_8Bit(0x2D);

    LCD_WriteReg(0xB4); //Column inversion
    LCD_WriteData_8Bit(0x07);

    //ST7735R Power Sequence
    LCD_WriteReg(0xC0);
    LCD_WriteData_8Bit(0xA2);
    LCD_WriteData_8Bit(0x02);
    LCD_WriteData_8Bit(0x84);
    LCD_WriteReg(0xC1);
    LCD_WriteData_8Bit(0xC5);

    LCD_WriteReg(0xC2);
    LCD_WriteData_8Bit(0x0A);
    LCD_WriteData_8Bit(0x00);

    LCD_WriteReg(0xC3);
    LCD_WriteData_8Bit(0x8A);
    LCD_WriteData_8Bit(0x2A);
    LCD_WriteReg(0xC4);
    LCD_WriteData_8Bit(0x8A);
    LCD_WriteData_8Bit(0xEE);

    LCD_WriteReg(0xC5); //VCOM
    LCD_WriteData_8Bit(0x0E);

    //ST7735R Gamma Sequence
    LCD_WriteReg(0xe0);
    LCD_WriteData_8Bit(0x0f);
    LCD_WriteData_8Bit(0x1a);
    LCD_WriteData_8Bit(0x0f);
    LCD_WriteData_8Bit(0x18);
    LCD_WriteData_8Bit(0x2f);
    LCD_WriteData_8Bit(0x28);
    LCD_WriteData_8Bit(0x20);
    LCD_WriteData_8Bit(0x22);
    LCD_WriteData_8Bit(0x1f);
    LCD_WriteData_8Bit(0x1b);
    LCD_WriteData_8Bit(0x23);
    LCD_WriteData_8Bit(0x37);
    LCD_WriteData_8Bit(0x00);
    LCD_WriteData_8Bit(0x07);
    LCD_WriteData_8Bit(0x02);
    LCD_WriteData_8Bit(0x10);

    LCD_WriteReg(0xe1);
    LCD_WriteData_8Bit(0x0f);
    LCD_WriteData_8Bit(0x1b);
    LCD_WriteData_8Bit(0x0f);
    LCD_WriteData_8Bit(0x17);
    LCD_WriteData_8Bit(0x33);
    LCD_WriteData_8Bit(0x2c);
    LCD_WriteData_8Bit(0x29);
    LCD_WriteData_8Bit(0x2e);
    LCD_WriteData_8Bit(0x30);
    LCD_WriteData_8Bit(0x30);
    LCD_WriteData_8Bit(0x39);
    LCD_WriteData_8Bit(0x3f);
    LCD_WriteData_8Bit(0x00);
    LCD_WriteData_8Bit(0x07);
    LCD_WriteData_8Bit(0x03);
    LCD_WriteData_8Bit(0x10);

    LCD_WriteReg(0xF0); //Enable test command
    LCD_WriteData_8Bit(0x01);

    LCD_WriteReg(0xF6); //Disable ram power save mode
    LCD_WriteData_8Bit(0x00);

    LCD_WriteReg(0x3A); //65k mode
    LCD_WriteData_8Bit(0x05);

}


/********************************************************************************
function:	Set the display scan and color transfer modes
parameter:
		Scan_dir   :   Scan direction
		Colorchose :   RGB or GBR color format
********************************************************************************/
void LCD_SetGramScanWay(LCD_SCAN_DIR Scan_dir)
{
    //Get the screen scan direction
    sLCD_DIS.LCD_Scan_Dir = Scan_dir;

    //Get GRAM and LCD width and height
    if(Scan_dir == L2R_U2D || Scan_dir == L2R_D2U || Scan_dir == R2L_U2D || Scan_dir == R2L_D2U) {
        sLCD_DIS.LCD_Dis_Column	= LCD_HEIGHT ;
        sLCD_DIS.LCD_Dis_Page = LCD_WIDTH ;
    } else {
        sLCD_DIS.LCD_Dis_Column	= LCD_WIDTH ;
        sLCD_DIS.LCD_Dis_Page = LCD_HEIGHT ;
    }

    // Gets the scan direction of GRAM
    uint16_t MemoryAccessReg_Data=0;  //0x36
    switch (Scan_dir) {
    case L2R_U2D:
        MemoryAccessReg_Data = 0X00 | 0x00;//x Scan direction | y Scan direction
        break;
    case L2R_D2U:
        MemoryAccessReg_Data = 0x00 | 0x80;//0xC8 | 0X10
        break;
    case R2L_U2D://	0X4
        MemoryAccessReg_Data = 0x40 | 0x00;
        break;
    case R2L_D2U://	0XC
        MemoryAccessReg_Data = 0x40 | 0x80;
        break;
    case U2D_L2R://0X2
        MemoryAccessReg_Data = 0X00 | 0X00 | 0x20;
        break;
    case U2D_R2L://0X6
        MemoryAccessReg_Data = 0x00 | 0X40 | 0x20;
        break;
    case D2U_L2R://0XA
        MemoryAccessReg_Data = 0x80 | 0x00 | 0x20;
        break;
    case D2U_R2L://0XE
        MemoryAccessReg_Data = 0x40 | 0x80 | 0x20;
        break;
    }

    //please set (MemoryAccessReg_Data & 0x10) != 1
    if((MemoryAccessReg_Data && 0x20) != 1) {
        sLCD_DIS.LCD_X_Adjust = LCD_X;
        sLCD_DIS.LCD_Y_Adjust = LCD_Y;
    } else {
        sLCD_DIS.LCD_X_Adjust = LCD_Y;
        sLCD_DIS.LCD_Y_Adjust = LCD_X;
    }

    // Set the read / write scan direction of the frame memory
    LCD_WriteReg(0x36); //MX, MY, RGB mode
#if defined(LCD_1IN44)
    LCD_WriteData_8Bit( MemoryAccessReg_Data | 0x08);	//0x08 set RGB
#elif defined(LCD_1IN8)
    LCD_WriteData_8Bit( MemoryAccessReg_Data & 0xf7);	//RGB color filter panel
#endif

}

/***********************************************************************************************************************
			------------------------------------------------------------------------
			|\\\																///|
			|\\\						App layer								///|
			------------------------------------------------------------------------
***********************************************************************************************************************/

/********************************************************************************
function:
			initialization
********************************************************************************/
void LCD_Init( LCD_SCAN_DIR Lcd_ScanDir )
{
    //Turn on the backlight
    LCD_BL_1;

    //Hardware reset
    LCD_Reset();

    //Set the initialization register
    LCD_InitReg();

    //Set the display scan and color transfer modes
    LCD_SetGramScanWay( Lcd_ScanDir );
    DEV_Delay_ms(200);

    //sleep out
    LCD_WriteReg(0x11);
    DEV_Delay_ms(120);

    //Turn on the LCD display
    LCD_WriteReg(0x29);
}

/********************************************************************************
function:	Sets the start position and size of the display area
parameter:
		Xstart 	:   X direction Start coordinates
		Ystart  :   Y direction Start coordinates
		Xend    :   X direction end coordinates
		Yend    :   Y direction end coordinates
********************************************************************************/
void LCD_SetWindows( POINT Xstart, POINT Ystart, POINT Xend, POINT Yend )
{

    //set the X coordinates
    LCD_WriteReg ( 0x2A );
    LCD_WriteData_8Bit ( 0x00 );						//Set the horizontal starting point to the high octet
    LCD_WriteData_8Bit ( (Xstart & 0xff) + sLCD_DIS.LCD_X_Adjust);			//Set the horizontal starting point to the low octet
    LCD_WriteData_8Bit ( 0x00 );				//Set the horizontal end to the high octet
    LCD_WriteData_8Bit ( (( Xend - 1 ) & 0xff) + sLCD_DIS.LCD_X_Adjust);	//Set the horizontal end to the low octet

    //set the Y coordinates
    LCD_WriteReg ( 0x2B );
    LCD_WriteData_8Bit ( 0x00 );
    LCD_WriteData_8Bit ( (Ystart & 0xff) + sLCD_DIS.LCD_Y_Adjust);
    LCD_WriteData_8Bit ( 0x00 );
    LCD_WriteData_8Bit ( ( (Yend - 1) & 0xff )+ sLCD_DIS.LCD_Y_Adjust);

    LCD_WriteReg(0x2C);

}

/********************************************************************************
function:	Set the display point (Xpoint, Ypoint)
parameter:
		xStart :   X direction Start coordinates
		xEnd   :   X direction end coordinates
********************************************************************************/
void LCD_SetCursor ( POINT Xpoint, POINT Ypoint )
{
    LCD_SetWindows ( Xpoint, Ypoint, Xpoint , Ypoint );
}

/********************************************************************************
function:	Set show color
parameter:
		Color  :   Set show color
********************************************************************************/
//static void LCD_SetColor( LENGTH Dis_Width, LENGTH Dis_Height, COLOR Color ){
void LCD_SetColor( COLOR Color ,POINT Xpoint, POINT Ypoint)
{
    LCD_WriteData_NLen16Bit(Color ,(uint32_t)Xpoint * (uint32_t)Ypoint);
}

/********************************************************************************
function:	Point (Xpoint, Ypoint) Fill the color
parameter:
		Xpoint :   The x coordinate of the point
		Ypoint :   The y coordinate of the point
		Color  :   Set the color
********************************************************************************/
void LCD_SetPointlColor ( POINT Xpoint, POINT Ypoint, COLOR Color )
{
    if ( ( Xpoint <= sLCD_DIS.LCD_Dis_Column ) && ( Ypoint <= sLCD_DIS.LCD_Dis_Page ) ) {
        LCD_SetCursor (Xpoint, Ypoint);
        LCD_SetColor ( Color , 1 , 1);
    }
}

/********************************************************************************
function:	Fill the area with the color
parameter:
		Xstart :   Start point x coordinate
		Ystart :   Start point y coordinate
		Xend   :   End point coordinates
		Yend   :   End point coordinates
		Color  :   Set the color
********************************************************************************/
void LCD_SetArealColor (POINT Xstart, POINT Ystart, POINT Xend, POINT Yend,	COLOR  Color)
{
    if((Xend > Xstart) && (Yend > Ystart)) {
        LCD_SetWindows( Xstart , Ystart , Xend , Yend  );
        LCD_SetColor ( Color ,Xend - Xstart , Yend - Ystart );
    }
}

/********************************************************************************
function:
			Clear screen
********************************************************************************/
void LCD_Clear(COLOR  Color)
{
    LCD_SetArealColor(0,0, sLCD_DIS.LCD_Dis_Column , sLCD_DIS.LCD_Dis_Page, Color);
}




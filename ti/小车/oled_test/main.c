#include <msp430.h> 
#include "oledfont.h"
#include "oled.h"       //里面有SDA和SCL引脚定义，移植时需注意修改

//延时函数，IAR自带，经常使用到
#define CPU_F ((double)8000000)   //外部高频晶振8MHZ
//#define CPU_F ((double)32768)   //外部低频晶振32.768KHZ
#define delay_us(x) __delay_cycles((long)(CPU_F*(double)x/1000000.0))
#define delay_ms(x) __delay_cycles((long)(CPU_F*(double)x/1000.0))



void main(void)//主函数
{
     WDTCTL = WDTPW + WDTHOLD;       //关闭看门狗

     BCSCTL1 = CALBC1_8MHZ;                    // Set range
     DCOCTL = CALDCO_8MHZ;


     OLED_Init(); //OLED初始化
     delay_ms(200);


        OLED_ShowChar(0,0,'S');//停止提示
        OLED_ShowChar(8,0,'t');
        OLED_ShowChar(16,0,'o');
        OLED_ShowChar(24,0,'p');

}

#include <msp430.h> 
#include "oledfont.h"
#include "oled.h"       //里面有SDA和SCL引脚定义，移植时需注意修改

//延时函数，IAR自带，经常使用到
#define CPU_F ((double)8000000)   //外部高频晶振8MHZ
//#define CPU_F ((double)32768)   //外部低频晶振32.768KHZ
#define delay_us(x) __delay_cycles((long)(CPU_F*(double)x/1000000.0))
#define delay_ms(x) __delay_cycles((long)(CPU_F*(double)x/1000.0))

char name[6]="Name:";
char name1[11]="T.Z_Gyatso";
char num[8]="Number:";
char num1[15]="22920222205252";
char department[7]="Depart:";
char depart[9]="Comm.Eng";

void main(void)//主函数
{
     WDTCTL = WDTPW + WDTHOLD;       //关闭看门狗

     BCSCTL1 = CALBC1_8MHZ;                    // Set range
     DCOCTL = CALDCO_8MHZ;


     OLED_Init(); //OLED初始化
     delay_ms(200);
     int i;
     while(1){
     for(i = 0;i < 5;i++)
            OLED_ShowChar(i*8,0,name[i]);
     for(i = 0;i < 10;i++)
                 OLED_ShowChar((i+5)*8,0,name1[i]);
     for(i = 0;i < 7;i++)
                 OLED_ShowChar(i*8,2,num[i]);
     for(i = 0;i < 14;i++)
                 OLED_ShowChar((i+2)*8,4,num1[i]);
     for(i = 0;i < 7;i++)
                 OLED_ShowChar(i*8,6,department[i]);
     for(i = 0;i < 8;i++)
                 OLED_ShowChar((i+8)*8,6,depart[i]);
     }

}

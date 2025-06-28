#include <msp430.h> 
#include "oledfont.h"
#include "oled.h"       //������SDA��SCL���Ŷ��壬��ֲʱ��ע���޸�

//��ʱ������IAR�Դ�������ʹ�õ�
#define CPU_F ((double)8000000)   //�ⲿ��Ƶ����8MHZ
//#define CPU_F ((double)32768)   //�ⲿ��Ƶ����32.768KHZ
#define delay_us(x) __delay_cycles((long)(CPU_F*(double)x/1000000.0))
#define delay_ms(x) __delay_cycles((long)(CPU_F*(double)x/1000.0))

char name[6]="Name:";
char name1[11]="T.Z_Gyatso";
char num[8]="Number:";
char num1[15]="22920222205252";
char department[7]="Depart:";
char depart[9]="Comm.Eng";

void main(void)//������
{
     WDTCTL = WDTPW + WDTHOLD;       //�رտ��Ź�

     BCSCTL1 = CALBC1_8MHZ;                    // Set range
     DCOCTL = CALDCO_8MHZ;


     OLED_Init(); //OLED��ʼ��
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

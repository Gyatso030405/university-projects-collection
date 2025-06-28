#include <msp430.h> 
#include "oledfont.h"
#include "oled.h"       //������SDA��SCL���Ŷ��壬��ֲʱ��ע���޸�

//��ʱ������IAR�Դ�������ʹ�õ�
#define CPU_F ((double)8000000)   //�ⲿ��Ƶ����8MHZ
//#define CPU_F ((double)32768)   //�ⲿ��Ƶ����32.768KHZ
#define delay_us(x) __delay_cycles((long)(CPU_F*(double)x/1000000.0))
#define delay_ms(x) __delay_cycles((long)(CPU_F*(double)x/1000.0))



void main(void)//������
{
     WDTCTL = WDTPW + WDTHOLD;       //�رտ��Ź�

     BCSCTL1 = CALBC1_8MHZ;                    // Set range
     DCOCTL = CALDCO_8MHZ;


     OLED_Init(); //OLED��ʼ��
     delay_ms(200);


        OLED_ShowChar(0,0,'S');//ֹͣ��ʾ
        OLED_ShowChar(8,0,'t');
        OLED_ShowChar(16,0,'o');
        OLED_ShowChar(24,0,'p');

}

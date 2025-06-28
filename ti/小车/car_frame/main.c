#include <msp430.h> 
#include "oledfont.h"
#include "oled.h"       //������SDA��SCL���Ŷ��壬��ֲʱ��ע���޸�


//��ʱ������IAR�Դ�������ʹ�õ�
#define CPU_F ((double)8000000)   //�ⲿ��Ƶ����8MHZ
#define delay_us(x) __delay_cycles((long)(CPU_F*(double)x/1000000.0))
#define delay_ms(x) __delay_cycles((long)(CPU_F*(double)x/1000.0))


#define hy1 (P1IN&BIT4) //Ѱ�����
#define hy2 (P1IN&BIT5) //ֹͣ���

#define key3 (P1IN&BIT3) //������⣨���������ã������µ͵�ƽ��̧��ߵ�ƽ��
#define key2 (P1IN&BIT7) //������⣨���µ͵�ƽ��̧��ߵ�ƽ��
#define key1 (P2IN&BIT5) //������⣨���µ͵�ƽ��̧��ߵ�ƽ��

#define FM_L            P2OUT &= ~BIT0            //�������õ͵�ƽ
#define FM_H            P2OUT |= BIT0             //�������øߵ�ƽ



//***********************************************************************
//             TIMERA��ʼ��������ΪUPģʽ����
//***********************************************************************
int t_miao=0,count,setmode=15;
void TIMERA_Init(void)
{   //��TA0��׽/�Ƚ��ж�ʹ��
    TA0CCTL0 = CCIE;
    //TA0ʱ������      SMCLK��ʱ��Դ        8��Ƶ            ��������ģʽ
    TA0CTL |= (TASSEL1 + ID_3 + MC_2);
    //����50000�ο��ж�
    TA0CCR0 = 50000;
}

//***********************************************************************
//             TIMERA�жϷ��������Ҫ�ж��ж�����
//***********************************************************************
// Timer A0 interrupt service routine
#pragma vector=TIMER0_A0_VECTOR
__interrupt void Timer_A (void)
{
    TA0CCR0 += 50000;                            // Add Offset to CCR0
    count++;

      if(count>=20)     //1��
      {
         count=0;
         t_miao++;
         P1OUT^=BIT6;//LED��P1.6��˸��ʾ
      }
}
//***********************************************************************
//             TIMERA��ʼ��������
//***********************************************************************

/*********************С����������**************************/
char set_time[10]="set time:";
char attr_num[6]="attr:";
char current_time[14]="current time:";
int i;
int per;//ռ�ձ� = 50%+ ��p-10��*5%
//10  11  12  13   14   15 16 17 18 19 20
//15  13  12  10.5 10   8  **  7 **  6  **
int p = 0;
double attr[2][11]={
              {15,13,12,10.5,10,//10 11 12 13 14
              8,7.5,7,6.75,6.5,        //15 16 17 18 19
              6},               //20
              {20,19.5,18.5,18,18,
              18,17,16.75,16.5,16,
              15}
};
//10  11  12  13   14   15 16 17 18 19 20
//**   **  **   **  **   15  **  ** **  **  15
//double m[5]={1,2.5};
void go()
{
    //TimerA1������PWM�������
    TA1CCR0 = 20000; // PWM ���� 20MS
    TA1CCTL1 = OUTMOD_7;
    TA1CCR1 = 0; //PWMΪ0ֹͣ״̬

    TA1CCTL2 = OUTMOD_7;
    TA1CCR2 = 0;//PWMΪ0ֹͣ״̬
    TA1CTL = (TASSEL1 + ID0 + ID1 + MC0);
    t_miao = 0;
    //per = 2;
    delay_ms(200);
    while(1)
    {
        //OLED��ʾ
        OLED_ShowChar(0,0,'g');
        OLED_ShowChar(8,0,'o');
        for(i = 0;i < 13;i++)
            OLED_ShowChar(i*8,2,current_time[i]);
        OLED_ShowChar(13*8,2,'0'+t_miao/10);
        OLED_ShowChar(14*8,2,'0'+t_miao%10);
        for(i = 0;i < 5;i++)
            OLED_ShowChar(i*8,4,attr_num[i]);
        OLED_ShowChar(5*8,4,'0'+(int)(attr[p][per-10])/10);
        OLED_ShowChar(6*8,4,'0'+(int)(attr[p][per-10])%10);
        OLED_ShowChar(7*8,4,'.');
        OLED_ShowChar(8*8,4,'0'+(int)(attr[p][per-10]*10)%10);
        for(i = 0;i < 9;i++)
            OLED_ShowChar(i*8,6,set_time[i]);

        OLED_ShowChar(9*8,6,'0'+per/10);
        OLED_ShowChar(10*8,6,'0'+per%10);
        OLED_ShowChar(14*8,6,'0'+p);

        //С����ʻ����
        TA1CCR2 = (int)(attr[p][per-10]*500);
        TA1CCR1 = (int)(attr[p][per-10]*500);

        if(hy1 && hy2)
        {
            TA1CCR2 = 0;
            TA1CCR1 = 0;
            FM_L;
            OLED_ShowChar(0,0,'s');
            OLED_ShowChar(8,0,'t');
            OLED_ShowChar(16,0,'o');
            OLED_ShowChar(24,0,'p');
            if(t_miao-per>2)t_miao-=2;
            else if(per-t_miao>2)t_miao+=2;
            if(t_miao-per==2)t_miao-=1;
            else if(per-t_miao==2)t_miao+=1;
            for(i = 0;i < 13;i++)
                OLED_ShowChar(i*8,2,current_time[i]);
            OLED_ShowChar(13*8,2,'0'+t_miao/10);
            OLED_ShowChar(14*8,2,'0'+t_miao%10);
            delay_ms(1000);
            FM_H;
            break;
//            TA1CCR2 = 1;
//            TA1CCR1 = 0;
//            delay_ms(1000);
//            break;
        }
        else if(hy2)TA1CCR2 = (int)(attr[p][per-10]*5);
        else if(hy1)TA1CCR1 = (int)(attr[p][per-10]*5);
        delay_ms(100);


    }
}
/*********************С�����н���**************************/


//
void main(void)//������
{
     WDTCTL = WDTPW | WDTHOLD;              //�رտ��Ź�����

     BCSCTL1 = CALBC1_8MHZ;                 //ϵͳʱ������Ϊ8MHz
     DCOCTL = CALDCO_8MHZ;

     TIMERA_Init();                         //����TIMERA
     _EINT();

     OLED_Init(); //OLED��ʼ��
     delay_ms(200);

     //P1��������
     P1DIR |= (BIT0 + BIT6);
     P1DIR &= ~(BIT3 + BIT4 + BIT5 + BIT7);
     P1IE |=  BIT3 + BIT7;
     P1IES |= BIT3 + BIT7;
     P1REN |= BIT3 + BIT7;
     P1IFG &= ~(BIT3 + BIT7);

     //P2��������
     P2DIR |= (BIT0 + BIT1 + BIT2 + BIT3 + BIT4);
     P2DIR &= ~(BIT5);
     P2SEL |= (BIT1+BIT4);
     P2OUT &= ~(BIT1 + BIT4);
     P2OUT |= BIT0;


     while(1)
     {
         //OLED��ʾ
         delay_ms(200);
         per = 10;
         while(1)
         {
             if(!key1)break;
             delay_ms(200);
             for(i = 0;i < 5;i++)
                 OLED_ShowChar(i*8,4,attr_num[i]);
             OLED_ShowChar(5*8,4,'0'+(int)(attr[p][per-10])/10);
             OLED_ShowChar(6*8,4,'0'+(int)(attr[p][per-10])%10);
             OLED_ShowChar(7*8,4,'.');
             OLED_ShowChar(8*8,4,'0'+(int)(attr[p][per-10]*10)%10);
             for(i = 0;i < 9;i++)
                 OLED_ShowChar(i*8,6,set_time[i]);
             OLED_ShowChar(9*8,6,'0'+per/10);
             OLED_ShowChar(10*8,6,'0'+per%10);
             OLED_ShowChar(14*8,6,'0'+p);
         }
         delay_ms(200);
//         per = 30 - per;

         go();

         delay_ms(2000);
         break;
    }
}


// ����ʱ��
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector=PORT1_VECTOR
__interrupt void Port_1(void)
#elif defined(__GNUC__)
void __attribute__ ((interrupt(PORT1_VECTOR))) Port_1 (void)
#else
#error Compiler not supported!
#endif
{
    if(!key3)
    {
        if(p)p=0;
        else p=1;
        P1IFG &= ~BIT3;
    }
    if(!key2)
    {
        per++;
        if(per>20)per = 10;
        P1IFG &= ~BIT7;
    }

}

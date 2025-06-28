#include <msp430.h> 
#include "oledfont.h"
#include "oled.h"       //里面有SDA和SCL引脚定义，移植时需注意修改


//延时函数，IAR自带，经常使用到
#define CPU_F ((double)8000000)   //外部高频晶振8MHZ
#define delay_us(x) __delay_cycles((long)(CPU_F*(double)x/1000000.0))
#define delay_ms(x) __delay_cycles((long)(CPU_F*(double)x/1000.0))


#define hy1 (P1IN&BIT4) //寻迹检测
#define hy2 (P1IN&BIT5) //停止检测

#define key3 (P1IN&BIT3) //按键检测（开发板内置）（按下低电平，抬起高电平）
#define key2 (P1IN&BIT7) //按键检测（按下低电平，抬起高电平）
#define key1 (P2IN&BIT5) //按键检测（按下低电平，抬起高电平）

#define FM_L            P2OUT &= ~BIT0            //蜂鸣器置低电平
#define FM_H            P2OUT |= BIT0             //蜂鸣器置高电平



//***********************************************************************
//             TIMERA初始化，设置为UP模式计数
//***********************************************************************
int t_miao=0,count,setmode=15;
void TIMERA_Init(void)
{   //打开TA0捕捉/比较中断使能
    TA0CCTL0 = CCIE;
    //TA0时钟设置      SMCLK做时钟源        8分频            连续计数模式
    TA0CTL |= (TASSEL1 + ID_3 + MC_2);
    //计数50000次开中断
    TA0CCR0 = 50000;
}

//***********************************************************************
//             TIMERA中断服务程序，需要判断中断类型
//***********************************************************************
// Timer A0 interrupt service routine
#pragma vector=TIMER0_A0_VECTOR
__interrupt void Timer_A (void)
{
    TA0CCR0 += 50000;                            // Add Offset to CCR0
    count++;

      if(count>=20)     //1秒
      {
         count=0;
         t_miao++;
         P1OUT^=BIT6;//LED灯P1.6闪烁提示
      }
}
//***********************************************************************
//             TIMERA初始化，结束
//***********************************************************************

/*********************小车启动程序**************************/
char set_time[10]="set time:";
char attr_num[6]="attr:";
char current_time[14]="current time:";
int i;
int per;//占空比 = 50%+ （p-10）*5%
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
    //TimerA1和它的PWM输出设置
    TA1CCR0 = 20000; // PWM 周期 20MS
    TA1CCTL1 = OUTMOD_7;
    TA1CCR1 = 0; //PWM为0停止状态

    TA1CCTL2 = OUTMOD_7;
    TA1CCR2 = 0;//PWM为0停止状态
    TA1CTL = (TASSEL1 + ID0 + ID1 + MC0);
    t_miao = 0;
    //per = 2;
    delay_ms(200);
    while(1)
    {
        //OLED显示
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

        //小车行驶策略
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
/*********************小车运行结束**************************/


//
void main(void)//主函数
{
     WDTCTL = WDTPW | WDTHOLD;              //关闭看门狗设置

     BCSCTL1 = CALBC1_8MHZ;                 //系统时钟设置为8MHz
     DCOCTL = CALDCO_8MHZ;

     TIMERA_Init();                         //设置TIMERA
     _EINT();

     OLED_Init(); //OLED初始化
     delay_ms(200);

     //P1引脚配置
     P1DIR |= (BIT0 + BIT6);
     P1DIR &= ~(BIT3 + BIT4 + BIT5 + BIT7);
     P1IE |=  BIT3 + BIT7;
     P1IES |= BIT3 + BIT7;
     P1REN |= BIT3 + BIT7;
     P1IFG &= ~(BIT3 + BIT7);

     //P2引脚配置
     P2DIR |= (BIT0 + BIT1 + BIT2 + BIT3 + BIT4);
     P2DIR &= ~(BIT5);
     P2SEL |= (BIT1+BIT4);
     P2OUT &= ~(BIT1 + BIT4);
     P2OUT |= BIT0;


     while(1)
     {
         //OLED显示
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


// 设置时间
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

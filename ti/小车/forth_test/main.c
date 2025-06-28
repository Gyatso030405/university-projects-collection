

#include <msp430.h>

void configureClockSystem(void) {
    BCSCTL1 = CALBC1_1MHZ;   // 设置DCO为1MHz
    DCOCTL = CALDCO_1MHZ;    // 设置DCO为1MHz
}

void configureTimerA0(void) {
    TA0CCR0 = 1000 - 1;          // PWM周期
    TA0CCTL1 = OUTMOD_7;         // CCR1 reset/set模式
    TA0CCR1 = 0;                 // CCR1 PWM占空比
    TA0CTL = TASSEL_2 + MC_1;    // SMCLK, up mode
}

void configurePins(void) {
    P1DIR |= BIT6;               // P1.6输出
    P1SEL |= BIT6;               // P1.6设为TA0.1输出
}

void main(void) {
    WDTCTL = WDTPW + WDTHOLD;    // 关闭看门狗
    configureClockSystem();
    configurePins();
    configureTimerA0();

    int brightness = 0;
    int increment = 1;

    while (1) {
        TA0CCR1 = brightness;    // 更新占空比
        __delay_cycles(1000);    // 延迟

        brightness += increment;
        if (brightness == 1000 || brightness == 0) {
            increment = -increment; // 反转增量方向
        }
    }
}

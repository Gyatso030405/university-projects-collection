

#include <msp430.h>

void configureClockSystem(void) {
    BCSCTL1 = CALBC1_1MHZ;   // ����DCOΪ1MHz
    DCOCTL = CALDCO_1MHZ;    // ����DCOΪ1MHz
}

void configureTimerA0(void) {
    TA0CCR0 = 1000 - 1;          // PWM����
    TA0CCTL1 = OUTMOD_7;         // CCR1 reset/setģʽ
    TA0CCR1 = 0;                 // CCR1 PWMռ�ձ�
    TA0CTL = TASSEL_2 + MC_1;    // SMCLK, up mode
}

void configurePins(void) {
    P1DIR |= BIT6;               // P1.6���
    P1SEL |= BIT6;               // P1.6��ΪTA0.1���
}

void main(void) {
    WDTCTL = WDTPW + WDTHOLD;    // �رտ��Ź�
    configureClockSystem();
    configurePins();
    configureTimerA0();

    int brightness = 0;
    int increment = 1;

    while (1) {
        TA0CCR1 = brightness;    // ����ռ�ձ�
        __delay_cycles(1000);    // �ӳ�

        brightness += increment;
        if (brightness == 1000 || brightness == 0) {
            increment = -increment; // ��ת��������
        }
    }
}

#include <msp430.h> 


/**
 * main.c
 */
int main(void)
{
    WDTCTL = WDTPW + WDTHOLD;   // stop watchdog timer

//    BCSCTL1 = CALBC1_1MHZ;
    BCSCTL1 = CALBC1_8MHZ;

    P1DIR |= 0x01;


    for(;;)
    {
        volatile unsigned int i;
        P1OUT ^= 0x01;
        i = 50000;
        do (i--);
        while (i!=0);
    }
}

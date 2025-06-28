#include <msp430.h> 


/**
 * main.c
 */
int main(void)
{
	WDTCTL = WDTPW | WDTHOLD;	// stop watchdog timer
	
	DCOCTL = 0;
	BCSCTL1 = CALBC1_1MHZ;
	DCOCTL = CALDCO_1MHZ;

	P1DIR |= BIT0;
	P1DIR &= ~BIT3;
	P1REN |= BIT3;

	while(1)
	{
	    if(!(BIT3 & P1IN))
	        P1OUT |= BIT0;
	    else
	        P1OUT &= ~BIT0;
	}
	return 0;
}

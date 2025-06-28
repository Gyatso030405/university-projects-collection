#include <msp430.h> 
/**
 * main.c
 */
int main(void)
{
	WDTCTL = WDTPW + WDTHOLD;	// stop watchdog timer
	P1DIR |= BIT0;
	P1OUT &= ~BIT0;

	P1DIR &= ~BIT3;
	P1OUT != BIT3;
	P1REN |= BIT3;

	P1IES |= BIT3;
	P1IFG &= ~BIT3;
	P1IE |= BIT3;
	
	    P1DIR |= BIT6;
	    P1OUT &= ~BIT6;

	    P2DIR &= ~BIT0;
	    P2OUT != BIT0;
	    P2REN |= BIT0;

	    P2IES |= BIT0;
	    P2IFG &= ~BIT0;
	    P2IE |= BIT0;

	__bis_SR_register(GIE);
}

#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector=PORT1_VECTOR
__interrupt void Port_1(void)
#elif defined(__GNUC__)
void __attribute__ ((interrupt(PORT1_VECTOR))) Port_1 (void)
#else
#error Compiler not supported!
#endif
{
    P1OUT ^= BIT0; // P1.0 = toggle
    P1IFG &= ~BIT3; // P1.3 IFG cleared
}
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector=PORT2_VECTOR
__interrupt void Port_2(void)
#elif defined(__GNUC__)
void __attribute__ ((interrupt(PORT2_VECTOR))) Port_2 (void)
#else
#error Compiler not supported!
#endif
{
    P1OUT ^= BIT6; // P1.6 = toggle
    P2IFG &= ~BIT0; // P1.7 IFG cleared
}


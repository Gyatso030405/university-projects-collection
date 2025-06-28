
#include <msp430.h>

int main(void){

WDTCTL = WDTPW + WDTHOLD;
if (CALBC1_1MHZ == 0xFF)
{
    while(1);
}

DCOCTL = 0;
BCSCTL1 = CALBC1_1MHZ;
DCOCTL = CALDCO_1MHZ;
P1DIR |=BIT0;
P1OUT &= ~BIT0;
P1SEL = BIT1 + BIT2 ;
P1SEL2 = BIT1 + BIT2 ;

UCA0CTL1 |= UCSSEL_2;
UCA0BR0 = 104;
UCA0BR1 = 0;
UCA0MCTL = UCBRS0;
UCA0CTL1 &= ~UCSWRST;
IE2 |= UCA0RXIE;

__bis_SR_register(LPM0_bits+ GIE);
}
void sendString(const char *str)
{
    while(*str)
    {
        while (!(IFG2&UCA0TXIFG));
        UCA0TXBUF=*str++;
    }
}

#if defined( __TI_COMPILER_VERSION__) ||defined(__IAR_SYSTEMS_ICC__)
#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void)
#elif defined(__GNUC__)
void __attribute__((interrupt(USCIAB0RX_VECTOR))) USCI0RX_ISR (void)
#else
#error Compiler not supported!
#endif
{
    char receiveChar =UCA0RXBUF;
while (!(IFG2&UCA0TXIFG));
   if(receiveChar=='1'){
       P1OUT |=BIT0;
       sendString("LED_ON");
   }
   else if(receiveChar=='0'){
          P1OUT &=~BIT0;
          sendString("LED_OFF");
      }
   else    {P1OUT ^=BIT0;

         if(!(P1OUT&BIT0))sendString("LED_OFF");
            if(P1OUT&BIT0)sendString("LED_ON");}
    IFG2 &=~UCA0RXIFG;

}


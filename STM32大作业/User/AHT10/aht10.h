#ifndef _AHT10_H
#define _AHT10_H

#include <stdint.h>
#include "stm32f4xx_hal.h"

#define AHT10_ADDR 0x38  //从机地址
#define AHT10_WRITE 0x70  //从机写地址
#define AHT10_READ 0x71  //从机读地址

void AHT10_Init(void);
void AHT10_RST(void);
void AHT10_Read(void);

#endif /* aht10_H */


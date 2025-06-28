#ifndef _AHT10_IIC_H
#define _AHT10_IIC_H
#include "stdint.h"
#include "stm32f4xx.h"
//////////////////////////////////////////////////////////////////////////////////	 
//All rights reserved									  
////////////////////////////////////////////////////////////////////////////////// 	
//IO��������

#define AHT10_SDA_IN()  {GPIOF->MODER&=~(3<<(10*2));GPIOF->MODER|=0<<10*2;}	//PH5����ģʽ
#define AHT10_SDA_OUT() {GPIOF->MODER&=~(3<<(10*2));GPIOF->MODER|=1<<10*2;} //PH5���ģʽ


#define AHT10_IIC_SCL_0  HAL_GPIO_WritePin(GPIOH,GPIO_PIN_15,GPIO_PIN_RESET) //SCL
#define AHT10_IIC_SCL_1  HAL_GPIO_WritePin(GPIOH,GPIO_PIN_15,GPIO_PIN_SET) //SCL

#define AHT10_IIC_SDA_0  HAL_GPIO_WritePin(GPIOF,GPIO_PIN_10,GPIO_PIN_RESET) //SDA
#define AHT10_IIC_SDA_1  HAL_GPIO_WritePin(GPIOF,GPIO_PIN_10,GPIO_PIN_SET) //SDA

#define AHT10_READ_SDA  HAL_GPIO_ReadPin(GPIOF,GPIO_PIN_10)  //����SDA
//AHT10_IIC���в�������
void AHT10_IIC_Init(void);                //��ʼ��AHT10_IIC��IO��				 
void AHT10_IIC_Start(void);				//����AHT10_IIC��ʼ�ź�
void AHT10_IIC_Stop(void);	  			//����AHT10_IICֹͣ�ź�
void AHT10_IIC_Send_Byte(uint8_t txd);			//AHT10_IIC����һ���ֽ�
uint8_t AHT10_IIC_Read_Byte(uint8_t ack);//AHT10_IIC��ȡһ���ֽ�
uint8_t AHT10_IIC_Wait_Ack(void); 				//AHT10_IIC�ȴ�ACK�ź�
void AHT10_IIC_Ack(void);					//AHT10_IIC����ACK�ź�
void AHT10_IIC_NAck(void);				//AHT10_IIC������ACK�ź�

void AHT10_IIC_Write_One_Byte(uint8_t daddr,uint8_t addr,uint8_t data);
uint8_t AHT10_IIC_Read_One_Byte(uint8_t daddr,uint8_t addr);	 
#endif


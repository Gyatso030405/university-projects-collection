#include "IIC/aht10_iic.h"
#include "DELAY/delay.h"
//////////////////////////////////////////////////////////////////////////////////	 

// STM32F429
//IIC驱动
//All rights reserved									  
////////////////////////////////////////////////////////////////////////////////// 	

//IIC初始化
void AHT10_IIC_Init(void)
{
    GPIO_InitTypeDef GPIO_Initure;
    
    __HAL_RCC_GPIOF_CLK_ENABLE();   //ʹ��GPIOFʱ��
	__HAL_RCC_GPIOH_CLK_ENABLE();   //ʹ��GPIOHʱ��
    
    //PH5,PF10��ʼ������
    GPIO_Initure.Pin=GPIO_PIN_10;
    GPIO_Initure.Mode=GPIO_MODE_OUTPUT_PP;  //�������
    GPIO_Initure.Pull=GPIO_PULLUP;          //����
    GPIO_Initure.Speed=GPIO_SPEED_FAST;     //����
    HAL_GPIO_Init(GPIOF,&GPIO_Initure);
	
	GPIO_Initure.Pin=GPIO_PIN_15;
    GPIO_Initure.Mode=GPIO_MODE_OUTPUT_PP;  //�������
    GPIO_Initure.Pull=GPIO_PULLUP;          //����
    GPIO_Initure.Speed=GPIO_SPEED_FAST;     //����
    HAL_GPIO_Init(GPIOH,&GPIO_Initure);
    
    AHT10_IIC_SDA_1;
    AHT10_IIC_SCL_1;  
}

//����AHT10_IIC��ʼ�ź�
void AHT10_IIC_Start(void)
{
	AHT10_SDA_OUT();     //sda�����
	AHT10_IIC_SDA_1;	  	  
	AHT10_IIC_SCL_1;
	delay_us(4);
 	AHT10_IIC_SDA_0;//START:when CLK is high,DATA change form high to low 
	delay_us(4);
	AHT10_IIC_SCL_0;//ǯסI2C���ߣ�׼�����ͻ�������� 
}	  
//����AHT10_IICֹͣ�ź�
void AHT10_IIC_Stop(void)
{
	AHT10_SDA_OUT();//sda�����
	AHT10_IIC_SCL_0;
	AHT10_IIC_SDA_0;//STOP:when CLK is high DATA change form low to high
 	delay_us(4);
	AHT10_IIC_SCL_1; 
	delay_us(4);			
	AHT10_IIC_SDA_1;//����I2C���߽����ź�				   	
}
//�ȴ�Ӧ���źŵ���
//����ֵ��1������Ӧ��ʧ��
//        0������Ӧ��ɹ�
uint8_t AHT10_IIC_Wait_Ack(void)
{
	uint8_t ucErrTime=0;
	AHT10_SDA_IN();      //SDA����Ϊ����  
	AHT10_IIC_SDA_1;delay_us(1);	   
	AHT10_IIC_SCL_1;delay_us(1);	 
	while(AHT10_READ_SDA)
	{
		ucErrTime++;
		if(ucErrTime>250)
		{
			AHT10_IIC_Stop();
			return 1;
		}
	}
	AHT10_IIC_SCL_0;//ʱ�����0 	   
	return 0;  
} 
//����ACKӦ��
void AHT10_IIC_Ack(void)
{
	AHT10_IIC_SCL_0;
	AHT10_SDA_OUT();
	AHT10_IIC_SDA_0;
	delay_us(2);
	AHT10_IIC_SCL_1;
	delay_us(2);
	AHT10_IIC_SCL_0;
}
//������ACKӦ��		    
void AHT10_IIC_NAck(void)
{
	AHT10_IIC_SCL_0;
	AHT10_SDA_OUT();
	AHT10_IIC_SDA_1;
	delay_us(2);
	AHT10_IIC_SCL_1;
	delay_us(2);
	AHT10_IIC_SCL_0;
}					 				     
//AHT10_IIC����һ���ֽ�
//���شӻ�����Ӧ��
//1����Ӧ��
//0����Ӧ��			  
void AHT10_IIC_Send_Byte(uint8_t txd)
{                        
    uint8_t t;   
	AHT10_SDA_OUT(); 	    
    AHT10_IIC_SCL_0;//����ʱ�ӿ�ʼ���ݴ���
    for(t=0;t<8;t++)
    {         
				if((txd&0x80)>>7 == 1)
				{
					AHT10_IIC_SDA_1;
				}
				else
				{
					AHT10_IIC_SDA_0;
				}
//        AHT10_IIC_SDA=(txd&0x80)>>7;
        txd<<=1; 	  
				delay_us(2);   //��TEA5767��������ʱ���Ǳ����
				AHT10_IIC_SCL_1;
				delay_us(2); 
				AHT10_IIC_SCL_0;	
				delay_us(2);
    }	 
} 	    
//��1���ֽڣ�ack=1ʱ������ACK��ack=0������nACK   
uint8_t AHT10_IIC_Read_Byte(uint8_t ack)
{
	uint8_t i,receive=0;
	AHT10_SDA_IN();//SDA����Ϊ����
    for(i=0;i<8;i++ )
	{
        AHT10_IIC_SCL_0; 
        delay_us(2);
		AHT10_IIC_SCL_1;
        receive<<=1;
        if(AHT10_READ_SDA)receive++;   
		delay_us(1); 
    }					 
    if (!ack)
        AHT10_IIC_NAck();//����nACK
    else
        AHT10_IIC_Ack(); //����ACK   
    return receive;
}



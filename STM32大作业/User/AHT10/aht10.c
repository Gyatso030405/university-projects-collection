#include "AHT10/aht10.h"
#include "stm32f4xx_hal.h"
#include "IIC/aht10_iic.h"
#include "DELAY/delay.h"

uint8_t aht10_command_data[3] = {0xAC,0x33,0x00};//触发测量数据
uint8_t aht10_data[10]={0};
uint8_t aht10_read_len=6;

float 	g_relative_humidity=0;
float 	g_temperature=0;


void AHT10_RST()     //软件复位
{
	AHT10_IIC_Start();/*启动总线*/
	AHT10_IIC_Send_Byte(AHT10_WRITE);
	AHT10_IIC_Send_Byte(0xba);	//软件复位
	AHT10_IIC_Stop();
}



void AHT10Init(void)
{
	AHT10_IIC_Start();
	AHT10_IIC_Send_Byte(AHT10_WRITE);
	AHT10_IIC_Send_Byte(0xe1);//初始化命令，保持主机	
	AHT10_IIC_Send_Byte(0x08);//校准使能，已校准
	AHT10_IIC_Send_Byte(0x00);//
	AHT10_IIC_Stop();	
	delay_ms(40);
}

void AHT10_Init(void)        //初始化AHT10
	{
		delay_ms(50);
		AHT10_IIC_Init();//初始化模拟IIC
		
		AHT10Init();	//初始化AHT10寄存器
		
		AHT10_IIC_Start();
		AHT10_IIC_Send_Byte(AHT10_WRITE);
		AHT10_IIC_Wait_Ack();
		AHT10_IIC_Send_Byte(0xac);//触发测量
		AHT10_IIC_Wait_Ack();
		AHT10_IIC_Send_Byte(0x33);//DATA0
		AHT10_IIC_Wait_Ack();
		AHT10_IIC_Send_Byte(0x00);//DATA1
		AHT10_IIC_Wait_Ack();
		AHT10_IIC_Stop();	  
		delay_ms(80);

	}

void AHT10_Read(void)
{

	uint32_t hr_temp = 0;
	uint32_t tem_temp =0;
	float temp=0;	
	uint8_t ack;

	AHT10_IIC_Start();
	AHT10_IIC_Send_Byte(AHT10_WRITE);//写数据
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Send_Byte(0xac);//触发测量
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Send_Byte(0x33);//DATA0
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Send_Byte(0x00);//DATA1
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Stop();	  
	delay_ms(10);
	AHT10_IIC_Start();
	AHT10_IIC_Send_Byte(AHT10_READ);//读数据
	AHT10_IIC_Wait_Ack();
	ack=AHT10_IIC_Read_Byte(1);//读取状态位
	if((ack&0x40)==0)//判断状态位，当前是否属于CMD模式
	{
		aht10_data[0]=AHT10_IIC_Read_Byte(1);//湿度数据
		aht10_data[1]=AHT10_IIC_Read_Byte(1);//湿度数据
		aht10_data[2]=AHT10_IIC_Read_Byte(1);//湿度数据，温度数据
		aht10_data[3]=AHT10_IIC_Read_Byte(1);//温度数据
		aht10_data[4]=AHT10_IIC_Read_Byte(0);//温度数据

		AHT10_IIC_Stop();
	}
	AHT10_IIC_Stop();
	
	//湿度信息转换
	hr_temp = (aht10_data[0] * 0xfff) + (aht10_data[1] * 0xf) + ((aht10_data[2])/0xf);
	temp = (float) hr_temp/0xfffff*100;
	g_relative_humidity =  temp;
	//温度信息转换
	tem_temp = (((aht10_data[2] & 0x0f) * 0xffff) + (aht10_data[3] * 0xff) + aht10_data[4]);
	temp = (float) tem_temp/0xfffff*200-50;
	g_temperature = temp;
	
}






























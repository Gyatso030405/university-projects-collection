#include "AHT10/aht10.h"
#include "stm32f4xx_hal.h"
#include "IIC/aht10_iic.h"
#include "DELAY/delay.h"

uint8_t aht10_command_data[3] = {0xAC,0x33,0x00};//������������
uint8_t aht10_data[10]={0};
uint8_t aht10_read_len=6;

float 	g_relative_humidity=0;
float 	g_temperature=0;


void AHT10_RST()     //�����λ
{
	AHT10_IIC_Start();/*��������*/
	AHT10_IIC_Send_Byte(AHT10_WRITE);
	AHT10_IIC_Send_Byte(0xba);	//�����λ
	AHT10_IIC_Stop();
}



void AHT10Init(void)
{
	AHT10_IIC_Start();
	AHT10_IIC_Send_Byte(AHT10_WRITE);
	AHT10_IIC_Send_Byte(0xe1);//��ʼ�������������	
	AHT10_IIC_Send_Byte(0x08);//У׼ʹ�ܣ���У׼
	AHT10_IIC_Send_Byte(0x00);//
	AHT10_IIC_Stop();	
	delay_ms(40);
}

void AHT10_Init(void)        //��ʼ��AHT10
	{
		delay_ms(50);
		AHT10_IIC_Init();//��ʼ��ģ��IIC
		
		AHT10Init();	//��ʼ��AHT10�Ĵ���
		
		AHT10_IIC_Start();
		AHT10_IIC_Send_Byte(AHT10_WRITE);
		AHT10_IIC_Wait_Ack();
		AHT10_IIC_Send_Byte(0xac);//��������
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
	AHT10_IIC_Send_Byte(AHT10_WRITE);//д����
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Send_Byte(0xac);//��������
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Send_Byte(0x33);//DATA0
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Send_Byte(0x00);//DATA1
	AHT10_IIC_Wait_Ack();
	AHT10_IIC_Stop();	  
	delay_ms(10);
	AHT10_IIC_Start();
	AHT10_IIC_Send_Byte(AHT10_READ);//������
	AHT10_IIC_Wait_Ack();
	ack=AHT10_IIC_Read_Byte(1);//��ȡ״̬λ
	if((ack&0x40)==0)//�ж�״̬λ����ǰ�Ƿ�����CMDģʽ
	{
		aht10_data[0]=AHT10_IIC_Read_Byte(1);//ʪ������
		aht10_data[1]=AHT10_IIC_Read_Byte(1);//ʪ������
		aht10_data[2]=AHT10_IIC_Read_Byte(1);//ʪ�����ݣ��¶�����
		aht10_data[3]=AHT10_IIC_Read_Byte(1);//�¶�����
		aht10_data[4]=AHT10_IIC_Read_Byte(0);//�¶�����

		AHT10_IIC_Stop();
	}
	AHT10_IIC_Stop();
	
	//ʪ����Ϣת��
	hr_temp = (aht10_data[0] * 0xfff) + (aht10_data[1] * 0xf) + ((aht10_data[2])/0xf);
	temp = (float) hr_temp/0xfffff*100;
	g_relative_humidity =  temp;
	//�¶���Ϣת��
	tem_temp = (((aht10_data[2] & 0x0f) * 0xffff) + (aht10_data[3] * 0xff) + aht10_data[4]);
	temp = (float) tem_temp/0xfffff*200-50;
	g_temperature = temp;
	
}






























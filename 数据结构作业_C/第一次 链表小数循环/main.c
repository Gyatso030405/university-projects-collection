#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct node
{
    int   data;
    struct node * next;
} NODE;


NODE * find(NODE*,int *);
void outputring(NODE *);
void change(int,int,NODE *);
void outputring( NODE * pring )
{
    NODE * p;
	p=pring;
	if(p==NULL)
           printf("NULL");
	else
           do{
                printf("%d", p->data);
                p = p->next;
            }while ( p != pring );
	printf("\n");
	return;
}



int p1 = 0, p2 = 0;
void change(int n,int m,NODE *head ){   //��ʼ��
    int shang[10010], yushu[10010];
    memset(shang, 0, sizeof(shang));
    memset(yushu, 0, sizeof(yushu));
    p1=0,p2=0;
    int flag=0;
    int num=n*10;
    for(int i=0; ;i++){
       shang[i]=num/m;
       yushu[i]=num%m;
       for(int j=0;j<i;j++){    /* ���̺�������֮ǰ��ͬʱ������־�ų���ѭ��
                                   ��p1��p2��¼λ�ã�flag=1��ʾ����ѭ�� */
           if(shang[j]==shang[i]&&yushu[j]==yushu[i]){
                p1=j;
                p2=i;
                flag=1;
                break;
           }
    	}
    	num=yushu[i]*10;
        if(!num){     //���num����������Ϊ0����û��ѭ��
           p1 = i + 1;
           break;
    	}
    	if(flag == 1){
           break;
    	}
    }
    /*���� p1 ��λ�ã����û��ѭ����������������
    	�����ѭ������������ǰ׺�� */
    NODE *r=head;
    for(int i=0;i<p1;i++)
    {
    	//β�巨��������
    	NODE *q=(NODE*)malloc(sizeof(NODE));
    	q->data=shang[i];
    	q->next=NULL;
    	r->next=q;
    	r=q;
    }

    //����ѭ��
    if(flag==1)
    {
    	NODE *r_save=r;
    	for(int i=p1;i<p2;i++)
    	{
           NODE *q=(NODE*)malloc(sizeof(NODE));
           q->data=shang[i];
           q->next=NULL;
           r->next=q;
           r=q;
    	}
    	r->next=r_save->next;
    }
}

NODE* find(NODE *head,int *n)
{
    if(p2>p1)//����ѭ��
    {
        NODE *p=head->next;//��ʼ��
         //���㳤��
        *n=p2-p1;
        //Խ��ǰ׺
        for(int i=0;i<p1;i++)
        {
            p=p->next;
        }
        return p;
	}
    else//������ѭ��
    {
        *n = 0;
        return NULL;
     }
}
int main()
{
    int M, N;
	NODE *head,*pring;

        printf("�������M�ͷ�ĸN(M<N)��\n");
        printf("M:\n");
        scanf("%d",&M);
        printf("N:\n");
        scanf("%d",&N);

        if(M>=N){printf("�������:\n");}
        else{
	head =(NODE *)malloc(sizeof(NODE));
	head->next=NULL;
	head->data=-1;

	change( M,N,head);
	pring = find(head,&M);
	printf("ѭ�����ĳ���Ϊ=%d\n",M);
	printf("ѭ������Ϊ��\n");
	outputring(pring);
        }
        system("pause");
	return 0;
}


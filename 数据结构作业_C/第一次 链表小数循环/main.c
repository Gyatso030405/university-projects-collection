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
void change(int n,int m,NODE *head ){   //初始化
    int shang[10010], yushu[10010];
    memset(shang, 0, sizeof(shang));
    memset(yushu, 0, sizeof(yushu));
    p1=0,p2=0;
    int flag=0;
    int num=n*10;
    for(int i=0; ;i++){
       shang[i]=num/m;
       yushu[i]=num%m;
       for(int j=0;j<i;j++){    /* 当商和余数与之前相同时，即标志着出现循环
                                   用p1、p2记录位置，flag=1表示存在循环 */
           if(shang[j]==shang[i]&&yushu[j]==yushu[i]){
                p1=j;
                p2=i;
                flag=1;
                break;
           }
    	}
    	num=yushu[i]*10;
        if(!num){     //如果num被除尽，变为0，则没有循环
           p1 = i + 1;
           break;
    	}
    	if(flag == 1){
           break;
    	}
    }
    /*根据 p1 的位置，如果没有循环，则建立完整链表；
    	如果有循环，则建立的是前缀。 */
    NODE *r=head;
    for(int i=0;i<p1;i++)
    {
    	//尾插法建立链表
    	NODE *q=(NODE*)malloc(sizeof(NODE));
    	q->data=shang[i];
    	q->next=NULL;
    	r->next=q;
    	r=q;
    }

    //补上循环
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
    if(p2>p1)//存在循环
    {
        NODE *p=head->next;//初始化
         //计算长度
        *n=p2-p1;
        //越过前缀
        for(int i=0;i<p1;i++)
        {
            p=p->next;
        }
        return p;
	}
    else//不存在循环
    {
        *n = 0;
        return NULL;
     }
}
int main()
{
    int M, N;
	NODE *head,*pring;

        printf("输入分子M和分母N(M<N)：\n");
        printf("M:\n");
        scanf("%d",&M);
        printf("N:\n");
        scanf("%d",&N);

        if(M>=N){printf("输入错误:\n");}
        else{
	head =(NODE *)malloc(sizeof(NODE));
	head->next=NULL;
	head->data=-1;

	change( M,N,head);
	pring = find(head,&M);
	printf("循环数的长度为=%d\n",M);
	printf("循环部分为：\n");
	outputring(pring);
        }
        system("pause");
	return 0;
}


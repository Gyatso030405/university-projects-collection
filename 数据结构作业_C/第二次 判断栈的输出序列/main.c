
#include <stdio.h>
#include <stdlib.h>
#define   MAXSIZE  1000   //定义栈中元素个数的最大值

typedef  struct{
          int data[MAXSIZE];
          int top;
 }SqStack;

 void InitStack(SqStack* S)
 {
     S->top=-1;     //初始化

 }

 _Bool StackEmpty(SqStack* S)
 {
     if(S->top==-1)
     {
         return 0;  //栈空
     }
     else{
        return 1;
     }
 }

 //插入e作为新的栈顶元素
 _Bool Push(SqStack* S, int e)
 {
     if(S->top==MAXSIZE-1){
        return 1;
     }
     S->top++;
     S->data[S->top]=e;  //将新插入元素赋值给栈顶空间
     return 0;
 }

 //若栈不空，则删除S的栈顶元素，用e返回其值，并返回OK，否则返回ERROR
 _Bool Pop(SqStack* S, int* e)
 {
     if(S->top==-1){
        return 1;
     }
     *e=S->data[S->top];  //将要删除的栈顶元素赋值给e
     S->top--;
     return 0;
 }



int main()
{
    SqStack* A=(SqStack*)malloc(sizeof(SqStack));
    InitStack(A);
    int n;
    int k=0;
    int k1=0;
    int flag=0;
    int tem[20];
    int tem1[20];
    int e=0;
    printf("输入元素个数n：\n");
    scanf_s("%d",&n);
    printf("依次输入入栈元素：\n");
    for(int i=0;i<n;i++)
    {

        scanf_s("%d",&tem[i]);  //入栈
    }
     printf("依次输入出栈元素：\n");
    for(int i=0;i<n;i++)
    {

        scanf_s("%d",&tem1[i]);  //出栈
    }
    for(k;k<n;k++)
    {
        Push(A, tem[k]);//输入序列一个个入栈
        while(A->data[A->top]==tem1[k1])
        {
            Pop(A, &e);
            k1++;
        }
    }
    if(StackEmpty(A))
    {
        flag=1;
    }
    if(flag==0)
    {
        printf("是正确输出序列\n");
    }else{
        printf("不是正确输出序列\n");
    }
    system("pause");
    return 0;
}

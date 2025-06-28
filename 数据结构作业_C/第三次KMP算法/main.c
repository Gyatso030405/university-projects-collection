#include <stdio.h>
#include <stdlib.h>
#define maxsize  100

void Nextval(char T[],int *next)
{
    int lenT=strlen(T);
    int k=-1;  //前缀
    int j=0;   //后缀
    next[0]=-1;

    while(j<lenT)
    {
        if(k==-1||T[j]==T[k])
        {
            j++;
            k++;
            if(T[j]!=T[k]) //优化next从而省掉重复匹配的现象
            {
                next[j]=k;
            }
            else
            {
                next[j]=next[k];
            }
        }
        else
        {
            k=next[k];
        }
    }
}

int KMP(char S[],char T[])
{
      int i=0,j=0,lenS,lenT;
      lenS=strlen(S);
      lenT=strlen(T);

      int next[maxsize];
      Nextval(T,next);

      while(i<lenS&&j<lenT){
          if(j==-1||S[i]==T[j]) //匹配过程
          {
                i++;
                j++;
          }
          else{
                j=next[j];  //j进行回溯，调用nextval的结果
          }
      }
     if(j==lenT)
      {
          printf("匹配成功！\n");
          return i-j;
      }
      else{
          printf("匹配失败！\n");
          return -1;
      }
}


int main()
{
    char S[maxsize],T[maxsize];
    int target;

    printf("输入主串S\n");
    scanf_s("%s",S);
    printf("输入模式串T\n");
    scanf_s("%s",T);

    target=KMP(S,T);

    printf("匹配位置是：%d\n",target);
    system("pause");
    return 0;
}

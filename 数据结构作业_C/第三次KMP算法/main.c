#include <stdio.h>
#include <stdlib.h>
#define maxsize  100

void Nextval(char T[],int *next)
{
    int lenT=strlen(T);
    int k=-1;  //ǰ׺
    int j=0;   //��׺
    next[0]=-1;

    while(j<lenT)
    {
        if(k==-1||T[j]==T[k])
        {
            j++;
            k++;
            if(T[j]!=T[k]) //�Ż�next�Ӷ�ʡ���ظ�ƥ�������
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
          if(j==-1||S[i]==T[j]) //ƥ�����
          {
                i++;
                j++;
          }
          else{
                j=next[j];  //j���л��ݣ�����nextval�Ľ��
          }
      }
     if(j==lenT)
      {
          printf("ƥ��ɹ���\n");
          return i-j;
      }
      else{
          printf("ƥ��ʧ�ܣ�\n");
          return -1;
      }
}


int main()
{
    char S[maxsize],T[maxsize];
    int target;

    printf("��������S\n");
    scanf_s("%s",S);
    printf("����ģʽ��T\n");
    scanf_s("%s",T);

    target=KMP(S,T);

    printf("ƥ��λ���ǣ�%d\n",target);
    system("pause");
    return 0;
}

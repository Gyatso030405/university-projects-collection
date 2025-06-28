#include<stdio.h>
#define maxleaf 20//���Ҷ����Ŀ
#define maxnode maxleaf*2-1//�������
#define maxval 10000
#define maxsize  100//��������������λ��
typedef struct
{
 char ch;
 float weight;
 int lchild,rchild,parent;
}hufmtree;
typedef struct
{
 char bits[maxsize];//λ��
 int start;      //������λ���е���ʼλ��
 char ch;        //�ַ�
}codetype;
//huffman
void huffman(hufmtree tree[],int n)//������������
{
 int i,j,p1,p2;//p1,p2�ֱ��סÿ�κϲ�ʱȨֵ��С�ʹ�С�������������±�
 float small1,small2,f;
 char c;
 int m = 2*n-1;
 for(i=0;i<m;i++)    //��ʼ��
 {
  tree[i].parent=0;
  tree[i].lchild=-1;
  tree[i].rchild=-1;
  tree[i].weight=0;
 }
 for(i=0;i<n;i++)  //����ǰn�������ַ���Ȩֵ
 {
  printf("��%d��Ԫ�ص�=>\n",i+1);
  printf("\t���ֵ:");
  scanf("%c",&c);
  getchar();
  printf("\tȨ��:");
  scanf("%f",&f);
  getchar();
  tree[i].ch=c;
  tree[i].weight=f;
 }
  for(i=n;i<m;i++)      //����n-1�κϲ�������n-1���½��
 {
  p1=0;p2=0;
  small1=maxval;small2=maxval;   //maxval��float���͵����ֵ
  for(j=0;j<i;j++)    //ѡ������Ȩֵ��С�ĸ����
   if(tree[j].parent==0)
    if(tree[j].weight<small1)
    {
     small2=small1;  //�ı���СȨ����СȨ����Ӧ��λ��
     small1=tree[j].weight;
     p2=p1;
     p1=j;
    }
    else if(tree[j].weight<small2)
    {
     small2=tree[j].weight;  //�ı��СȨ��λ��
     p2=j;
    }
  tree[p1].parent=i;
  tree[p2].parent=i;
  tree[i].lchild=p1;  //��СȨ��������½�������
  tree[i].rchild=p2;  //��СȨ��������½����Һ���
  tree[i].weight=tree[p1].weight+tree[p2].weight;
 }
}
//huffmancode
void huffmancode(codetype code[],hufmtree tree[],int n)//���ݹ��������������������
{
 int i,c,p;
 codetype cd;   //�������
 for(i=0;i<n;i++)
 {
  cd.start=n;
  cd.ch=tree[i].ch;
  c=i;       //��Ҷ���������ϻ���
  p=tree[i].parent;   //tree[p]��tree[i]��˫��
  while(p!=0)
  {
   cd.start--;
   if(tree[p].lchild==c)
    cd.bits[cd.start]='0';   //tree[i]�������������ɴ���'0'
   else
    cd.bits[cd.start]='1';   //tree[i]�������������ɴ���'1'
   c=p;
   p=tree[p].parent;
  }
  code[i]=cd;    //��i+1���ַ��ı������code[i]
 }
}
//decode
void decode(hufmtree tree[],int m)//���ζ�����ģ����ݹ�����������
{
 int i,j=0,k=0;
 char b[maxsize];
 char endflag='#';    //���Ľ�����־ȡ2
 i=m-1;             //�Ӹ���㿪ʼ��������
 getchar();
 gets(b);
 printf("������������룺\n");
 while(b[j]!='#')
 {
  if(b[j]=='0')
   i=tree[i].lchild;   //��������
  else
   i=tree[i].rchild;   //�����Һ���
  if(tree[i].lchild==-1)     //tree[i]��Ҷ���
  {
   printf("%c",tree[i].ch);
   i=m-1;      //�ص������
  }
  j++;
 }
 printf("\n");
 if(tree[i].lchild!=-1&&b[j]!='#')   //���Ķ��꣬����δ��Ҷ�ӽ��
  printf("\nERROR\n");  //��������д�
}
//������--�������
int main()
{
 int i,j,n,m;
 int choose;
 hufmtree tree[maxnode];
 codetype code[maxleaf];
 while(1){
  printf(" ��ѡ����Ҫʵ�ֵĹ��ܣ�������1-4���֣�\n");
  printf("  1---������������\n");
  printf("  2---����\n");
  printf("  3---����\n");
  printf("  4---�˳�\n");
  scanf("%d",&choose);
  switch(choose){
  case 1:
   printf("������Ԫ�ظ�����");
   scanf("%d",&n);
   getchar();
   huffman(tree,n);//������������
   printf("���������ѳɹ�������\n");
   break;
     case 2:
   printf("������������룺\n");
   huffmancode(code,tree,n);//���ݹ��������������������
   for(i=0;i<n;i++)
   {
    printf("%c: ",code[i].ch);
    for(j=code[i].start;j<n;j++)
     printf("%c",code[i].bits[j]);
    printf("\n");
   }
   break;
  case 3:
   m=2*n-1;
   printf("��������ģ�0 or 1��,��#Ϊ������־��\n");
   decode(tree,m);//���ζ�����ģ����ݹ�����������
   break;
  case 4:
   return 0;
  }
 }
 return 0;
}

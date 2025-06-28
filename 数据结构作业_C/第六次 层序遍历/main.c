#include <stdio.h>
#include <stdlib.h>
#define MAX_SIZE 30

typedef struct Node
{    int data;
	 struct Node* lchild, * rchild;
} BiNode, *BiTree;
typedef struct Queue
{
	 int front, rear;
	 BiNode* data[MAX_SIZE];
} Queue;// ���ö��е���ʽ���в������

     BiNode* buildBiTree(int preOrder[], int inOrder[], int n) {    //����������
		 if (preOrder == NULL || inOrder == NULL || n <= 0)
		 {
			 return NULL;
		 }
		 int root = preOrder[0];
		 BiNode* BiTreeRoot = (BiNode*)malloc(sizeof(BiNode));
		 BiTreeRoot->data = root;
		 int i;
		 for (i = 0; i < n; ++i)
		 {
			 if (inOrder[i] == root)
			 {
				 break;
			 }
		 }
		 BiTreeRoot->lchild = buildBiTree(preOrder + 1, inOrder, i);
		 BiTreeRoot->rchild = buildBiTree(preOrder + i + 1, inOrder + i + 1, n - i - 1);
		 return BiTreeRoot;
	 }

	 void levelOrder(BiTree BiTreeRoot) //�������
	 {
		 if (BiTreeRoot == NULL)
		 {
			 return;
		 }
		 BiNode* current = NULL;
		 Queue* queue = (Queue*)malloc(sizeof(Queue));
		 queue->front = queue->rear = -1;
		 queue->data[++queue->rear] = BiTreeRoot;
		 printf("�������α������ַ�����\n");
		 while (queue->front != queue->rear)
		 {
			 current = queue->data[++queue->front];
			 if (queue->front == 0)
			 {
				 printf("%d", current->data);
			 }
			 else
			 {
				 printf(" %d", current->data);
			 }
			 if (current->lchild != NULL)
			 {
				 queue->data[++queue->rear] = current->lchild;
			 }
			 if (current->rchild != NULL)
			 {
				 queue->data[++queue->rear] = current->rchild;
			 }
		 }
		 free(queue);
		 return;
	 }
	 int main()
	 {
		 int n;
		 printf("�����ַ������ȣ�\n");
		 scanf("%d", &n);
		 int preOrderx[MAX_SIZE] = {0}, inOrderx[MAX_SIZE] = {0};
		 printf("����ǰ������ַ�����\n");
		 for (int i = 0; i < n; ++i)
		 {
			 scanf("%d", &preOrderx[i]);
		 }
		 printf("������������ַ�����\n");
		 for (int i = 0; i < n; ++i)
		 {
			 scanf("%d", &inOrderx[i]);
		 }
		 BiNode* BiTreeRoot = buildBiTree(preOrderx, inOrderx, n);
		 levelOrder(BiTreeRoot);
		 return 0;
	 }


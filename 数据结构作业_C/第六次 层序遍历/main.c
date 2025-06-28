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
} Queue;// 利用队列的形式进行层序遍历

     BiNode* buildBiTree(int preOrder[], int inOrder[], int n) {    //构建二叉树
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

	 void levelOrder(BiTree BiTreeRoot) //层序遍历
	 {
		 if (BiTreeRoot == NULL)
		 {
			 return;
		 }
		 BiNode* current = NULL;
		 Queue* queue = (Queue*)malloc(sizeof(Queue));
		 queue->front = queue->rear = -1;
		 queue->data[++queue->rear] = BiTreeRoot;
		 printf("输出按层次遍历的字符串：\n");
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
		 printf("输入字符串长度：\n");
		 scanf("%d", &n);
		 int preOrderx[MAX_SIZE] = {0}, inOrderx[MAX_SIZE] = {0};
		 printf("输入前序遍历字符串：\n");
		 for (int i = 0; i < n; ++i)
		 {
			 scanf("%d", &preOrderx[i]);
		 }
		 printf("输入中序遍历字符串：\n");
		 for (int i = 0; i < n; ++i)
		 {
			 scanf("%d", &inOrderx[i]);
		 }
		 BiNode* BiTreeRoot = buildBiTree(preOrderx, inOrderx, n);
		 levelOrder(BiTreeRoot);
		 return 0;
	 }


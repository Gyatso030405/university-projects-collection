#include<stdio.h>
#include<string.h>
#include<stdlib.h>

struct LNode{
	int num;
	struct LNode *next;
};

//创建新链表
struct LNode* create(){
	int x,y,i;
	struct LNode *s;
	struct LNode *l;
	struct LNode *p;
	l=(struct LNode*)malloc(sizeof(struct LNode));
	l->num=0;
	l->next=NULL;
	p=l;
	printf("请输入表的元素个数\n");
	scanf("%d",&x);
	printf("\n");
	for(i=1;i<=x;i++){
		printf("请输入第%d个元素\n",i);
		scanf("%d",&y);
		s=(struct LNode*)malloc(sizeof(struct LNode));
		s->num=y;
		p->next=s;
		p=s;
	}
	s->next=NULL;
	return l;
	/*while(l){
    struct LNode *temp = l;
    l = l->next;
    free(temp);
}*/
}

void print(struct LNode*l){
	int a;
	struct LNode*p=l->next;
	if(p==NULL) {printf("所得链表A为空！\n");}
	else{
	printf("输出链表A：\n");
	while(p!=NULL){
		a=p->num;
		printf("%d\n",a);
		p=p->next;
	}
	}
}


void common(struct LNode*L1,struct LNode*L2,struct LNode*L3){
	struct LNode*p1=L1->next;
	struct LNode*p2=L2->next;
	struct LNode*p3=L3->next;
	struct LNode*p4=L1;
	int x=0;
	while(p1!=NULL&&p2!=NULL&&p3!=NULL){
		if(p1->num>p2->num){
			if(p2->next==NULL) break;
			while(p1->num>p2->num&&p2!=NULL){
				p2=p2->next;
			}
		}
        if(p1->num>p3->num){
			if(p3->next==NULL) break;
			while(p1->num>p3->num){
				p3=p3->next;
			}
		}
       if(p1->num<p2->num||p1->num<p3->num){
	    struct LNode*q=p1;
			p1=p1->next;
			p4->next=p4->next->next;
			free(q);
		}
        if(p1->next==NULL) break;
        if(p1->num==p2->num&&p1->num==p3->num){
			if(p1->next==NULL){
				x=1;
				break;
			}
			if(p1->num==p1->next->num){
				while(p1->num==p1->next->num){
			        struct LNode*q=p1;
			        p1=p1->next;
			        p4->next=p4->next->next;
			        free(q);
			        if(p1->next==NULL){
				        x=1;
				        break;
			        }
			    }
			}
			p1=p1->next;
		    p2=p2->next;
		    p3=p3->next;
		    p4=p4->next;
		}
	}

	if(p1!=NULL&&x==0){
		while(p1!=NULL){
			struct LNode*q=p1;
			p1=p1->next;
			p4->next=p4->next->next;
			free(q);
		}
	}
}

int main(){
	printf("请输入表a\n\n");
	struct LNode *L1=create();
	printf("请输入表b\n\n");
	struct LNode *L2=create();
	printf("请输入表c\n\n");
	struct LNode *L3=create();

	common(L1,L2,L3);

	print(L1);
	return 0;
}

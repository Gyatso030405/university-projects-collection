#include <stdio.h>
#include <stdlib.h>
#define  MAX_VERTEX_NUM 20   //最大顶点个数
#define  VertexType int      //顶点数据的类型
typedef enum
{
    false,true
} bool;

//建立全局变量，保存边的最早开始时间
VertexType ve[MAX_VERTEX_NUM];

//建立全局变量，保存边的最晚开始时间
VertexType vl[MAX_VERTEX_NUM];
typedef struct ArcNode
{
    int adjvex;                //邻接点在数组中的位置下标
    struct ArcNode * nextarc; //指向下一个邻接点的指针
    VertexType dut;
}ArcNode;

typedef struct VNode
{
    VertexType data;//顶点的数据域
    ArcNode * firstarc;//指向邻接点的指针
}VNode,AdjList[MAX_VERTEX_NUM];//存储各链表头结点的数组

typedef struct
{
    AdjList vertices;//图中顶点及各邻接点数组
    int vexnum,arcnum;//记录图中顶点数和边或弧数
}ALGraph;

//找到顶点对应在邻接表数组中的位置下标
int LocateVex(ALGraph G,VertexType u){
    for (int i=0; i<G.vexnum; i++) {
        if (G.vertices[i].data==u) {
            return i;
        }
    }
    return -1;
}
//创建AOE网，构建邻接表
void CreateAOE(ALGraph **G){
    *G=(ALGraph*)malloc(sizeof(ALGraph));

    printf("请输入顶点个数：\n");
    scanf("%d",&((*G)->vexnum));
    printf("请输入有向边的个数：\n");
    scanf("%d",&((*G)->arcnum));
     printf("依次输入每个顶点的值：\n");
    for (int i=0; i<(*G)->vexnum; i++)
    {

        scanf("%d",&((*G)->vertices[i].data));
        (*G)->vertices[i].firstarc=NULL;
    }
    VertexType initial,end,dut;

    printf("分别输入边的起始顶点，末顶点，边的权值:\n");
    for (int i=0; i<(*G)->arcnum; i++)
    {

        scanf("%d,%d,%d",&initial,&end,&dut);

        ArcNode *p=(ArcNode*)malloc(sizeof(ArcNode));
        p->adjvex=LocateVex(*(*G), end);
        p->nextarc=NULL;
        p->dut=dut;

        int locate=LocateVex(*(*G), initial);
        p->nextarc=(*G)->vertices[locate].firstarc;
        (*G)->vertices[locate].firstarc=p;
    }
}
//结构体定义栈结构
typedef struct stack{
    VertexType data;
    struct stack * next;
}stack;

stack *T;

//初始化栈结构
void initStack(stack* *S){
    (*S)=(stack*)malloc(sizeof(stack));
    (*S)->next=NULL;
}
//判断栈是否为空
bool StackEmpty(stack S){
    if (S.next==NULL) {
        return true;
    }
    return false;
}
//进栈，以头插法将新结点插入到链表中
void push(stack *S,VertexType u){
    stack *p=(stack*)malloc(sizeof(stack));
    p->data=u;
    p->next=NULL;
    p->next=S->next;
    S->next=p;
}
//弹栈函数，删除链表首元结点的同时，释放该空间，并将该结点中的数据域通过地址传值给变量i;
void pop(stack *S,VertexType *i){
    stack *p=S->next;
    *i=p->data;
    S->next=S->next->next;
    free(p);
}
//统计各顶点的入度
void FindInDegree(ALGraph G,int indegree[]){
    //初始化数组，默认初始值全部为0
    for (int i=0; i<G.vexnum; i++) {
        indegree[i]=0;
    }
    //遍历邻接表，根据各链表中结点的数据域存储的各顶点位置下标，在indegree数组相应位置+1
    for (int i=0; i<G.vexnum; i++) {
        ArcNode *p=G.vertices[i].firstarc;
        while (p) {
            indegree[p->adjvex]++;
            p=p->nextarc;
        }
    }
}

bool TopologicalOrder(ALGraph G){
    int indegree[G.vexnum];//创建记录各顶点入度的数组
    FindInDegree(G,indegree);//统计各顶点的入度
    //建立栈结构，程序中使用的是链表
    stack *S;
    //初始化栈
    initStack(&S);
    for (int i=0; i<G.vexnum; i++) {
        ve[i]=0;
    }
    //查找度为0的顶点，作为起始点
    for (int i=0; i<G.vexnum; i++) {
        if (!indegree[i]) {
            push(S, i);
        }
    }
    int count=0;
    //栈为空为结束标志
    while (!StackEmpty(*S)) {
        int index;
        //弹栈，并记录栈中保存的顶点所在邻接表数组中的位置
        pop(S,&index);
        //压栈，为求各边的最晚开始时间做准备
        push(T, index);
        ++count;
        //依次查找跟该顶点相链接的顶点，如果初始入度为1，当删除前一个顶点后，该顶点入度为0
        for (ArcNode *p=G.vertices[index].firstarc; p ; p=p->nextarc) {
              VertexType k=p->adjvex;
             if (!(--indegree[k])) {
                //顶点入度为0，入栈
                push(S, k);
            }
            /*如果边的源点的最长路径长度加上边的权值比汇点的最长路径长度还长，
            就覆盖ve数组中对应位置的值，最终结束时，ve数组中存储的就是各顶点的最长路径长度。*/
            if (ve[index]+p->dut>ve[k]) {
                ve[k]=ve[index]+p->dut;
            }
        }
    }
    //如果count值小于顶点数量，表明有向图有环
    if (count<G.vexnum) {
        printf("该图有回路");
        return false;
    }
    return true;
}
//求各顶点的最晚发生时间并计算出各边的最早和最晚开始时间
void CriticalPath(ALGraph G){
    if (!TopologicalOrder(G)) {
        return ;
    }
    for (int i=0 ; i<G.vexnum ; i++) {
        vl[i]=ve[G.vexnum-1];
    }
    int j,k;
    int count=0;
    while (!StackEmpty(*T)) {
        pop(T, &j);
        for (ArcNode* p=G.vertices[j].firstarc ; p ; p=p->nextarc) {
            k=p->adjvex;
            //构建Vl数组，在初始化时，如果每个边的汇点-边的权值比源点值小，就保存更小的。
            if (vl[k]-p->dut<vl[j]) {
                vl[j] = vl[k]-p->dut;
            }
        }
    }
    printf("输出关键路径的各权值：\n");
    for (j = 0; j < G.vexnum; j++) {
        for (ArcNode*p = G.vertices[j].firstarc; p ;p = p->nextarc) {
            k = p->adjvex;
            //求各边的最早开始时间e[i],等于ve数组中相应源点存储的值
            int ee = ve[j];
            //求各边的最晚开始时间l[i]，等于汇点在vl数组中存储的值减改边的权值
            int el = vl[k]-p->dut;
            if(ee==el)
                printf("%3d",p->dut);
        }
    }
}
int main(){
    ALGraph *G;
    CreateAOE(&G);//创建AOE网
    initStack(&T);
    TopologicalOrder(*G);
    CriticalPath(*G);
    return  0;
}

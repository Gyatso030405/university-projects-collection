#include<graphics.h>
#include<stdio.h>

#define NUM 40 //ը���ĸ���

int mapbomb[20][20];//ը����ͼ��0-8��ʾ��Χը��������9��ʾ��λ��Ϊը��
int showmap[20][20];//��ʾ��ǰ����״̬��0��δ������1�Ƿ�����2�ǲ���

int life,isnew;
PIMAGE BOMB;//ը��
PIMAGE SHOW_0;//δ���������̸�
PIMAGE SHOW_1;//�ѷ��������̸�
PIMAGE SHOW_FLAG;//����

int innitmap(int num);//��ʼ������
int place_png();//����ͼ��
int response();//��Ӧ������
void show_other(int x,int y);//�����հ׷����Ա߰��ŵĿհ׷���


int main ()
{
    int x,y;

    initgraph(600,660);//��ʼ����ͼ����

    BOMB=newimage();
    SHOW_0=newimage();
    SHOW_1=newimage();
    SHOW_FLAG=newimage();

    getimage(BOMB,"bomb.png");
    getimage(SHOW_0,"show_0.png");
    getimage(SHOW_1,"show_1.png");
    getimage(SHOW_FLAG,"show_flag.png");

    setfillcolor(WHITE);

    while(1)
    {
        bar(80,600,600,700);
        setcolor(YELLOW);
        setfont(50,0,"����");
        setfont(20,0,"����");
        xyprintf(80,610,"����������Ҽ�����");

        life=1;
        isnew=1;
        innitmap(NUM);//������40��ը��������
        for(y=0; y<20; y++)
            for(x=0; x<20; x++)
                showmap[y][x]=0;//��ʼ��20*20����
        setbkcolor(WHITE);

        place_png();

        while(life)
        {
            response();
            if(life==0)
            {
                for(y=0; y<20; y++)
                    for(x=0; x<20; x++)
                        showmap[y][x]=1;
                place_png();
                break;
            }
            if(isnew)
                place_png();
            if(life==2)
                break;
        }
        setfont(30,0,"����");
        bar(80,600,600,700);
        if(life==2)
            xyprintf(80,600,"WIN!");
        if(life==0)
            xyprintf(80,600,"LOSE!");
        setfont(20,0,"����");
        xyprintf(80,630,"(���ո����¿�ʼ���������˳�)");
        if(getch()!=VK_SPACE)
            break;

    }

    delimage(SHOW_1);
    delimage(SHOW_0);
    delimage(BOMB);

    closegraph();
}



int innitmap(int num)
{
    int x,y,n=0;
    int i,j;
    for(y=0; y<20; y++)
        for(x=0; x<20; x++)
            mapbomb[y][x]=0;//��ʼ��
    for(; n<num;)
    {
        n=0;
        x=rand()%20;
        y=rand()%20;
        mapbomb[y][x]=9;//�����ը��
        for(y=0; y<20; y++)
            for(x=0; x<20; x++)
            {
                if(mapbomb[y][x]==9)
                    n++;
            }
    }

    for(y=0; y<20; y++)
        for(x=0; x<20; x++)
        {
            if(mapbomb[y][x]!=9)
                for(i=y-1; i<=y+1; i++)
                    for(j=x-1; j<=x+1; j++)
                    {
                        if(i>=0&&i<20&&j>=0&&j<20)
                            if(mapbomb[i][j]==9)
                                mapbomb[y][x]++;//ը����Χ�����ּ�һ
                    }
        }
    return 0;
}


int place_png()
{
    int x,y;
    for(y=0; y<20; y++)
        for(x=0; x<20; x++)
        {
            if(showmap[y][x]==1)
            {
                if(mapbomb[y][x]==9)
                    putimage(x*30,y*30,BOMB);//9����ǰ��Ϊը��
                else
                {
                    putimage(x*30,y*30,SHOW_1);//����ը���򷭿���ǰ��
                    if(mapbomb[y][x]!=0)
                    {
                        if(mapbomb[y][x]==1)
                            setcolor(BLUE);//��ɫ1
                        else if(mapbomb[y][x]==2)
                            setcolor(GREEN);//��ɫ2
                        else if(mapbomb[y][x]<6)
                            setcolor(RED);//����2��Ϊ��
                        else
                            setcolor(RED);
                        setfont(-25,0,"����");
                        xyprintf(x*30+10,y*30+3,"%d",mapbomb[y][x]);
                    }
                }
            }

            else if (showmap[y][x]==2)
                putimage(x*30,y*30,SHOW_FLAG);
            else
                putimage(x*30,y*30,SHOW_0);
        }
    isnew =0;
}



int response()
{
    int x,y,n=0;
    mouse_msg mous;
    if(mousemsg()) mous= getmouse();

    x=(int)(mous.x/30);
    y=(int)(mous.y/30);

    if(mous.is_up())
    {
        if(mous.x<600)
        {
            if(mous.is_left())
                show_other(x,y);
            if(mous.is_right())
            {
                if(showmap[y][x]==0)
                    showmap[y][x]=2;
                else if(showmap[y][x]==2)
                    showmap[y][x]=0;
            }
            isnew =1;
        }
    }

    for(y=0; y<20; y++)
        for(x=0; x<20; x++)
        {
            if(showmap[y][x]==2)
                if(mapbomb[y][x]==9)
                    n++;
        }

    if(n==NUM)
        life=2;
}



void show_other(int x,int y)
{
    int i,j;
    showmap[y][x]=1;

    if(mapbomb[y][x]==9)
    {
        life=0;
        return;
    }
    if(mapbomb[y][x]==0)
    {
        for(i=y-1; i<=y+1; i++)
            for(j=x-1; j<=x+1; j++)
            {
                if(i>=0 && i<20 && j>=0 && j<20)
                    if(showmap[i][j]==0)
                    {
                        showmap[i][j]==1;
                        if(showmap[i][j]==0)
                            show_other(j,i);
                    }
            }
    }
}

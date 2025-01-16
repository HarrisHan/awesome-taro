 % a=str2num(char(a));
% d=str2num(char(d));
% 导入航班对停机位数据表
clear all;close all;
flight_gateData = readtable('newdata.xlsx', 'Sheet', 'Sheet1');

% 提取进港时间（进港时间列从482开始）
a = num2cell(flight_gateData.arrive); % 替换 YourArrivalTimeColumn 为实际列名

% 提取离港时间（离港时间列从595开始）
d = num2cell(flight_gateData.leave); % 替换 YourDepartureTimeColumn 为实际列名

% 提取航班机型
fi = flight_gateData.fshape; % 替换 YourAircraftTypeColumn 为实际列名
% 导入停机位数据表
%gateData = readtable('data.xlsx', 'Sheet', 'GateData'); 

% 提取停机位型号
gk = flight_gateData.gshape; % 替换 YourGateTypeColumn 为实际列名

% 提取停机位组号
gnum = flight_gateData.zh; % 替换 YourGateGroupColumn 为实际列名

% 提取机位分配的原计划方案
yuanf =flight_gateData.yuan; % 替换 YourOriginalPlanColumn 为实际列名

a = cellfun(@str2double, a);
d = cellfun(@str2double, d);
a=a'; %航班对机位占用的开始时刻
d=d'; %航班对机位占用的结束时刻
fi=fi'; %航班机型
gk=gk'; %停机位型号
gnum=gnum'; %停机位组号

% Store original data before delays for F3 calculation
original_a = a;
original_d = d;
original_f = yuanf;

% Randomly select 20% of flights for delays
num_delayed = floor(0.2*N);
delayed_flights = randperm(N, num_delayed);
delay_times = [25, 20, 15, 10]; % Example delays from requirements

% Apply delays
for i = 1:num_delayed
    flight_idx = delayed_flights(i);
    delay = delay_times(mod(i-1, length(delay_times)) + 1);
    a(flight_idx) = a(flight_idx) + delay;
    d(flight_idx) = d(flight_idx) + delay;
end
N=length(a); %航班数,单染色体上的基因数(即12个变量)(每个基因采用10进制) 
M=64; %机位数
Gn=23; %机位分组数
O=ones(1,M)*480; %机位开放时间
S=ones(1,M)*1440; %机位关闭时间
alpha=15; %同一机位相邻航班的最小安全缓冲时间
beta=15; %同一组内冲突避免安全间隔
gamma=5; %相邻分组冲突避免安全间隔
T_max=150;%过站时间超过1.5h自动分配至远机位

figk=cell(N,1); %存放每个航班可以停靠的机位(匹配机型)
for i=1:N
     figk{i,1}=find(gk>=fi(i));
end

tong=cell(N,1); %存放每个航班的冲突航班(同一机位相邻航班)
for i=2:N
     for j=1:i-1
          if (a(i)>=a(j))&&(a(i)<(d(j)+alpha))
             tong{i,1}=[tong{i,1},j];
          end
     end
end

tongg=cell(N,1); %存放每个航班的冲突航班(同一组内)
for i=2:N
     for j=1:i-1
          if (abs(a(i)-a(j))<beta)||(abs(d(i)-d(j))<beta)||(abs(a(i)-d(j))<beta)||(abs(d(i)-a(j))<beta)
             tongg{i,1}=[tongg{i,1},j];
          end
     end
end

ling=cell(N,1); %存放每个航班的冲突航班(相邻分组)
for i=2:N
     for j=1:i-1
          if (abs(a(i)-a(j))<gamma)||(abs(d(i)-d(j))<gamma)||(abs(a(i)-d(j))<gamma)||(abs(d(i)-a(j))<gamma)
             ling{i,1}=[ling{i,1},j];
          end
     end
end


NP=300; %染色体数目(初始化种群的数目)
G=300;  %最大遗传代数
Pc=0.8; %交叉概率
% Pm=0.08; %变异概率
Pm=0.1; %变异概率

f=zeros(NP,N); %初始种群赋空间
nf=zeros(NP,N); %子种群赋空间
for i=1:NP %随机获得初始种群(满足约束条件)
     f(i,:)=generate2(f(i,:),1,N,gnum,figk,tong,tongg,ling,a,d,T_max);
end

classNo=unique(f,'rows');

%一阶段求解
tic
%遗传算法循环(改)
for gen=1: G
     for np=1:NP
          % Calculate original objective
           Fit1(np)=func1(f(np,:),M,N,a,d,T_max); %计算各染色体的适应度
           % Calculate reallocation penalty
           Fit3(np)=func3(f(np,:),original_f,a,original_a,d,original_d,T_max); %计算重分配惩罚
           % Combine objectives (weighted sum for simple implementation)
           Fit(np)=0.7*Fit1(np) - 0.3*Fit3(np); %权重组合目标
     end
     maxFit=max(Fit); %最大值
     minFit=min(Fit); %最小值
     rr=find(Fit==maxFit);
     fBest=f(rr(1,1),:); %历代最优个体
     %基于轮盘赌的复制操作
     sum_Fit=sum(Fit);
     fitvalue=Fit./sum_Fit;
     fitvalue=cumsum(fitvalue);
     ms=sort(rand(NP,1));
     fiti=1;
     newi=1;
     while newi<=NP
           if (ms(newi))< fitvalue(fiti)
              nf(newi,:)=f(fiti,:);
              newi=newi+1;
           else
              fiti=fiti+1;
           end
     end

     %基于概率的单点交叉
     for i=1:2:NP-1
          if (rand<Pc)
             cpoint=randi(N-1); %产生一个小于N的随机整数cpoint,交换两个父代染色体的第cpoint个基因以后的基因
             nf(i,:)=[f(i,1:cpoint),f(i+1,cpoint+1:N)];
             nf(i+1,:)=[f(i+1,1:cpoint),f(i,cpoint+1:N)];
             nf(i,:)=ceshi2(nf(i,:),cpoint,N,gnum,figk,tong,tongg,ling,a,d,T_max); %测试交叉产生的个体是否满足约束,不满足约束则重新生成新的个体
             nf(i+1,:)=ceshi2(nf(i+1,:),cpoint,N,gnum,figk,tong,tongg,ling,a,d,T_max);
          else
             nf(i,:)=f(i,:);
             nf(i+1,:)=f(i+1,:);
          end
     end
     %基于概率的变异操作
     for m=1:NP %对所有个体进行变异
          index=zeros(1,N); %标记变异位置
          for n=1:N  %每个基因都可能变异
                r=rand(1,1);
                if r<Pm
                   index(n)=1;
                end
           end
           flag=find(index==1,1,'last'); %找到变异的最后一个位置
           if ~isempty(flag) %不为空
              % 将 newnf(m,:) 转换为 cell 数组格式
              temp_cell = cell(1,M);
              for i=1:M
                  temp_indices = find(nf(m,:)==i);
                  if ~isempty(temp_indices)
                      temp_cell{1,i} = temp_indices(:)'; % 确保是行向量
                  else
                      temp_cell{1,i} = []; % 如果没有找到，设为空数组
                  end
              end
              % 调用 generate 函数
              try
                  result = generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
                  % 将结果赋值回 nf
                  nf(m,:) = result;
              catch
                  % 如果 generate 失败，使用 generate2 作为后备方案
                  nf(m,:) = generate2(nf(m,:),flag,N,gnum,figk,tong,tongg,ling,a,d,T_max);
              end
           end
     end
     f=nf;
     f(1,:)=fBest; %保留最优个体在新种群中
     trace(gen)=maxFit; %历代最优适应度
end
toc
fBest;  %最优个体(最后)
trace(end); %最优值,end为取最后一个值
figure(1)
plot(trace)
xlabel('迭代次数')
ylabel('目标函数值')
title('适应度进化曲线')

%对一阶段所求得的个体进行处理
%对一阶段的适应度值进行排序，然后选择排在前面百分之10的个体参与二阶段迭代
fit=unique(Fit);%去除重复适应度值
fit=sort(fit,'descend');%升序排序
fit=fit';
%在一阶段适应度值矩阵里通过挑选出来的适应度值查找个体位置
%找到符合适应度要求的个体的序号
newfn=cell(length(fit),1);
for i=1:length(newfn)
newfn{i,1}=find(Fit==fit(i));
end

%确定二阶段参与求解的个体数
newNP=length(Fit(1,:))*0.2;

%初始化参与第二阶段求解的个体
newf=zeros(newNP,N);
newnf=zeros(newNP,N);

%通过筛选出来的个体编号矩阵，从一阶段种群中挑选出个体参与二阶段求解
k=1;%控制个体矩阵中个体的存放位置
for i=1:length(newfn)
    if(length(newfn{i,1})<=1)
        newf(k,:)=f(newfn{i,1},:);
        k=k+1;
    else
        for j=1:length(newfn{i,1})
            newf(k,:)=f((newfn{i,1}(j)),:);
            k=k+1;
        end
    end
end

%再取所有个体的前百分之10，与之前的百分之10的适应度值个体对应
  


%二阶段求解,对于交叉，将个体-航班编码方式映射到停机位-航班编码，然后对停机位进行排序，近机位与近机位交叉，远机位与远机位交叉
%保证一阶段目标函数值不变。交叉生成不可行解的原因在于交叉后可能存在不同机位分配了相同的航班号。这样有的航班多分配了一个机位，而
%有的航班没有分配到机位，需要将机位进行调换以生成可行解。
%变异处，加入一个目标启发式变异方式，在交叉后对新生成的子种群进行判断，若某个机场分配航班多，而另一个航班分配少，考虑是否可以将其进行调换
G=300;  %最大遗传代数
Pc=0.8; %交叉概率
% Pm=0.08; %变异概率
Pm=0.1; %变异概率

tic
%遗传算法循环(改)
for gen=1: G
     for np=1:newNP
          newFit(np)=func4(newf(np,:),M,a,d,O,S,T_max); %计算各染色体的适应度
     end
     maxFit=max(newFit); %最大值
     minFit=min(newFit); %最小值
     rr=find(newFit==minFit);
     newfBest=newf(rr(1,1),:); %历代最优个体
     newFit=(maxFit-newFit)/(maxFit-minFit); %归一化适应度值
     %基于轮盘赌的复制操作
     sum_Fit=sum(newFit);
     fitvalue=newFit./sum_Fit;
     fitvalue=cumsum(fitvalue);
     ms=sort(rand(newNP,1));
     fiti=1;
     newi=1;
     while newi<=newNP
           if (ms(newi))< fitvalue(fiti)
              newnf(newi,:)=newf(fiti,:);
              newi=newi+1;
           else
              fiti=fiti+1;
           end
     end
    
    newgf=cell(newNP,M);
    %将个体-航班编码转化为个体-停机位编码
    for i=1:length(newf(:,1))
    for j=1:M
        newgf{i,j}=find(newf(i,:)==j);
         end
     end

     %创建一个用于个体-停机位编码的子代个体
     newngf=cell(newNP,M);
     %基于概率的单点交叉
      for i=1:2:newNP-1
        if (rand<Pc)
           cpoint=randi(M-1); %产生一个小于N的随机整数cpoint,交换两个父代染色体的第cpoint个基因以后的基因
           newngf(i,:)=[newgf(i,1:cpoint),newgf(i+1,cpoint+1:M)];
           newngf(i+1,:)=[newgf(i+1,1:cpoint),newgf(i,cpoint+1:M)];
        else
           newngf(i,:)=newgf(i,:);
           newngf(i+1,:)=newgf(i+1,:);
         end
      end
      
     
     %基于概率的变异操作
     for m=1:NP %对所有个体进行变异
          index=zeros(1,N); %标记变异位置
          for n=1:N  %每个基因都可能变异
                r=rand(1,1);
                if r<Pm
                   index(n)=1;
                end
           end
           flag=find(index==1,1,'last'); %找到变异的最后一个位置
           if ~isempty(flag) %不为空
              % 将 newnf(m,:) 转换为 cell 数组格式
              temp_cell = cell(1,M);
              for i=1:M
                  temp_indices = find(nf(m,:)==i);
                  if ~isempty(temp_indices)
                      temp_cell{1,i} = temp_indices(:)'; % 确保是行向量
                  else
                      temp_cell{1,i} = []; % 如果没有找到，设为空数组
                  end
              end
              % 调用 generate 函数
              try
                  result = generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
                  % 将结果赋值回 nf
                  nf(m,:) = result;
              catch
                  % 如果 generate 失败，使用 generate2 作为后备方案
                  nf(m,:) = generate2(nf(m,:),flag,N,gnum,figk,tong,tongg,ling,a,d,T_max);
              end
           end
     end
     newf=nf;
     newf(1,:)=newfBest; %保留最优个体在新种群中
     trace(gen)=minFit; %历代最优适应度
end
toc
newfBest;  %最优个体(最后)
trace(end); %最优值,end为取最后一个值
figure(2)
plot(trace)
xlabel('迭代次数')
ylabel('目标函数值')
title('适应度进化曲线')

%画图操作
findex=zeros(1,N); %存放航班编号
for i=1:N
     findex(i)=i;
end
DurationTime=d-a;  %各航班占用机位的持续时间
gnum=[0,gnum];

% 第二个图：机位分配甘特图（按停机位编号）
figure(3)
clf;  % 清除当前图形窗口
hold on;  % 允许在同一图形窗口中绘制多个图形

% 设置图形大小和位置
set(gcf, 'Position', [100, 100, 1200, 800]);  % 调整图形窗口大小

% 设置图形背景
set(gca, 'Color', [1 1 1]);  % 设置白色背景
grid on;  % 添加网格线
set(gca, 'GridColor', [0.9 0.9 0.9]);  % 设置浅灰色网格

% 设置双Y轴
yyaxis left   % 激活y轴左侧
ylabel('停机位编号')
set(gca,'ylim',[0,M],'yTick',[0:1:M],'FontSize',8);

% 绘制矩形
rec=[0,0,0,0];
for i=1:N
    rec(1)=a(i); % 矩形左下角的横坐标
    rec(2)=newfBest(i)-0.5; % 矩形左下角的纵坐标
    rec(3)=DurationTime(i); % 矩形的x轴方向的长度
    rec(4)=1; % 矩形高度
    txt=sprintf('%d',findex(i));   
    % 使用不同的颜色和透明度
    rectangle('Position',rec, 'EdgeColor', [0 0 1], 'FaceColor', [0.8 0.8 1], 'LineWidth', 1);
    text(a(i)+rec(3)/2, newfBest(i), txt, 'FontSize', 6, ...
         'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
end

% 设置右侧Y轴
yyaxis right  % 激活y轴右侧
ylabel('分组编号')
set(gca,'ylim',[0,M],'yTick',[0:1:M]);
set(gca,'yticklabel',gnum)

% 设置X轴
xlabel('时间/min')
set(gca,'xlim',[480,1440],'xTick',[480:30:1440]);

% 添加标题
title('机位分配甘特图');

% 添加图例
box on;  % 显示边框
set(gca,'Layer','top');  % 确保坐标轴在最上层

hold off;  % 结束绘图

%转换航班-停机位编码为停机位-航班编码
for np=1:newNP
    for k=1:M
        if ~isempty(newngf{k})  % 检查 cell 是否为空
            for l=1:length(newngf{k})
                flight_num = newngf{k}(l);
                if flight_num > 0 && flight_num <= N
                    newnf(i,flight_num) = k;
                end
            end
        end
    end
end

%转换个体-停机位编码为个体-航班编码
for i=1:newNP
    for j=1:M
        if ~isempty(newngf{i,j})  % 检查 cell 是否为空
            for k=1:length(newngf{i,j})
                flight_num = newngf{i,j}(k);  % 获取航班号
                if flight_num > 0 && flight_num <= N  % 确保航班号有效
                    newnf(i,flight_num) = j;  % 将停机位号 j 分配给航班 flight_num
                end
            end
        end
    end
end

%存留

%转换个体-停机位编码为个体-航班编码
     for i=1:newNP
          for j=1:M
              for k=1:length(newngf{i,j})
                  newnf(i,newngf{i,j}(k))=j;
              end
          end
      end

% rectangle(),创建带有尖角或圆角的矩形
% rectangle('Position',pos,'Curvature',cur),pos-矩形的大小和位置，指定为[x y w h]形式的四元素向量,x和y元素定义矩形的左下角坐标。w和h元素
% 定义矩形的维度。

%画新方案停机位分配图
findex=zeros(1,N); %存放航班编号
for i=1:N
     findex(i)=i;
end
DurationTime=d-a;  %各航班占用机位的持续时间
% figure(2) %机位分配甘特图
% axis([480,1440,0,M+1]); %x轴,y轴的范围
% set(gca,'xtick',480:60:1440); %x轴的增长幅度(x轴的数据显示范围)
% set(gca,'ytick',0:2:M); %y轴的增长幅度(y轴的数据显示范围)
% xlabel('时间/min')
% ylabel('停机位编号','FontName','宋体')
% rec=[0,0,0,0];
% for i=1:N
%      rec(1)=a(i); %矩形左下角的横坐标
%      rec(2)=newfBest(i)-0.5; %矩形左下角的纵坐标
%      rec(3)=DurationTime(i); %矩形的x轴方向的长度
%      rec(4)=1; %矩形高度
%      txt=sprintf('%d',findex(i));   
%      rectangle('Position',rec);
%      text(a(i)+1,newfBest(i),txt,'FontSize',8);
% end

gBest=zeros(N,1); %最优分组
for i=1:N
     gBest(i)=gnum(newfBest(i));
end

figure(4) %机位分配甘特图(按分组编号)
axis([480,1440,0,Gn+1]); %x轴,y轴的范围
set(gca,'xtick',480:60:1440); %x轴的增长幅度(x轴的数据显示范围)
set(gca,'ytick',0:1:Gn); %y轴的增长幅度(y轴的数据显示范围)
xlabel('时间/min')
ylabel('分组编号')
rec=[0,0,0,0];
for i=1:N
     rec(1)=a(i); %矩形左下角的横坐标
     rec(2)=gBest(i)-0.5; %矩形左下角的纵坐标
     rec(3)=DurationTime(i); %矩形的x轴方向的长度
     rec(4)=1; %矩形高度
     txt=sprintf('%d',findex(i));   
     rectangle('Position',rec);
     text(a(i)+1,gBest(i),txt,'FontSize',8);
end

%绘制存在冲突的原机位分配方案

yuanf=yuanf'; %机位分配的原计划方案
yuanfit=func4(yuanf,M,a,d,O,S,T_max);
findex=zeros(1,N); %存放航班编号
for i=1:N
     findex(i)=i;
end
DurationTime=d-a;  %各航班占用机位的持续时间
figure(5)  % 改为figure(4)，避免覆盖之前的图
axis([480,1440,0,M+1]); %x轴,y轴的范围
set(gca,'xtick',480:60:1440); %x轴的增长幅度(x轴的数据显示范围)
set(gca,'ytick',0:2:M); %y轴的增长幅度(y轴的数据显示范围)
xlabel('时间/min')
ylabel('停机位编号','FontName','宋体')
rec=[0,0,0,0];
for i=1:N
     rec(1)=a(i); %矩形左下角的横坐标
     rec(2)=yuanf(i)-0.5; %矩形左下角的纵坐标
     rec(3)=DurationTime(i); %矩形的x轴方向的长度
     rec(4)=1; %矩形高度
     txt=sprintf('%d',findex(i));   
     rectangle('Position',rec);
     text(a(i)+1,yuanf(i),txt,'FontSize',8);
end
rectangle('Position',[1100,51-0.5,25,1],'Curvature',[1,1],'EdgeColor','r');
rectangle('Position',[1065,38-0.5,25,1],'Curvature',[1,1],'EdgeColor','r');

yuang=zeros(N,1); %原计划分组
for i=1:N
     yuang(i)=gnum(yuanf(i));
end
figure(6) %原计划机位分配甘特图(按分组编号)
axis([480,1440,0,Gn+1]); %x轴,y轴的范围
set(gca,'xtick',480:60:1440); %x轴的增长幅度(x轴的数据显示范围)
set(gca,'ytick',0:1:Gn); %y轴的增长幅度(y轴的数据显示范围)
xlabel('时间/min')
ylabel('分组编号')
rec=[0,0,0,0];
for i=1:N
     rec(1)=a(i); %矩形左下角的横坐标
     rec(2)=yuang(i)-0.5; %矩形左下角的纵坐标
     rec(3)=DurationTime(i); %矩形的x轴方向的长度
     rec(4)=1; %矩形高度
     txt=sprintf('%d',findex(i));   
     rectangle('Position',rec);
     text(a(i)+1,yuang(i),txt,'FontSize',8);
end
rectangle('Position',[860,19-0.5,20,1],'Curvature',[1,1],'EdgeColor','r');
rectangle('Position',[580,18,20,2],'Curvature',[1,1],'EdgeColor','r');
rectangle('Position',[584,11-0.5,20,2],'Curvature',[1,1],'EdgeColor','r');
rectangle('Position',[899,5-0.5,20,1],'Curvature',[1,1],'EdgeColor','r');
rectangle('Position',[579,12-0.5,30,1],'Curvature',[1,1],'EdgeColor','r');
rectangle('Position',[610,3-0.5,20,2],'Curvature',[1,1],'EdgeColor','r');

%同一机位冲突
tindex=zeros(N,1); %标记矩阵
tcell=cell(N,1); %位置矩阵
for i=2:N
     if ismember(yuanf(i),yuanf(tong{i,1}))
        tindex(i)=1;
        m=find(yuanf(tong{i,1})==yuanf(i));
        tcell(i)={[i,tong{i,1}(m)]};
     end
end

%同一分组冲突
tgindex=zeros(N,1); %标记矩阵
tgcell=cell(N,1); %位置矩阵
for i=2:N
     if ismember(gnum(yuanf(i)),unique(gnum(yuanf(tongg{i,1}))))
        tgindex(i)=1;
        mg=find(gnum(yuanf(tongg{i,1}))==gnum(yuanf(i)));
        tgcell(i)={[i,tongg{i,1}(mg)]};
     end
end

%相邻分组冲突
lindex=zeros(N,1); %标记矩阵
lcell=cell(N,1); %位置矩阵
for i=2:N
     if ismember(gnum(yuanf(i)),unique(gnum(yuanf(ling{i,1}))-1))||ismember(gnum(yuanf(i)),unique(gnum(yuanf(ling{i,1}))+1))
        lindex(i)=1;
        ml1=find((gnum(yuanf(ling{i,1}))-1)==gnum(yuanf(i)));
        ml2=find((gnum(yuanf(ling{i,1}))+1)==gnum(yuanf(i)));
        lcell(i)={[i,ling{i,1}(ml1),ling{i,1}(ml2)]};
     end
end

sumt=sum(tindex);
sumtg=sum(tgindex);
suml=sum(lindex);


% % 过站时间约束处理函数
% function f = apply_station_time_constraint(f,a,d,T_max)
%     % f 是航班到机位的分配情况，arrive 和 leave 是航班的到达和离开时间，T_max 是过站时间阈值
%     N = length(f);  % 总航班数
%     
%     for i = 1:N
%         % 计算航班的过站时间
%         layover_time = d(i) - a(i);
%         
%         % 如果过站时间超过阈值 T_max，将该航班分配至远机位（63或64）
%         if layover_time > T_max
%             % 随机选择远机位（63或64）
%             f(i) = 63 + randi([0, 1]);  % 63或64，randi([0, 1]) 随机生成 0 或 1
%         end
%     end
% end

%% 机场停机位分配优化算法
clear;
clc;
%% 读取数据
[num,txt,raw]=xlsread('newdata.xlsx');
a=num(:,1); %到达时间
d=num(:,2); %离开时间
fi=num(:,3); %航班机型
gk=num(:,4); %停机位型号
gnum=num(:,5); %停机位组号
O=num(:,6); %航班所属公司
S=num(:,7); %航班所属类型
yuanf=num(:,8); %原停机位
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
NP=300; %染色体数目(初始化种群的数目)
G=50;  %最大遗传代数
Pc=0.8; %交叉概率
Pm=0.08; %变异概率
T_max=150; %最大中转时间
alpha=15; %同一机位最小间隔时间
beta=15; %同一组内最小间隔时间
gamma=5; %相邻组间最小间隔时间

%% 初始化种群
f=zeros(NP,N); %初始种群
nf=zeros(NP,N); %新种群
trace=zeros(G,1); %记录每一代的最优值
fBest=zeros(1,N); %记录最优个体
tong=zeros(1,M); %记录每个机位的航班数
tongg=zeros(1,Gn); %记录每个机位组的航班数
ling=zeros(1,M); %记录每个机位是否有航班
figk=zeros(1,M); %记录每个机位的机型

%% 生成初始种群
for i=1:NP
    temp_cell = cell(1,M);
    f(i,:)=generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
end

%% 遗传算法循环(改进EBNSGA-II)
for gen=1: G
     objectives = zeros(NP,3);
     for np=1:NP
           objectives(np,1)=func1(f(np,:),M,N,a,d,T_max); %计算F1目标值：非远机位停靠率
           objectives(np,2)=func4(f(np,:),M,a,d,O,S,T_max); %计算F2目标值：时间间隔最小化
           objectives(np,3)=func3(f(np,:),original_f,a,original_a,d,original_d,T_max); %计算F3目标值：重分配惩罚
     end
     
     plot_objectives(objectives,gen);
     [ranks, fronts] = non_dominated_sort(objectives);
     distances = zeros(NP,1);
     for i = 1:length(fronts)
          distances(fronts{i}) = crowding_distance(objectives, fronts{i});
     end
     
     % 基于等级和拥挤度的选择操作
     combined = [f; nf];  % 合并父代和子代
     combined_objectives = [objectives; objectives];  % 临时复制目标值
     combined_ranks = [ranks; ranks];  % 临时复制等级
     combined_distances = [distances; distances];  % 临时复制拥挤度
     
     % 根据等级和拥挤度进行排序
     [~, sort_idx] = sort(combined_ranks + 1./(1+combined_distances));
     f = combined(sort_idx(1:NP),:);  % 选择前NP个个体
     
     % 记录当前最优个体（第一个非支配解）
     front1 = fronts{1};
     if ~isempty(front1)
         [~, best_idx] = max(distances(front1));
         fBest = f(front1(best_idx),:);
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
     trace(gen)=min(objectives(:,1)); %记录第一个目标的最优值
end

%% 输出结果
disp('最优个体为：');
disp(fBest);
disp('最优适应度为：');
disp(trace(end));

%% 绘制收敛曲线
figure(1);
plot(trace);
xlabel('迭代次数');
ylabel('适应度值');
title('适应度进化曲线');

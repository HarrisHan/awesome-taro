tic
%遗传算法循环(改)
for gen=1: G
     for np=1:newNP
          newFit(np)=func4(newf(np,:),M,a,d,O,S); %计算各染色体的适应度
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

     %创建一个用于个体-停机位编码的子代个体
     newngf=cell(newNP,M);
     %将原编码转成个体-停机位编码的父代个体
     newgf=cell(newNP,M);
     %将个体-航班编码转化为个体-停机位编码
     for i=1:length(newf(:,1))
         for j=1:M
             newgf{i,j}=find(newf(i,:)==j);
          end
     end
     
     %基于概率的单点交叉
     for i=1:2:newNP-1
       if (rand<Pc)
          cpoint=randi(M-1); %产生一个小于N的随机整数cpoint,交换两个父代染色体的第cpoint个基因以后的基因
          newngf(i,:)=[newgf(i,1:cpoint),newgf(i+1,cpoint+1:M)];
          newngf(i+1,:)=[newgf(i+1,1:cpoint),newgf(i,cpoint+1:M)];
          newngf(i,:)=ceshib(newngf(i,:),M,N,cpoint,gnum,figk,tong,tongg,ling);
          newngf(i+1,:)=ceshib(newngf(i+1,:),M,N,cpoint,gnum,figk,tong,tongg,ling);
       else
          newngf(i,:)=newgf(i,:);
          newngf(i+1,:)=newgf(i+1,:);
        end
     end
     
     %基于概率的变异操作
     for m=1:newNP %对所有个体进行变异
         r=rand(1,1);
         if r<Pm
             newnf(m,:)=generate(newngf(m,:),M,N,gnum,figk,tong,tongg,ling);
         end
     end
     newf=newnf;
     newf(1,:)=newfBest; %保留最优个体在新种群中
     trace(gen)=minFit; %历代最优适应度
end
toc
newfBest;  %最优个体(最后)
trace(end); %最优值,end为取最后一个值
figure(1)
plot(trace)
xlabel('迭代次数')
ylabel('目标函数值')
title('适应度进化曲线')
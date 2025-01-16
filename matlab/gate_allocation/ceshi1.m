%创建一个用于个体-停机位编码的子代个体
 newngf=cell(newNP,M);
 %基于概率的单点交叉
for i=1:2:newNP-1
if (rand<Pc)
   cpoint=randi(M-1); %产生一个小于N的随机整数cpoint,交换两个父代染色体的第cpoint个基因以后的基因
   newngf(i,:)=[newgf(i,1:cpoint),newgf(i+1,cpoint+1:M)];
   newngf(i+1,:)=[newgf(i+1,1:cpoint),newgf(i,cpoint+1:M)];
   newngf(i,:)=ceshi(newgf(i,:),newngf(i,:),M,N);
   newngf(i+1,:)=ceshi(newgf(i+1,:),newngf(i+1,:),M,N);
else
   newngf(i,:)=newgf(i,:);
   newngf(i+1,:)=newgf(i+1,:);
 end
end
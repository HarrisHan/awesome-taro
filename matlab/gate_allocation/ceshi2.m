%测试交叉产生的个体是否满足约束,不满足约束则重新生成新的个体
function result=ceshi2(f,cpoint,N,gnum,figk,tong,tongg,ling,a,d,T_max)
temfigk=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型和同一机位相邻航班约束)
temfigk2=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束和同一组内约束)
temfigk3=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束、同一组内约束和部分相邻分组约束)
newfigk=cell(N,1); %存放每个航班可以停靠的机位(满足所有约束)
flag=cpoint+1; %从第cpoint+1个基因开始检查
for i=flag:N
     temfigk{i,1}=setdiff(figk{i,1},f(1,tong{i,1}));
     temfigk2{i,1}=setdiff(temfigk{i,1},chazhao(gnum,gnum(f(1,tongg{i,1}))));
     temfigk3{i,1}=setdiff(temfigk2{i,1},chazhao(gnum,gnum(f(1,ling{i,1}))-1));
     newfigk{i,1}=setdiff(temfigk3{i,1},chazhao(gnum,gnum(f(1,ling{i,1}))+1));
     if ismember(f(i),newfigk{i,1})==0  %不满足约束
        f=generate2(f,flag,N,gnum,figk,tong,tongg,ling,a,d,T_max);
        break  
     end
end
result=f;
end
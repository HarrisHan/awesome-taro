%适应度函数
function result=func1(f,M,N,a,d,T_max)

% 在计算适应度之前，应用过站时间约束
f = apply_station_time_constraint(f,a,d,T_max);
    
newf=cell(M,1); %按照机位存放航班
yuanf=0;%记录分配到远机位的航班数
for i=1:M
     newf{i,1}=find(f==i);
end
for i=63:64
     yuanf=yuanf+length(newf{i,1});%分配到远机位的航班数
end
fit=(N-yuanf)/N;%适应度函数
result=fit;
end
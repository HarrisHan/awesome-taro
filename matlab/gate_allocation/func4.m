%适应度函数
function result=func4(f,M,a,d,O,S,T_max)

% 在计算适应度之前，应用过站时间约束
f = apply_station_time_constraint(f,a,d,T_max);
    
newf=cell(M,1); %按照机位存放航班
for i=1:M
     newf{i,1}=find(f==i);
end
fitM=zeros(M,1); %各机位的适应度函数
for i=1:M
     if isempty(newf{i,1})==0
        fitM(i)=(a(newf{i,1}(1))-O(i))^2;
        if length(newf{i,1})>=2
           for j=2:length(newf{i,1})
                fitM(i)=fitM(i)+(a(newf{i,1}(j))-d(newf{i,1}(j-1)))^2;
           end
        end
        fitM(i)=fitM(i)+(S(i)-d(newf{i,1}(length(newf{i,1}))))^2;
     else
        fitM(i)=(S(i)-O(i))^2;
     end
end
fit=sum(fitM); %适应度函数
result=fit;
end
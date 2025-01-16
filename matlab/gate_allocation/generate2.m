%从第flag个位置开始重新生成新的满足约束的个体
function nf=generate2(f,flag,N,gnum,figk,tong,tongg,ling,a,d,T_max)


    
temfigk=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型和同一机位相邻航班约束)
temfigk2=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束和同一组内约束)
temfigk3=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束、同一组内约束和部分相邻分组约束)
newfigk=cell(N,1); %存放每个航班可以停靠的机位(满足所有约束)
j=flag;
while j<=N
     temfigk{j,1}=setdiff(figk{j,1},f(1,tong{j,1}));
     temfigk2{j,1}=setdiff(temfigk{j,1},chazhao(gnum,gnum(f(1,tongg{j,1}))));
     temfigk3{j,1}=setdiff(temfigk2{j,1},chazhao(gnum,gnum(f(1,ling{j,1}))-1));
     % newfigk{j,1}表示航班j在所有约束下可以选择的机位
     newfigk{j,1}=setdiff(temfigk3{j,1},chazhao(gnum,gnum(f(1,ling{j,1}))+1));
     %如果存在可行的机位，随机选择一个机位来为航班分配新的机位，并继续处理下一个航班；
     %否则重新从 flag 开始尝试，直到找到符合条件的分配方案。
     if ~isempty(newfigk{j,1})
        f(j)=newfigk{j,1}(randi(length(newfigk{j,1})));
        j=j+1;
        continue;
     else
         j=flag;
     end
end

% 在生成新的机位分配方案后，应用过站时间约束
f = apply_station_time_constraint(f,a,d,T_max);
nf=f;%最后返回新的航班分配方案f
end
%从第flag个位置开始重新生成新的满足约束的个体
function nf=generate3(f,flag,N,gnum,figk,tong,tongg,ling)
temfigk=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型和同一机位相邻航班约束)
temfigk2=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束和同一组内约束)
temfigk3=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束、同一组内约束和部分相邻分组约束)
newfigk=cell(N,1); %存放每个航班可以停靠的机位(满足所有约束)
j=flag;
while j<=N
     temfigk{j,1}=setdiff(figk{j,1},f(1,tong{j,1}));
     temfigk2{j,1}=setdiff(temfigk{j,1},chazhao(gnum,gnum(f(1,tongg{j,1}))));
     temfigk3{j,1}=setdiff(temfigk2{j,1},chazhao(gnum,gnum(f(1,ling{j,1}))-1));
     newfigk{j,1}=setdiff(temfigk3{j,1},chazhao(gnum,gnum(f(1,ling{j,1}))+1));
     if ~isempty(newfigk{j,1})
         number=newfigk{j,1}(randi(length(newfigk{j,1})));
         if isequal(number,63)==1 || isequal(number,64)==1
            number=newfigk{j,1}(randi(length(newfigk{j,1})));
        end
        f(j)=number;
        j=j+1;
        continue;
     else
         j=flag;
     end
end
nf=f;
end
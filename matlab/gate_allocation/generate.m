%与 generate2 类似，该函数主要是通过变异操作产生新的航班分配方案，同时满足所有约束条件
function nf=generate(f,M,N,gnum,figk,tong,tongg,ling,a,d,T_max)

mg=zeros(M,1);

lg=zeros(M,1);

gf=zeros(M,1);
%计算每个机位的航班数量： gf(i,1) 存储每个机位的航班数量。通过遍历所有机位和航班，找到最大和最小航班数对应的机位。
for i=1:M
    if ~isempty(f{1,i})
        gf(i,1)=length(f{1,i});
    else
        gf(i,1)=0;
    end
end

%ຽ
maxf=max(gf);
%ٺ
minf=min(gf);

%根据航班数量选择机位： 选择最大航班数和最小航班数的机位（mg 和 lg），以便为新航班分配机位时做调整。
%¼ͣλźٵͣλ
for j=1:M
    if (gf(j,1)==maxf)
        mg(j,1)=j;
    elseif(gf(j,1)==minf)
        lg(j,1)=j;
    end
end


mg(mg==0)=[]; % 删除无效的机位
lg(lg==0)=[];

%将个体-停机位编码（f）转换为个体-航班编码(fg)
%f{1, k} 存储的是分配给机位 k 的航班列表，而 fg 则是一个数组，记录每个航班被分配到的机位
fg=zeros(1,N);
for k=1:M
    if ~isempty(f{1,k})  % 检查 cell 是否为空
        temp_flights = f{1,k};  % 获取当前停机位的航班列表
        if ~isempty(temp_flights)  % 确保航班列表不为空
            for l=1:length(temp_flights)
                if temp_flights(l) > 0 && temp_flights(l) <= N  % 确保索引有效
                    fg(1,temp_flights(l)) = k;
                end
            end
        end
    end
end

temfigk=cell(N,1);                   
temfigk2=cell(N,1);
temfigk3=cell(N,1);
newfigk=cell(N,1); 

for m=1:length(mg)
    if ~isempty(f{1,mg(m)})
        for n=1:length(f{1,mg(m)})
            o=f{1,mg(m)}(n);
            if o > 0 && o <= N  % 确保航班号有效
                temfigk{o,1}=setdiff(figk{o,1},fg(1,tong{o,1}));
                temfigk2{o,1}=setdiff(temfigk{o,1},chazhao(gnum,gnum(fg(1,tongg{o,1}))));
                temfigk3{o,1}=setdiff(temfigk2{o,1},chazhao(gnum,gnum(fg(1,ling{o,1}))-1));
                newfigk{o,1}=setdiff(temfigk3{o,1},chazhao(gnum,gnum(fg(1,ling{o,1}))+1));

                if ~isempty(newfigk{o,1})
  
                    for p=1:length(lg(:,1))
                        if ismember(lg(p,1),newfigk{o,1})==1 && lg(p,1)~=63 && lg(p,1)~=64
                            fg(1,o)=lg(p,1);
                            nf=fg;
                            return
                        end
                    end
                end
            end
        end
    end
end
% 在生成新的机位分配方案后，应用过站时间约束
fg= apply_station_time_constraint(fg,a,d,T_max);
nf=fg;  % 如果没有找到更好的解，返回原始解
end
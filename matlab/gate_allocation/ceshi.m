%测试交叉产生的个体是否满足约束,不满足约束则重新生成新的个体
function result=ceshi(f,nf,M,N,gnum,figk,tong,tongg,ling)
%存放个体-停机位编码转为个体-航班编码
nfg=zeros(1,N);
%存放使用了多个停机位的航班编号
msf=zeros(N,1);
%存放未分配停机位的航班编号
noflight=zeros(N,1);
%通过个体-停机位编码方式查找被多次使用的停机位
usg=cell(1,N);%记录各航班分配到的停机位编号
%记录停机位被哪个航班多次占用
mufg=zeros(1,M);

%将个体-停机位编码转换为个体-航班编码，并找到被多余占用的停机位
for i=1:M
    for j=1:length(nf{1,i})
        if length(usg{1,nf{1,i}(j)})==1
            msf(nf{1,i}(j))=nf{1,i}(j);
            usg{1,nf{1,i}(j)}=[usg{1,nf{1,i}(j)},i];
            mufg(1,i)=nf{1,i}(j);
        else
            usg{1,nf{1,i}(j)}=i;
        end
    end
end

%获得被多次占用的停机位编号和占用停机位的航班编号
msg=zeros(1,N);%所有被多次占用的停机位编号
msgf=zeros(1,N);%多次占用的停机位上停放的航班编号
for k=1:N
    for l=1:length(usg{1,k})
        if length(usg{1,k})>1
            msg(1,k+l)=usg{1,k}(l);
            msgf(1,k+l)=k;
        end
    end
end

%寻找未分配航班编号
for m=1:N
    if isempty(usg{1,m})==1
        noflight(m,1)=m;
    end
end

%将个体-停机位编码转为个体-航班编码，为了查找航班可用停机位
for n=1:M
    for r=1:length(nf{1,n})
        nfg(1,nf{1,n}(r))=n;
    end
end

%去除多余零元素
noflight(noflight==0)=[];
msg(msg==0)=[];
msgf(msgf==0)=[];

temfigk=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型和同一机位相邻航班约束)
temfigk2=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束和同一组内约束)
temfigk3=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束、同一组内约束和部分相邻分组约束)
newfigk=cell(N,1); %存放每个航班可以停靠的机位(满足所有约束)

for p=1:length(noflight)
    for o = noflight(p,1)
     temfigk{o,1}=setdiff(figk{o,1},nfg(1,tong{o,1}));
     temfigk2{o,1}=setdiff(temfigk{o,1},chazhao(gnum,gnum(nfg(1,tongg{o,1}))));
     temfigk3{o,1}=setdiff(temfigk2{o,1},chazhao(gnum,gnum(nfg(1,ling{o,1}))-1));
     newfigk{o,1}=setdiff(temfigk3{o,1},chazhao(gnum,gnum(nfg(1,ling{o,1}))+1));
    
     for w=1:length(msg)
         if ismember(msg(w),newfigk{o,1})==1  %如果未分配停机位可以分配给未进行停机位分配的航班，进行分配
            usg{1,o}=msg(w);%给未分配的航班分配被多余占用的停机位
            %原来分配了多余停机位的航班需要将调整后的停机位删除
            usg{1,mufg(msg(w))}=setdiff(usg{1,mufg(msg(w))},msg(w));
         else
             %如果未分配航班不能停放在多余占用的停机位上，直接返回
             result=f;
            return
         end
     end
    end
end

for q=1:M
    nf{1,q}=find(usg==q);
end
result=nf;
end
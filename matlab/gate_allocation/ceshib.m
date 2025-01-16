function result=ceshib(nf,M,N,cpoint,gnum,figk,tong,tongg,ling)

%将个体-停机位编码转为个体-航班编码，并进行存储
nfg=cell(1,N);

%找到未得到停机位分配的航班，并记录
noflight=zeros(N,1);

%记录需要调整的停机位编号,与航班编号对应
tzg=cell(N,1);

%记录需要调整的停机位编号
nogate=zeros(N,1);

%在将编码方式转变过程中找到占用了多个停机位的航班编号
for i=1:M
    for p=1:length(nf{1,i})%nf{1,i}是该停机位上停放的所有航班
        if length(nfg{1,nf{1,i}(p)})==1%通过停机位编号查找停放在该停机位上的所有航班
            nfg{1,nf{1,i}(p)}=[nfg{1,nf{1,i}(p)},i];
        else
            nfg{1,nf{1,i}(p)}=i;
        end
    end
end

%找到需要调整的航班-停机位对应关系
%即需要调整这些航班，这些航班都占用了哪些停机位
for k=1:N
    if length(nfg{1,k})>1%该航班占用了多个停机位需要调整
        tzg{k,1}=nfg{1,k};
    end
end
        
%找到需要调整的航班编号(优先调整未分配航班，然后在调整多余分配的航班)
for n=1:N
    if isempty(nfg{1,n})==1
        noflight(n,1)=n;
    end
end


%找到需要调整的停机位编号
nn=1;
for r=1:length(tzg(:,1))
    for v=1:2
        if ~isempty(tzg{r,1})
            nogate(nn,1)=tzg{r,1}(v);
            nn=nn+1;
        end
    end
end

%将需要调整的航班编号列表及停机位编号列表中的多余零元素去除
noflight(noflight==0)=[];
nogate(nogate==0)=[];

for o=1:length(noflight)
    for p=noflight(o,1)
        for q=1:length(nogate)
            for w=nogate(q,1)
                nfg{1,p}=w;%将需要调整的停机位分配给未分配的航班
               %然后对原分配方案进行修改
                ff=1;%初始化需要调整的航班号
                for t=1:N
                    if ~isempty(tzg{t,1})
                        if ismember(w,tzg{t,1})
                            ff=t;
                            break;
                        end
                    end
                end
                if length(nfg{1,ff})>1
                    nfg{1,ff}=setdiff(nfg{1,ff},w);
                end
            end
        end
    end
end

%对于仍存在多余分配的停机位，随机删除一个其已占用的停机位(后续改)
for x=1:N
    if length(nfg{1,x})>1
        randd=randi(2);
        nfg{1,x}=setdiff(nfg{1,x},nfg{1,x}(randd));
    end
end

%对于仍未分配的停机位，随机分配一个近机位
for z=1:N
    if isempty(nfg{1,z})==1
        rande=randi(62);%随机从近机位中挑选一个进行分配，日后改
        nfg{1,z}=rande;
    end
end

%重新编码
newnfg=zeros(1,N);
for x=1:N
    newnfg(1,x)=nfg{1,x};
end

temfigk=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型和同一机位相邻航班约束)
temfigk2=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束和同一组内约束)
temfigk3=cell(N,1); %存放每个航班可以停靠的机位(满足匹配机型、同一机位相邻航班约束、同一组内约束和部分相邻分组约束)
newfigk=cell(N,1); %存放每个航班可以停靠的机位(满足所有约束)
flag=cpoint+1; %从第cpoint+1个基因开始检查
for i=flag:N
     temfigk{i,1}=setdiff(figk{i,1},newnfg(1,tong{i,1}));
     temfigk2{i,1}=setdiff(temfigk{i,1},chazhao(gnum,gnum(newnfg(1,tongg{i,1}))));
     temfigk3{i,1}=setdiff(temfigk2{i,1},chazhao(gnum,gnum(newnfg(1,ling{i,1}))-1));
     newfigk{i,1}=setdiff(temfigk3{i,1},chazhao(gnum,gnum(newnfg(1,ling{i,1}))+1));
     if ismember(newnfg(i),newfigk{i,1})==0  %不满足约束
        newnfg=generate3(newnfg,flag,N,gnum,figk,tong,tongg,ling);
        break
     end
end

newnf=cell(1,M);
for y=1:M
    newnf{1,y}=find(newnfg(1,:)==y);
end

result=newnf;
end
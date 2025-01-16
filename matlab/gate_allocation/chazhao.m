function C = chazhao(A,B)
% 查找一个数组B中元素在另一个数组A中的位置
% 输入: A为被查找数组,B为查找数组
% 输出: C为B中元素在A中的位置
B=unique(B); %去除数组中的重复值
C=[];
for i= 1:length(B)
     C1=find(A==B(i));
     C=[C,C1];
end
end
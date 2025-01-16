% 创建测试数据集验证约束检查
clear;
clc;

% 小规模测试数据
N = 10;  % 10个航班
M = 64;  % 64个机位
T_max = 150;

% 生成测试数据
a = [480; 500; 520; 540; 560; 580; 600; 620; 640; 660];  % 到达时间
d = [550; 570; 590; 610; 630; 650; 670; 690; 710; 730];  % 离开时间
fi = [1; 2; 1; 2; 1; 2; 1; 2; 1; 2];  % 航班机型
gk = ones(1,M)*3;  % 所有机位都可以停靠所有机型
gnum = [1:23, ones(1,41)*23];  % 机位分组
O = ones(1,M)*480;  % 机位开放时间
S = ones(1,M)*1440;  % 机位关闭时间

% 测试用例1：正常分配
disp('测试用例1：正常分配');
solution1 = [1; 2; 3; 4; 5; 6; 7; 8; 9; 10];  % 每个航班分配不同机位
try
    verify_constraints(solution1, M, N, a, d, O, S, T_max, gnum, fi, gk);
    disp('测试用例1通过');
catch ME
    disp(['测试用例1失败: ' ME.message]);
end

% 测试用例2：违反过站时间约束
disp('测试用例2：违反过站时间约束');
d(1) = d(1) + T_max + 10;  % 使第一个航班超过T_max
solution2 = [1; 2; 3; 4; 5; 6; 7; 8; 9; 10];
try
    verify_constraints(solution2, M, N, a, d, O, S, T_max, gnum, fi, gk);
    disp('测试用例2应该失败但通过了');
catch ME
    disp('测试用例2按预期失败');
end

% 测试用例3：违反时间间隔约束
disp('测试用例3：违反时间间隔约束');
a(2) = a(1) + 10;  % 使两个航班时间间隔小于alpha
solution3 = [1; 1; 3; 4; 5; 6; 7; 8; 9; 10];  % 两个航班分配到同一机位
try
    verify_constraints(solution3, M, N, a, d, O, S, T_max, gnum, fi, gk);
    disp('测试用例3应该失败但通过了');
catch ME
    disp('测试用例3按预期失败');
end

% 测试用例4：远机位分配
disp('测试用例4：远机位分配');
d(1) = d(1) + T_max + 10;  % 使第一个航班超过T_max
solution4 = [63; 2; 3; 4; 5; 6; 7; 8; 9; 10];  % 将超时航班分配到远机位
try
    verify_constraints(solution4, M, N, a, d, O, S, T_max, gnum, fi, gk);
    disp('测试用例4通过');
catch ME
    disp(['测试用例4失败: ' ME.message]);
end

% 显示测试结果汇总
disp('测试完成');

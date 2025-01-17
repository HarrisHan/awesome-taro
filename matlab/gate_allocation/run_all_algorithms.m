% 运行所有算法并比较结果
clear;
clc;

% 定义要运行的算法
algorithms = {'EBNSGA-II', 'NSGA-II', 'PSO', 'Two-Phase-GA'};

% 创建结果目录
if ~exist('results', 'dir')
    mkdir('results');
end

% 读取数据
[num,txt,raw] = xlsread('newdata.xlsx');
a = num(:,1); % 到达时间
d = num(:,2); % 离开时间
fi = num(:,3); % 航班机型
gk = num(:,4); % 停机位型号
gnum = num(:,5); % 停机位组号
O = num(:,6); % 航班所属公司
S = num(:,7); % 航班所属类型
yuanf = num(:,8); % 原停机位

% 转置向量
fi = fi';
gk = gk';
gnum = gnum';

% 保存原始数据用于计算重分配惩罚
original_a = a;
original_d = d;
original_f = yuanf;

% 设置算法参数
N = length(a); % 航班数
M = 64; % 机位数
NP = 300; % 种群大小
G = 50; % 迭代次数
Pc = 0.8; % 交叉概率
Pm = 0.08; % 变异概率
T_max = 150; % 最大中转时间

% 运行每个算法
for i = 1:length(algorithms)
    disp(['运行算法: ' algorithms{i}]);
    algorithm_type = algorithms{i};
    
    % 运行主程序并获取所需变量
    switch algorithm_type
        case 'EBNSGA-II'
            [best_solution, pareto_front] = main(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d);
        case 'NSGA-II'
            [best_solution, pareto_front] = nsga2(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d);
        case 'PSO'
            [best_solution, pareto_front] = pso(M, N, a, d, O, S, T_max, NP, G, original_f, original_a, original_d);
        case 'Two-Phase-GA'
            [best_solution, pareto_front] = two_phase_ga(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d);
    end
    
    % 保存结果
    save(['results/' algorithm_type '_result.mat'], 'best_solution', 'pareto_front');
    
    % 验证约束条件
    disp(['验证' algorithms{i} '的约束条件']);
    verify_constraints(best_solution, M, N, a, d, O, S, T_max, gnum, fi, gk);
    
    close all; % 关闭所有图形窗口
end

% 加载所有结果并比较
compare_algorithms(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d);

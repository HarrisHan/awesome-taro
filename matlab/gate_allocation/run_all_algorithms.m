% 运行所有算法并比较结果
clear;
clc;

% 定义要运行的算法
algorithms = {'EBNSGA-II', 'NSGA-II', 'PSO', 'Two-Phase-GA'};

% 创建结果目录
if ~exist('results', 'dir')
    mkdir('results');
end

% 运行每个算法
for i = 1:length(algorithms)
    disp(['运行算法: ' algorithms{i}]);
    algorithm_type = algorithms{i};
    
    % 运行主程序并获取所需变量
    main;  % 运行主程序会设置所有需要的变量
    
    % 保存当前算法的结果
    save(['results/' algorithms{i} '_vars.mat'], 'fBest', 'M', 'N', 'a', 'd', 'O', 'S', 'T_max', 'gnum', 'fi', 'gk');
    
    % 验证约束条件
    disp(['验证' algorithms{i} '的约束条件']);
    verify_constraints(fBest, M, N, a, d, O, S, T_max, gnum, fi, gk);
    
    close all;  % 关闭所有图形窗口
end

% 加载所有结果并比较
all_results = struct();
for i = 1:length(algorithms)
    result_file = ['results/' algorithms{i} '_result.mat'];
    if exist(result_file, 'file')
        data = load(result_file);
        all_results.(algorithms{i}) = data;
    end
end

% 调用比较函数
compare_algorithms(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d);

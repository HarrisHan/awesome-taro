function [best_solution, pareto_front] = pso(M, N, a, d, O, S, T_max, NP, G, original_f, original_a, original_d)
    % PSO参数
    w = 0.7;  % 惯性权重
    c1 = 2;   % 个体学习因子
    c2 = 2;   % 社会学习因子
    
    % 初始化种群位置和速度
    positions = zeros(NP,N);
    velocities = zeros(NP,N);
    pbest = zeros(NP,N);
    pbest_obj = inf(NP,3);
    gbest = zeros(1,N);
    gbest_obj = inf(1,3);
    
    % 初始化辅助变量
    tong = zeros(1,M);
    tongg = zeros(1,23);
    ling = zeros(1,M);
    figk = zeros(1,M);
    
    % 初始化种群
    for i=1:NP
        temp_cell = cell(1,M);
        positions(i,:) = generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
        velocities(i,:) = rand(1,N)*2 - 1;  % [-1,1]的随机速度
        pbest(i,:) = positions(i,:);
    end
    
    % 主循环
    pareto_archive = [];
    for gen=1:G
        % 评估目标值
        objectives = zeros(NP,3);
        for i=1:NP
            pos = round(positions(i,:));  % 离散化位置
            pos = apply_station_time_constraint(pos,a,d,T_max);
            objectives(i,1) = func1(pos,M,N,a,d,T_max);
            objectives(i,2) = func4(pos,M,a,d,O,S,T_max);
            objectives(i,3) = func3(pos,original_f,a,original_a,d,original_d,T_max);
            
            % 更新个体最优
            if all(objectives(i,:) <= pbest_obj(i,:)) && any(objectives(i,:) < pbest_obj(i,:))
                pbest(i,:) = positions(i,:);
                pbest_obj(i,:) = objectives(i,:);
            end
        end
        
        % 更新帕累托档案
        pareto_archive = [pareto_archive; objectives];
        [~, fronts] = non_dominated_sort(pareto_archive);
        pareto_archive = pareto_archive(fronts{1},:);
        
        % 选择全局最优（随机选择一个非支配解）
        if ~isempty(fronts{1})
            idx = randi(length(fronts{1}));
            gbest = positions(fronts{1}(idx),:);
            gbest_obj = objectives(fronts{1}(idx),:);
        end
        
        % 更新速度和位置
        for i=1:NP
            % 更新速度
            velocities(i,:) = w*velocities(i,:) + ...
                c1*rand*(pbest(i,:) - positions(i,:)) + ...
                c2*rand*(gbest - positions(i,:));
            
            % 限制速度
            velocities(i,:) = min(max(velocities(i,:),-1),1);
            
            % 更新位置
            positions(i,:) = positions(i,:) + velocities(i,:);
            
            % 离散化和约束处理
            positions(i,:) = round(positions(i,:));
            positions(i,:) = min(max(positions(i,:),1),M);
            positions(i,:) = apply_station_time_constraint(positions(i,:),a,d,T_max);
        end
    end
    
    % 返回结果
    pareto_front = pareto_archive;
    [~, best_idx] = min(pareto_archive(:,1));  % 选择第一个目标最优的解
    best_solution = positions(best_idx,:);
end

function [best_solution, pareto_front] = nsga2(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d)
    % 初始化种群
    f = zeros(NP,N);
    nf = zeros(NP,N);
    
    % 初始化辅助变量
    tong = zeros(1,M);
    tongg = zeros(1,23);
    ling = zeros(1,M);
    figk = zeros(1,M);
    
    % 生成初始种群
    for i=1:NP
        temp_cell = cell(1,M);
        f(i,:) = generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
    end
    
    % 主循环
    for gen=1:G
        % 计算目标值
        objectives = zeros(NP,3);
        for np=1:NP
            objectives(np,1)=func1(f(np,:),M,N,a,d,T_max);
            objectives(np,2)=func4(f(np,:),M,a,d,O,S,T_max);
            objectives(np,3)=func3(f(np,:),original_f,a,original_a,d,original_d,T_max);
        end
        
        % 非支配排序
        [ranks, fronts] = non_dominated_sort(objectives);
        distances = zeros(NP,1);
        for i = 1:length(fronts)
            distances(fronts{i}) = crowding_distance(objectives, fronts{i});
        end
        
        % 选择操作
        [~, sort_idx] = sort(ranks + 1./(1+distances));
        f = f(sort_idx(1:NP),:);
        
        % 交叉操作
        for i=1:2:NP-1
            if rand < Pc
                cpoint = randi(N-1);
                nf(i,:) = [f(i,1:cpoint), f(i+1,cpoint+1:N)];
                nf(i+1,:) = [f(i+1,1:cpoint), f(i,cpoint+1:N)];
                nf(i,:) = apply_station_time_constraint(nf(i,:),a,d,T_max);
                nf(i+1,:) = apply_station_time_constraint(nf(i+1,:),a,d,T_max);
            else
                nf(i,:) = f(i,:);
                nf(i+1,:) = f(i+1,:);
            end
        end
        
        % 变异操作
        for i=1:NP
            if rand < Pm
                j = randi(N);
                nf(i,j) = randi(M);
                nf(i,:) = apply_station_time_constraint(nf(i,:),a,d,T_max);
            end
        end
        
        % 更新种群
        f = nf;
    end
    
    % 计算最终的Pareto前沿
    objectives = zeros(NP,3);
    for np=1:NP
        objectives(np,1)=func1(f(np,:),M,N,a,d,T_max);
        objectives(np,2)=func4(f(np,:),M,a,d,O,S,T_max);
        objectives(np,3)=func3(f(np,:),original_f,a,original_a,d,original_d,T_max);
    end
    [~, fronts] = non_dominated_sort(objectives);
    pareto_front = objectives(fronts{1},:);
    
    % 选择一个最优解（以第一个目标为主）
    [~, best_idx] = min(objectives(fronts{1},1));
    best_solution = f(fronts{1}(best_idx),:);
end

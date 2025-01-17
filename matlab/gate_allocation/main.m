function [best_solution, pareto_front] = main(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d)
    % 初始化种群
    f = zeros(NP,N);
    nf = zeros(NP,N);
    trace = zeros(G,1);
    fBest = zeros(1,N);
    tong = zeros(1,M);
    tongg = zeros(1,23);
    ling = zeros(1,M);
    figk = zeros(1,M);
    
    % 生成初始种群
    for i=1:NP
        temp_cell = cell(1,M);
        f(i,:) = generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
    end
    
    % 遗传算法循环(改进EBNSGA-II)
    for gen=1:G
        objectives = zeros(NP,3);
        for np=1:NP
            objectives(np,1) = func1(f(np,:),M,N,a,d,T_max); % 计算F1目标值：非远机位停靠率
            objectives(np,2) = func4(f(np,:),M,a,d,O,S,T_max); % 计算F2目标值：时间间隔最小化
            objectives(np,3) = func3(f(np,:),original_f,a,original_a,d,original_d,T_max); % 计算F3目标值：重分配惩罚
        end
        
        plot_objectives(objectives,gen);
        [ranks, fronts] = non_dominated_sort(objectives);
        distances = zeros(NP,1);
        for i = 1:length(fronts)
            distances(fronts{i}) = crowding_distance(objectives, fronts{i});
        end
        
        % 基于等级和拥挤度的选择操作
        combined = [f; nf];  % 合并父代和子代
        combined_objectives = [objectives; objectives];  % 临时复制目标值
        combined_ranks = [ranks; ranks];  % 临时复制等级
        combined_distances = [distances; distances];  % 临时复制拥挤度
        
        % 根据等级和拥挤度进行排序
        [~, sort_idx] = sort(combined_ranks + 1./(1+combined_distances));
        f = combined(sort_idx(1:NP),:);  % 选择前NP个个体
        
        % 记录当前最优个体（第一个非支配解）
        front1 = fronts{1};
        if ~isempty(front1)
            [~, best_idx] = max(distances(front1));
            fBest = f(front1(best_idx),:);
        end
        
        % 基于概率的单点交叉
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
        
        % 基于概率的变异操作
        for i=1:NP
            if rand < Pm
                j = randi(N);
                nf(i,j) = randi(M);
                nf(i,:) = apply_station_time_constraint(nf(i,:),a,d,T_max);
            end
        end
        
        f = nf;
        f(1,:) = fBest;  % 保留最优个体在新种群中
        trace(gen) = min(objectives(:,1));  % 记录第一个目标的最优值
    end
    
    % 计算最终的Pareto前沿
    objectives = zeros(NP,3);
    for np=1:NP
        objectives(np,1) = func1(f(np,:),M,N,a,d,T_max);
        objectives(np,2) = func4(f(np,:),M,a,d,O,S,T_max);
        objectives(np,3) = func3(f(np,:),original_f,a,original_a,d,original_d,T_max);
    end
    [~, final_fronts] = non_dominated_sort(objectives);
    pareto_front = objectives(final_fronts{1},:);
    best_solution = fBest;
end

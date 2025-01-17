function [best_solution, pareto_front] = two_phase_ga(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d)
    % 第一阶段：优化非远机位停靠率
    f = zeros(NP,N);
    nf = zeros(NP,N);
    tong = zeros(1,M);
    tongg = zeros(1,23);
    ling = zeros(1,M);
    figk = zeros(1,M);
    
    % 初始化种群
    for i=1:NP
        temp_cell = cell(1,M);
        f(i,:) = generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
    end
    
    % 第一阶段优化
    for gen=1:floor(G/2)
        Fit = zeros(NP,1);
        for np=1:NP
            Fit(np) = func1(f(np,:),M,N,a,d,T_max);
        end
        
        % 选择操作
        [~, sort_idx] = sort(Fit, 'descend');
        f = f(sort_idx,:);
        
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
        
        f = nf;
    end
    
    % 保存第一阶段最优解
    [~, best_idx] = max(Fit);
    phase1_best = f(best_idx,:);
    
    % 第二阶段：优化时间间隔和重分配惩罚
    % 使用第一阶段结果初始化部分种群
    for i=1:NP/4
        f(i,:) = phase1_best;
    end
    for i=NP/4+1:NP
        temp_cell = cell(1,M);
        f(i,:) = generate(temp_cell,M,N,gnum,figk,tong,tongg,ling,a,d,T_max);
    end
    
    % 第二阶段优化
    objectives_history = zeros(floor(G/2),3);
    for gen=1:floor(G/2)
        objectives = zeros(NP,3);
        for np=1:NP
            objectives(np,1) = func1(f(np,:),M,N,a,d,T_max);
            objectives(np,2) = func4(f(np,:),M,a,d,O,S,T_max);
            objectives(np,3) = func3(f(np,:),original_f,a,original_a,d,original_d,T_max);
        end
        
        % 记录每代的平均目标值
        objectives_history(gen,:) = mean(objectives);
        
        % 使用加权和作为适应度
        Fit = 0.4*objectives(:,1) - 0.3*objectives(:,2) - 0.3*objectives(:,3);
        
        % 选择操作
        [~, sort_idx] = sort(Fit, 'descend');
        f = f(sort_idx,:);
        
        % 交叉和变异操作（与第一阶段相同）
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
        
        for i=1:NP
            if rand < Pm
                j = randi(N);
                nf(i,j) = randi(M);
                nf(i,:) = apply_station_time_constraint(nf(i,:),a,d,T_max);
            end
        end
        
        f = nf;
    end
    
    % 计算最终的Pareto前沿
    objectives = zeros(NP,3);
    for np=1:NP
        objectives(np,1) = func1(f(np,:),M,N,a,d,T_max);
        objectives(np,2) = func4(f(np,:),M,a,d,O,S,T_max);
        objectives(np,3) = func3(f(np,:),original_f,a,original_a,d,original_d,T_max);
    end
    
    % 选择最终解
    [~, best_idx] = max(0.4*objectives(:,1) - 0.3*objectives(:,2) - 0.3*objectives(:,3));
    best_solution = f(best_idx,:);
    
    % 构造Pareto前沿（为了与其他算法保持一致的输出格式）
    [~, fronts] = non_dominated_sort(objectives);
    pareto_front = objectives(fronts{1},:);
    
    % 绘制两阶段优化过程
    figure('Name', '两阶段GA优化过程');
    subplot(3,1,1);
    plot(objectives_history(:,1));
    xlabel('迭代次数');
    ylabel('F1: 非远机位停靠率');
    title('第二阶段优化过程');
    
    subplot(3,1,2);
    plot(objectives_history(:,2));
    xlabel('迭代次数');
    ylabel('F2: 时间间隔');
    
    subplot(3,1,3);
    plot(objectives_history(:,3));
    xlabel('迭代次数');
    ylabel('F3: 重分配惩罚');
end

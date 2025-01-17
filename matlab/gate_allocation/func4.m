function result = func4(f, M, a, d, O, S, T_max)
    % 计算时间间隔最小化目标
    % f: 当前解（机位分配方案）
    % M: 机位数量
    % a: 到达时间
    % d: 离开时间
    % O: 机位开放时间
    % S: 机位关闭时间
    % T_max: 最大过站时间
    
    % 应用过站时间约束
    f = apply_station_time_constraint(f, a, d, T_max);
    
    total_interval = 0;
    count = 0;
    
    % 对每个机位计算相邻航班的时间间隔
    for gate = 1:M
        flights_at_gate = find(f == gate);
        if length(flights_at_gate) > 1
            % 按到达时间排序
            [~, sort_idx] = sort(a(flights_at_gate));
            flights_at_gate = flights_at_gate(sort_idx);
            
            % 计算相邻航班间隔
            for i = 1:length(flights_at_gate)-1
                interval = a(flights_at_gate(i+1)) - d(flights_at_gate(i));
                if interval > 0  % 只考虑正的时间间隔
                    total_interval = total_interval + interval;
                    count = count + 1;
                end
            end
        end
    end
    
    % 如果没有间隔可计算，返回一个大数
    if count == 0
        result = 1000;
    else
        % 返回平均时间间隔（越小越好）
        result = total_interval / count;
    end
end

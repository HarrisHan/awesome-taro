function result = func1(f, M, N, a, d, T_max)
    % 计算非远机位停靠率目标
    % f: 当前解（机位分配方案）
    % M: 机位数量
    % N: 航班数量
    % a: 到达时间
    % d: 离开时间
    % T_max: 最大过站时间
    
    % 应用过站时间约束
    f = apply_station_time_constraint(f, a, d, T_max);
    
    % 计算远机位使用数量
    remote_gates = f == 63 | f == 64;  % 假设63和64是远机位
    remote_count = sum(remote_gates);
    
    % 计算非远机位停靠率 (1 - 远机位使用率)
    result = 1 - (remote_count / N);
end

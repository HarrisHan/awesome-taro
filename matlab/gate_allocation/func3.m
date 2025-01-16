function result = func3(f, original_f, a, original_a, d, original_d, T_max)
    % f: current gate assignments
    % original_f: original gate assignments before delays
    % a: current arrival times
    % original_a: original arrival times before delays
    % d: current departure times
    % original_d: original departure times before delays
    % T_max: maximum transit time threshold
    
    % Apply station time constraint first (maintain consistency with other objectives)
    f = apply_station_time_constraint(f, a, d, T_max);
    
    N = length(f);
    
    % Calculate reassignment penalty (normalized by number of flights)
    reassignment_penalty = sum(f ~= original_f) / N;
    
    % Calculate delay penalty (normalized by maximum delay of 30 minutes)
    delay_penalty = sum(abs([a - original_a, d - original_d])) / (N * 30);
    
    % Combine penalties with equal weights
    result = (reassignment_penalty + delay_penalty) / 2;
end

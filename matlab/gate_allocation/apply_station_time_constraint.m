% 过站时间约束处理函数
function f = apply_station_time_constraint(f,a,d,T_max)
    % f 是航班到机位的分配情况，arrive 和 leave 是航班的到达和离开时间，T_max 是过站时间阈值
    N = length(f);  % 总航班数
    
    for i = 1:N
        % 计算航班的过站时间
        layover_time = d(i) - a(i);
        
        % 如果过站时间超过阈值 T_max，将该航班分配至远机位（63或64）
        if layover_time > T_max
            % 随机选择远机位（63或64）
            f(i) = 63 + randi([0, 1]);  % 63或64，randi([0, 1]) 随机生成 0 或 1
        end
    end
end
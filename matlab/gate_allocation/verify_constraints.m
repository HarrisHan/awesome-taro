function verify_constraints(solution, M, N, a, d, O, S, T_max, gnum, fi, gk)
    % 验证所有约束条件
    fprintf('开始验证约束条件...\n');
    
    % 1. 验证机位编号约束 (1-64)
    if any(solution < 1 | solution > M)
        error('错误：存在无效的机位编号');
    end
    fprintf('✓ 机位编号约束验证通过\n');
    
    % 2. 验证过站时间约束
    layover_times = d - a;
    remote_gates = solution == 63 | solution == 64;
    if any(layover_times > T_max & ~remote_gates)
        error('错误：过站时间超过T_max的航班未分配到远机位');
    end
    fprintf('✓ 过站时间约束验证通过\n');
    
    % 3. 验证时间间隔约束
    alpha = 15; % 同一机位最小间隔
    beta = 15;  % 同一组内最小间隔
    gamma = 5;  % 相邻组间最小间隔
    
    % 对每个机位检查时间冲突
    for gate = 1:M
        flights_at_gate = find(solution == gate);
        if length(flights_at_gate) > 1
            for i = 1:length(flights_at_gate)
                for j = i+1:length(flights_at_gate)
                    f1 = flights_at_gate(i);
                    f2 = flights_at_gate(j);
                    
                    % 检查同一机位时间间隔
                    if (a(f2) - d(f1) < alpha) && (a(f2) >= a(f1))
                        error('错误：同一机位的航班时间间隔小于alpha');
                    end
                end
            end
        end
    end
    fprintf('✓ 时间间隔约束验证通过\n');
    
    % 4. 验证机型匹配约束
    for i = 1:N
        gate_type = gk(solution(i));
        flight_type = fi(i);
        if gate_type < flight_type
            error('错误：机位类型与航班机型不匹配');
        end
    end
    fprintf('✓ 机型匹配约束验证通过\n');
    
    % 5. 验证分组约束
    for i = 1:N
        for j = i+1:N
            if gnum(solution(i)) == gnum(solution(j))
                % 同一组内航班
                if abs(a(i)-a(j)) < beta || abs(d(i)-d(j)) < beta
                    error('错误：同一组内航班时间间隔小于beta');
                end
            elseif abs(gnum(solution(i)) - gnum(solution(j))) == 1
                % 相邻组航班
                if abs(a(i)-a(j)) < gamma || abs(d(i)-d(j)) < gamma
                    error('错误：相邻组航班时间间隔小于gamma');
                end
            end
        end
    end
    fprintf('✓ 分组约束验证通过\n');
    
    fprintf('所有约束验证通过！\n');
    
    % 绘制甘特图进行可视化验证
    figure('Name', '约束验证可视化');
    hold on;
    colors = hsv(M);  % 为每个机位生成不同的颜色
    
    for i = 1:N
        gate = solution(i);
        rectangle('Position', [a(i), gate-0.4, d(i)-a(i), 0.8], ...
                 'FaceColor', colors(gate,:), ...
                 'EdgeColor', 'k');
        text(a(i), gate, num2str(i), 'FontSize', 8);
    end
    
    ylim([0 M+1]);
    xlim([min(a)-30 max(d)+30]);
    xlabel('时间 (分钟)');
    ylabel('机位编号');
    title('航班分配甘特图 (颜色表示不同机位)');
    grid on;
end

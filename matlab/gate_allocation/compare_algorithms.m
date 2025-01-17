function compare_algorithms(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d)
    % 加载各算法结果
    algorithms = {'EBNSGA-II', 'NSGA-II', 'PSO', 'Two-Phase-GA'};
    all_fronts = cell(length(algorithms), 1);
    all_solutions = cell(length(algorithms), 1);
    
    for i = 1:length(algorithms)
        result_file = ['results/' algorithms{i} '_result.mat'];
        if exist(result_file, 'file')
            data = load(result_file);
            all_fronts{i} = data.pareto_front;
            all_solutions{i} = data.best_solution;
        else
            warning(['未找到算法 ' algorithms{i} ' 的结果文件']);
            continue;
        end
    end
    
    % 绘制帕累托前沿对比
    figure('Name','算法对比');
    
    % 3D散点图
    subplot(2,2,1);
    hold on;
    for i = 1:length(algorithms)
        if ~isempty(all_fronts{i})
            scatter3(all_fronts{i}(:,1), all_fronts{i}(:,2), all_fronts{i}(:,3), 'filled', 'DisplayName', algorithms{i});
        end
    end
    xlabel('F1: 非远机位停靠率');
    ylabel('F2: 时间间隔');
    zlabel('F3: 重分配惩罚');
    title('帕累托前沿对比');
    legend('Location','best');
    grid on;
    
    % F1-F2投影
    subplot(2,2,2);
    hold on;
    for i = 1:length(algorithms)
        if ~isempty(all_fronts{i})
            scatter(all_fronts{i}(:,1), all_fronts{i}(:,2), 'filled', 'DisplayName', algorithms{i});
        end
    end
    xlabel('F1: 非远机位停靠率');
    ylabel('F2: 时间间隔');
    title('F1-F2平面投影');
    legend('Location','best');
    grid on;
    
    % F1-F3投影
    subplot(2,2,3);
    hold on;
    for i = 1:length(algorithms)
        if ~isempty(all_fronts{i})
            scatter(all_fronts{i}(:,1), all_fronts{i}(:,3), 'filled', 'DisplayName', algorithms{i});
        end
    end
    xlabel('F1: 非远机位停靠率');
    ylabel('F3: 重分配惩罚');
    title('F1-F3平面投影');
    legend('Location','best');
    grid on;
    
    % F2-F3投影
    subplot(2,2,4);
    hold on;
    for i = 1:length(algorithms)
        if ~isempty(all_fronts{i})
            scatter(all_fronts{i}(:,2), all_fronts{i}(:,3), 'filled', 'DisplayName', algorithms{i});
        end
    end
    xlabel('F2: 时间间隔');
    ylabel('F3: 重分配惩罚');
    title('F2-F3平面投影');
    legend('Location','best');
    grid on;
    
    % 计算和显示性能指标
    fprintf('算法性能对比:\n');
    fprintf('=========================================\n');
    fprintf('算法\t\tF1均值\t\tF2均值\t\tF3均值\n');
    for i = 1:length(algorithms)
        if ~isempty(all_fronts{i})
            fprintf('%s\t%.4f\t%.4f\t%.4f\n', algorithms{i}, mean(all_fronts{i}));
        end
    end
end

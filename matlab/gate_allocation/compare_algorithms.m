function compare_algorithms(M, N, a, d, O, S, T_max, NP, G, Pc, Pm, original_f, original_a, original_d)
    % 运行各算法
    [ebnsga2_best, ebnsga2_front] = main(M,N,a,d,O,S,T_max,NP,G,Pc,Pm,original_f,original_a,original_d);
    [nsga2_best, nsga2_front] = nsga2(M,N,a,d,O,S,T_max,NP,G,Pc,Pm,original_f,original_a,original_d);
    [pso_best, pso_front] = pso(M,N,a,d,O,S,T_max,NP,G,original_f,original_a,original_d);
    
    % 绘制帕累托前沿对比
    figure('Name','算法对比');
    
    % 3D散点图
    subplot(2,2,1);
    scatter3(ebnsga2_front(:,1),ebnsga2_front(:,2),ebnsga2_front(:,3),'filled','DisplayName','EBNSGA-II');
    hold on;
    scatter3(nsga2_front(:,1),nsga2_front(:,2),nsga2_front(:,3),'filled','DisplayName','NSGA-II');
    scatter3(pso_front(:,1),pso_front(:,2),pso_front(:,3),'filled','DisplayName','PSO');
    xlabel('F1: 非远机位停靠率');
    ylabel('F2: 时间间隔');
    zlabel('F3: 重分配惩罚');
    title('帕累托前沿对比');
    legend('Location','best');
    grid on;
    
    % F1-F2投影
    subplot(2,2,2);
    scatter(ebnsga2_front(:,1),ebnsga2_front(:,2),'filled','DisplayName','EBNSGA-II');
    hold on;
    scatter(nsga2_front(:,1),nsga2_front(:,2),'filled','DisplayName','NSGA-II');
    scatter(pso_front(:,1),pso_front(:,2),'filled','DisplayName','PSO');
    xlabel('F1: 非远机位停靠率');
    ylabel('F2: 时间间隔');
    title('F1-F2平面投影');
    legend('Location','best');
    grid on;
    
    % F1-F3投影
    subplot(2,2,3);
    scatter(ebnsga2_front(:,1),ebnsga2_front(:,3),'filled','DisplayName','EBNSGA-II');
    hold on;
    scatter(nsga2_front(:,1),nsga2_front(:,3),'filled','DisplayName','NSGA-II');
    scatter(pso_front(:,1),pso_front(:,3),'filled','DisplayName','PSO');
    xlabel('F1: 非远机位停靠率');
    ylabel('F3: 重分配惩罚');
    title('F1-F3平面投影');
    legend('Location','best');
    grid on;
    
    % F2-F3投影
    subplot(2,2,4);
    scatter(ebnsga2_front(:,2),ebnsga2_front(:,3),'filled','DisplayName','EBNSGA-II');
    hold on;
    scatter(nsga2_front(:,2),nsga2_front(:,3),'filled','DisplayName','NSGA-II');
    scatter(pso_front(:,2),pso_front(:,3),'filled','DisplayName','PSO');
    xlabel('F2: 时间间隔');
    ylabel('F3: 重分配惩罚');
    title('F2-F3平面投影');
    legend('Location','best');
    grid on;
    
    % 计算和显示性能指标
    fprintf('算法性能对比:\n');
    fprintf('=========================================\n');
    fprintf('算法\t\tF1均值\t\tF2均值\t\tF3均值\n');
    fprintf('EBNSGA-II\t%.4f\t%.4f\t%.4f\n', mean(ebnsga2_front));
    fprintf('NSGA-II\t\t%.4f\t%.4f\t%.4f\n', mean(nsga2_front));
    fprintf('PSO\t\t%.4f\t%.4f\t%.4f\n', mean(pso_front));
end

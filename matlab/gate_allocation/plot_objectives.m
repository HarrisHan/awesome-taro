function plot_objectives(objectives, gen)
    % Plot the convergence of each objective
    figure(2)
    subplot(3,1,1)
    plot(objectives(:,1))
    xlabel('迭代次数')
    ylabel('F1: 非远机位停靠率')
    title(['第' num2str(gen) '代'])
    
    subplot(3,1,2)
    plot(objectives(:,2))
    xlabel('迭代次数')
    ylabel('F2: 时间间隔')
    
    subplot(3,1,3)
    plot(objectives(:,3))
    xlabel('迭代次数')
    ylabel('F3: 重分配惩罚')
    
    % Plot Pareto front
    figure(3)
    scatter3(objectives(:,1), objectives(:,2), objectives(:,3), 'filled')
    xlabel('F1: 非远机位停靠率')
    ylabel('F2: 时间间隔')
    zlabel('F3: 重分配惩罚')
    title('Pareto前沿')
    grid on
    
    drawnow
end

function [ranks, fronts] = non_dominated_sort(objectives)
    % Input: objectives - N x M matrix where N is population size and M is number of objectives
    % Output: ranks - Nx1 vector containing rank of each solution
    %         fronts - cell array containing indices of solutions in each front
    
    N = size(objectives, 1); % population size
    domination_count = zeros(N, 1); % number of solutions dominating solution i
    dominated_solutions = cell(N, 1); % set of solutions dominated by solution i
    ranks = zeros(N, 1);
    fronts = cell(1);
    front_index = 1;
    
    % Compare each solution with every other solution
    for i = 1:N
        for j = i+1:N
            p = objectives(i,:);
            q = objectives(j,:);
            
            % Check if p dominates q
            if all(p <= q) && any(p < q)
                dominated_solutions{i} = [dominated_solutions{i}, j];
                domination_count(j) = domination_count(j) + 1;
            % Check if q dominates p
            elseif all(q <= p) && any(q < p)
                dominated_solutions{j} = [dominated_solutions{j}, i];
                domination_count(i) = domination_count(i) + 1;
            end
        end
        
        % If solution i belongs to first front
        if domination_count(i) == 0
            ranks(i) = 1;
            fronts{1} = [fronts{1}, i];
        end
    end
    
    % Find subsequent fronts
    while ~isempty(fronts{front_index})
        next_front = [];
        for i = fronts{front_index}
            for j = dominated_solutions{i}
                domination_count(j) = domination_count(j) - 1;
                if domination_count(j) == 0
                    ranks(j) = front_index + 1;
                    next_front = [next_front, j];
                end
            end
        end
        front_index = front_index + 1;
        fronts{front_index} = next_front;
    end
    
    % Remove empty front if exists
    if isempty(fronts{end})
        fronts(end) = [];
    end
end

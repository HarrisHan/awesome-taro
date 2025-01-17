function distances = crowding_distance(objectives, front)
    % Input: objectives - N x M matrix where N is population size and M is number of objectives
    %        front - indices of solutions in the current front
    % Output: distances - crowding distance for each solution in the front
    
    front_size = length(front);
    if front_size <= 2
        distances = inf(front_size, 1);
        return;
    end
    
    num_objectives = size(objectives, 2);
    distances = zeros(front_size, 1);
    
    % Calculate crowding distance for each objective
    for m = 1:num_objectives
        % Get values for current objective
        values = objectives(front, m);
        
        % Sort solutions by current objective
        [sorted_values, sorted_indices] = sort(values);
        
        % Set boundary points to infinity
        distances(sorted_indices(1)) = inf;
        distances(sorted_indices(end)) = inf;
        
        % Calculate distances for intermediate points
        obj_range = sorted_values(end) - sorted_values(1);
        if obj_range == 0
            obj_range = 1; % Avoid division by zero
        end
        
        for i = 2:front_size-1
            distances(sorted_indices(i)) = distances(sorted_indices(i)) + ...
                (sorted_values(i+1) - sorted_values(i-1)) / obj_range;
        end
    end
end

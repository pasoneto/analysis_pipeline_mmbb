function result = createTapObject(filename)
    % createUserStimulusStruct - Reads a CSV file and organizes data into a structure
    %
    % Syntax:
    %   result = createUserStimulusStruct(filename)
    % Input:
    %   filename - String, name of the CSV file to read
    %
    % Output:
    %   result - A structure array where each element corresponds to a 
    %            unique combination of userID and stimulus. Each element 
    %            has the fields:
    %            - userID: Unique user ID
    %            - stimulus: Unique stimulus ID
    %            - taps: Array of taps for the combination
    %            - rtAudio: Array of rtAudio for the combination

    % Read the CSV file into a table
    data = readtable(filename);

    % Get unique userID and stimulus pairs
    uniqueUsers = unique(data.userID);
    uniqueStimuli = unique(data.stimulus);

    % Initialize the structure array
    result = [];

    % Populate the structure array
    idx = 0; % Index for the structure array
    for i = 1:numel(uniqueUsers)
        for j = 1:numel(uniqueStimuli)
            % Filter rows for the current userID and stimulus
            currentUser = uniqueUsers{i};
            currentStimulus = uniqueStimuli{j};

            % Use strcmp to compare cell array strings
            rows = strcmp(data.userID, currentUser) & strcmp(data.stimulus, currentStimulus);
            
            % Remove path and file extension
            [p, currentStimulus, ext] = fileparts("./songs/movementTapAudio/modifiedAudio/name__11 - metronome_const_tempo__stretchfactor__1_25__0_75188__1.mp3");

            % If there are matching rows, extract the relevant fields
            if any(rows)
                idx = idx + 1;
                result = [result, TapClass(currentUser, currentStimulus, data.taps(rows), data.rtAudio(rows))]
            end
        end
    end

    % Handle the case where no matching rows exist
    if idx == 0
        result = [];
    end
end

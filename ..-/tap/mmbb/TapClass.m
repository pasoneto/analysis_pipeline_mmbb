classdef TapClass
    properties
        userID
        stimulus
        taps
        rtAudio
        tempoChanges
        bpms
        beatTimes
    end
    
    methods
        function obj = TapClass(userID, stimulus, taps, rtAudio, tempoChanges, bpms, beatTimes)
            obj.userID = userID;
            obj.stimulus = stimulus;
            obj.taps = taps;
            obj.rtAudio = rtAudio;

            if nargin == 7
              if length(tempoChanges)+1 ~= length(bpms)                %number of tempo changes needs to be equal to number of BPMs + 1
                error('Number of tempo changes and bpms dont match!');
              end

              obj.tempoChanges = tempoChanges;
              obj.bpms = bpms;
              obj.beatTimes = beatTimes;
              
              %If tempo changes and bpms are provided, trial is either metronome or song,
              %so taps and beat times should be segmented
              obj.taps = TapClass.divideTapByTempoChanges(taps, tempoChanges);
              obj.beatTimes = TapClass.divideTapByTempoChanges(beatTimes, tempoChanges);
            else
              obj.tempoChanges = [];
              obj.bpms = [];
              obj.beatTimes = [];
            end
        end
        
        % Compute median of inter tap interval
        function medianDiff = iti(obj, removeFirstN, n)

            %If not given value to filter out first N beats
            if nargin < 3
              removeFirstN = false;
              n = 0;
            elseif nargin == 2 & removeFirstN & iscell(obj.taps)
              n = 3;
              disp("No value of N given. Defaulting to 3")
            else
              disp("Tap format not recognized")
            end

            if iscell(obj.taps)
              taps = cellfun(@(x, y) TapClass.removeFirstBeats(x, y, n, removeFirstN), obj.taps, obj.beatTimes, 'UniformOutput', false);
              medianDiff = cellfun(@(x) TapClass.computeMedianDifferenceInternal(x), taps);
            else %Direct computation of ITI if taps is a single array (self paced tasks)
              medianDiff = TapClass.computeMedianDifferenceInternal(obj.taps);
            end

        end

        %Compute variability
        function varScore = variability(obj, removeFirstN, n)
            if nargin == 1 %If not given value to filter out first N beats
              removeFirstN = false;
              n = 0;
            elseif nargin == 2 & removeFirstN == true & iscell(obj.taps)
              n = 3;
              disp("No value of N given. Defaulting to 3")
            end
           
            if iscell(obj.taps)
              taps = cellfun(@(x, y) TapClass.removeFirstBeats(x, y, n, removeFirstN), obj.taps, obj.beatTimes, 'UniformOutput', false);
              varScore = cellfun(@(x) TapClass.variabilityInternal(x), taps);
            else
              varScore = TapClass.variabilityInternal(obj.taps);
            end
        end

        %Compute variability
        function driftCoeff = drift(obj, n, removeFirstN)
            if nargin == 1
              removeFirstN = false;
              n = 0
            end

            if iscell(obj.taps) %If input is a list of lists (cell array)
              taps = cellfun(@(x, y) TapClass.removeFirstBeats(x, y, n, removeFirstN), obj.taps, obj.beatTimes, 'UniformOutput', false);
              driftCoeff = cellfun(@(x) TapClass.driftInternal(x), taps);
            else  %If input is a single array
              driftCoeff = TapClass.driftInternal(obj.taps);
            end

        end

        %Compute Kuramoto
        function [orderParams, phaseShifts] = kuramoto(obj, n, removeFirstN)
            if nargin == 1 %If not given value to filter out first N beats
              disp("nargin is 1")
              removeFirstN = false;
              n = 0;
            elseif nargin == 2 & removeFirstN & iscell(obj.taps)
              n = 3;
              disp("No value of N given. Defaulting to 3")
            end

            if isempty(obj.beatTimes)
              error("No beat times provided!")
            end
            
            if iscell(obj.taps)
              taps = cellfun(@(x, y) TapClass.removeFirstBeats(x, y, n, removeFirstN), obj.taps, obj.beatTimes, 'UniformOutput', false);
              [orderParams, phaseShifts] = cellfun(@(x, y) TapClass.kuramotoInternal(x, y), taps, num2cell(obj.bpms), 'UniformOutput', false);
            else
              [orderParams, phaseShifts] = TapClass.kuramotoInternal(obj.taps, num2cell(obj.bpms));
            end
        end 

        function [bpm, metricLevel, confidenceMetric] = findMetricLevel(obj, removeFirstN, n)
            if nargin == 1 %If not given value to filter out first N beats
              removeFirstN = false;
              n = 0;
              disp("No filtering of N first taps")
            elseif nargin == 2 & removeFirstN == true & iscell(obj.taps)
              n = 3;
              disp("No value of N given. Defaulting to 3")
            end

            if isempty(obj.beatTimes)
              error("No beat times provided!")
            end

            if iscell(obj.taps)
                taps = cellfun(@(x, y) TapClass.removeFirstBeats(x, y, n, removeFirstN), obj.taps, obj.beatTimes, 'UniformOutput', false);
                [bpm, metricLevel, confidenceMetric] = cellfun(@(x, y) TapClass.findMetricLevelInternal(x, y), taps, num2cell(obj.bpms), 'UniformOutput', false);
            else
                taps = TapClass.removeFirstBeats(obj.taps, obj.beatTimes, n, removeFirstN);
                [bpm, metricLevel, confidenceMetric] = TapClass.findMetricLevelInternal(taps, obj.bpms);
            end
        end 
    end

    methods (Static)
        %Divide taps according to tempo 
        function windows = divideTapByTempoChanges(taps, tempoChanges)
            if isempty(tempoChanges)
              error("No tempo changes provided for this stimulus")
            end

            % Ensure tempoChanges are sorted
            tempoChanges = sort(tempoChanges);
            taps = sort(taps);
             
            windows = {taps(taps <= tempoChanges(1))};  % Initialize cell array and get first case

            % Loop through the tempoChanges to create windows
            for i = 1:length(tempoChanges)-1
                lowerBound = tempoChanges(i);
                upperBound = tempoChanges(i+1);
                
                % Filter taps within the current window
                window = taps(taps > lowerBound & taps <= upperBound);
                windows{end+1} = window;  % Add the window to the cell array
            end
            
            % Handle the last window (for taps greater than the last tempo change)
            lastWindow = taps(taps > tempoChanges(end));
            windows{end+1} = lastWindow;  % Add the last window to the cell array
        end

        %When tempo change occurs, remove all tapps ocurring at or before the time of the Nth beat.
        function filteredTaps = removeFirstBeats(taps, beatTimes, n, execute)
            if isempty(beatTimes)
              error("No beat times provided for this stimulus")
            end

            if execute == true
              % Ensure tempoChanges are sorted
              beatTimes = sort(beatTimes);
              taps = sort(taps);
              %Find time of nth beat
              lowerBound = beatTimes(n);
                  
              % Filter taps within before Nth beat
              filteredTaps = taps(taps > lowerBound);
            else
              filteredTaps = taps;
            end
        end


        % Static helper method to compute median
        function medianDiff = computeMedianDifferenceInternal(taps)
            if numel(taps) > 1
                % Compute differences
                diffTaps = diff(taps);
                medianDiff = median(diffTaps);
            else
                % Handle cases where there are not enough elements
                medianDiff = NaN;
                warning('Not enough elements in taps to compute differences.');
            end
        end
        
        % Remove outliers using the IQR*1.5 method
        function nonOutliers = removeOutliers(data)
            Q1 = quantile(data, 0.25);
            Q3 = quantile(data, 0.75);

            IQR = Q3 - Q1;

            lowerBound = Q1 - 1.5 * IQR;
            upperBound = Q3 + 1.5 * IQR;

            nonOutliers = data(data >= lowerBound & data <= upperBound);
        end

        % Static helper method to compute variability
        function varScore = variabilityInternal(taps)
            if numel(taps) > 1
                % Calculate differences between consecutive taps
                diffTaps = diff(taps);
                diffTaps = TapClass.removeOutliers(diffTaps);

                % Compute the 10th and 90th quantiles of the differences
                q10 = quantile(diffTaps, 0.1);
                q90 = quantile(diffTaps, 0.9);
                
                % Compute the range between the quantiles
                range = q90 - q10;
                
                % Get the median difference
                medianDiff = TapClass.computeMedianDifferenceInternal(taps);
                
                % Calculate the variability score
                if medianDiff ~= 0
                    varScore = range / medianDiff;
                else
                    varScore = NaN;
                    warning('Median difference is zero; variability is undefined.');
                end
            else
                varScore = NaN;
                warning('Not enough elements in taps to compute variability.');
            end
        end

        % Helper function to compute the drift coefficient by regressing differences in taps on their indices
        function driftCoeff = driftInternal(taps)
            if numel(taps) > 1
                % Calculate differences between consecutive taps
                diffTaps = diff(taps);
                
                % Create an index vector for regression
                indices = (1:numel(diffTaps))';
                
                % Perform linear regression using polyfit
                [coeffs, S] = polyfit(indices, diffTaps, 1);
                
                % Extract the slope (coefficient of drift)
                driftCoeff = coeffs(1);
                
            else
                driftCoeff = NaN;
                warning('Not enough elements in taps to compute drift and R^2.');
            end
        end
        
        % Kuramoto model
        function [o, a] = kuramotoInternal(taps, bpmOriginal)
            if numel(taps) > 1
              %ibi = TapClass.computeMedianDifferenceInternal(beatTimes); %Original IBI
              [metricLevel, bpmPerformed, confidenceMetric] = TapClass.findMetricLevelInternal(taps, bpmOriginal);
              ibi = 60000/bpmPerformed;
              N = length(taps);
	      rv=sum(exp(i*2*pi*(taps-beatTimes(1))/ibi))/N;
              o = abs(rv); %order parameter
              a = angle(rv); %phase shift (in radians)
              disp("Calculated kuramoto for metric level at " + bpmPerformed + " BPMs, (" + metricLevel + ") " + "and confidence of: " + confidenceMetric)
            else
              o = NaN 
              a = NaN
            end
        end

      function [metricLevel, bpm, confidenceMetric] = findMetricLevelInternal(taps, bpmOriginal)
        if numel(taps) > 1
          itiMS = TapClass.computeMedianDifferenceInternal(taps);
          bpm_performed = 60000/itiMS;
          
          %Possible BPMs and corresponding metrical levels
          bpm_values = [bpmOriginal / 2, bpmOriginal, bpmOriginal * 2];
          metricLevels = ["half", "original", "double"];

          % Compute absolute differences and sort them while keeping indexes
          [differences, sorted_indices] = sort(abs(bpm_values - bpm_performed));

          % Sort metrical and bpms level based on difference values
          metricLevels = metricLevels(sorted_indices);
          bpm_values = bpm_values(sorted_indices);

          % Get the closest metricLevel and corresponding BPM
          metricLevel = metricLevels(1);
          bpm = bpm_values(1);
            
          %Get confidence for current metric level. The closest to each other, the lowest the confidence. 
          confidenceMetric = 1 - (differences(1)/differences(2));

        else
          metricLevel = NaN;
          bpm = NaN;
          confidenceMetric = NaN;
        end
      end

    end
end

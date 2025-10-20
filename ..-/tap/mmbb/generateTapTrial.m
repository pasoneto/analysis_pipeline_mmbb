function [taps, tempoChanges, bpmList, beatTimes] = generateTapTrial(bpmList, nBeatsList, noise, phaseShift)
  bpm = 120;
  nBeats = 20;
  taps = [];
  beatTimes = [];
  tempoChanges = [];
  initTime = 0;
  for k=1:length(bpmList)
    bpm = bpmList(k);
    nBeats = nBeatsList(k);
    ibi = 60000/bpm;
    [tap, beatTime] = generateBeatInternal(bpm, nBeats, initTime);
    tap = tap(2:end);  % Remove the first tap to avoid repeating the initTime
    noiseTap = (noise*ibi) * rand(length(tap), 1)';
    tap = tap + noiseTap;
    beatTime = beatTime(2:end);  % Remove the first tap to avoid repeating the initTime
    initTime = tap(end);     % Update initTime to the last tap time
    tempoChange = initTime;
    tempoChanges = [tempoChanges, tempoChange];
    beatTimes = vertcat(beatTimes, beatTime');
    taps = vertcat(taps, tap');
  end
  tempoChanges = tempoChanges(1:length(tempoChanges)-1); %Remove last tempo change, because stimulus ended
end

function [taps, beatTimes] = generateBeatInternal(bpm, nBeats, initTime)
  ibi = 60000 / bpm;  % Calculate inter-beat interval
  tap = initTime + (0:nBeats) * ibi;  % Calculate tap times for the current segment
  beatTimes = initTime + (0:nBeats) * ibi;  % Calculate tap times for the current segment
  taps = beatTimes;
end


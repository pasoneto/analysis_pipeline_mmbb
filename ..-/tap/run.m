addpath('./mmbb/');

joe = TapClass("joe", "song1", taps, taps, tempoChanges, bpmList, beatTimes);

%%Create object
removeFirstN = true
n = 3

%%Check id
joe.userID
joe.stimulus
joe.taps

%%Compute features
joe.iti(removeFirstN, n)
joe.variability(removeFirstN, n)
joe.drift(removeFirstN, n)
[ord, ang] = joe.kuramoto(removeFirstN, n);
[metric_level, bpm, confidence] = joe.findMetricLevel(removeFirstN, n) %Finds the closest metric level to participant's median ITI

%Checking bpms
a = joe.iti()
60000/a(1)
60000/a(2)
60000/a(3)

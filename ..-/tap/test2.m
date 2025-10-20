addpath('/Users/pdealcan/Documents/github/CoE_Neto/code/MMBB/analisys_pipeline/mmbb/');

%%Generate tap trial with tempo change
bpms = [60, 120, 82];  %BPM per segment
nTaps = [10, 100, 100]; %nTaps per tempo segment
noise = 0.5 %Generates taps with error of uniform distribution between 0 and noise*IBI

%Simulate tap trials
[taps, tempoChanges, bpmList, beatTimes] = generateTapTrial(bpms, nTaps, noise);

%%Tap objects have the following properties
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

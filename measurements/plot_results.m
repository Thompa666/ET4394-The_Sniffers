%% Import channels
% Before reading channels file into matlab, first strip all unneccesary columns:
% cut -d , -f 2,3 channel_input.csv > channel_input_chanphy.csv

% Read the CSV data in matrix, note the row and column offset
M = csvread("wsn_lecture-1dot75h_21_2_2018-channel_results_chanphy.csv",1,0);
%% Import router phy
% Before reading beacon file for phy usage into matlab, first stripp all unneccesary columns:
% cut -d , -f 4,6 beacon_input.csv > beacon_input_phytrans.csv
% Then strip duplicates:
% sort -u beacon_input_phytrans.csv -o beacon_input_phytrans_unique.csv

% Read the CSV data in matrix, note the row and column offset
M2 = csvread("wsn_lecture-1dot75h_21_2_2018_beacon_results_phy_unique.csv",1,1);

%% Import router channel and phy
% Before reading beacon file for phychan usage into matlab, first stripp all unneccesary columns:
% cut -d , -f 1,2,6 beacon_input.csv > beacon_input_phychan.csv
% Then strip duplicates:
% sort -u beacon_input_phychan.csv -o beacon_input_phychan_unique.csv

% Read the CSV data in matrix, note the row and column offset
M3 = csvread("wsn_lecture-1dot75h_21_2_2018_beacon_results_phychan_unique.csv",0,1);

%% Plot message channel distribution
% Make a histogram of the channels
% This categorial trick enables that only channels which have been measured 
% will be displayed on the x-axis of the histogram
C = categorical(M(:,1),unique(M(:,1)),cellstr(num2str(unique(M(:,1)))));
subplot(3,2,[1,2]);
histogram(C)
title('message channel distribution');

%% plot message phy type distribution
% Get all phy types
pT = unique(M(:,2))

% String array of phy types
pST = [];

% Loop through phy types and assign real name for histogram
for i = 1:size(pT)
    switch pT(i)
        case 1
            pST = [pST, "FHSS"]
        case 2
            pST = [pST, "IR"]
        case 3
            pST = [pST, "DSSS"]
        case 4
            pST = [pST, "b"]
        case 5
            pST = [pST, "a"]
        case 6
            pST = [pST, "g"]
        case 7
            pST = [pST, "n"]
        case 8
            pST = [pST, "ac"]
        case 9
            pST = [pST, "ad"]
        otherwise
            disp("?")
    end
end

% Make histogram om PHY type
P = categorical(M(:,2),unique(M(:,2)),cellstr(pST));
subplot(3,2,3);
histogram(P)
title('message phy type distribution');

%% Plot router phy type distribution
% Get all phy types
pT = unique(M2(:,1))

% String array of phy types
pST = [];

% Loop through phy types and assign real name for histogram
for i = 1:size(pT)
    switch pT(i)
        case 1
            pST = [pST, "FHSS"]
        case 2
            pST = [pST, "IR"]
        case 3
            pST = [pST, "DSSS"]
        case 4
            pST = [pST, "b"]
        case 5
            pST = [pST, "a"]
        case 6
            pST = [pST, "g"]
        case 7
            pST = [pST, "n"]
        case 8
            pST = [pST, "ac"]
        case 9
            pST = [pST, "ad"]
        otherwise
            disp("?")
    end
end

B = categorical(M2(:,1),unique(M2(:,1)),cellstr(pST));
subplot(3,2,4);
histogram(B)
title('router phy type distribution');

%% Plot beacon channel over router type distribution


% Get indices of n-type routers (7) and ac-type routers (8)
ind7 = M3(:,2) == 7;
ind8 = M3(:,2) == 8;

% Create matrices with those indices
A7 = M3(ind7,:);
A8 = M3(ind8,:);

A7C = categorical(A7(:,1),unique(A7(:,1)),cellstr(num2str(unique(A7(:,1)))));
subplot(3,2,5)
histogram(A7C)
title('beacon channel distribution n-type router');

A8C = categorical(A8(:,1),unique(A8(:,1)),cellstr(num2str(unique(A8(:,1)))));
subplot(3,2,6)
histogram(A8C)
title('beacon channel distribution ac-type router');

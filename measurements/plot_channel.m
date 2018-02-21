% Read the CSV data in matrix, note the row and column offset
% Make sure eliminate the mac names (move them to the first column)
M = csvread("channel_results_boris_home_21-02.csv",1,1);

% Make a histogram of the channels
% This categorial trick enables that only channels which have been measured 
% will be displayed on the x-axis of the histogram
C = categorical(M(:,1),unique(M(:,1)),cellstr(num2str(unique(M(:,1)))));
figure
histogram(C)

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
figure
histogram(P)
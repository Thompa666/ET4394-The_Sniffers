% Read the CSV data in matrix, note the row and column offset
% Make sure eliminate the mac names (move them to the first column)
M = csvread("channel_results_boris_home_21-02.csv",1,1)

% Make a histogram of the channels
% This categorial trick enables that only channels which have been measured 
% will be displayed on the x-axis of the histogram
C = categorical(M(:,1),unique(M(:,1)),cellstr(num2str(unique(M(:,1)))))
histogram(C)
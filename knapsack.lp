\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  x[0] + 6 x[1] + 8 x[2] + 9 x[3] + 6 x[4] + 7 x[5] + 3 x[6] + 2 x[7]
   + 6 x[8]
Subject To
 knapsack-w: x[0] + 3 x[1] + 6 x[2] + 7 x[3] + 5 x[4] + 9 x[5] + 4 x[6]
   + 8 x[7] + 5 x[8] <= 1
 knapsack-v: x[0] + 3 x[1] + 2 x[2] + 9 x[3] + x[4] + 4 x[5] + 2 x[6]
   + 4 x[7] + 7 x[8] <= 1
 binaryCut1: x[0] - x[1] - x[2] - x[3] - x[4] - x[5] - x[6] - x[7] - x[8]
   <= 0
Bounds
Binaries
 x[0] x[1] x[2] x[3] x[4] x[5] x[6] x[7] x[8]
End

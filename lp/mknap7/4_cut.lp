\ENCODING=ISO-8859-1
\Problem name: mknap7_cut_n4

Maximize
 obj1: 5 x0 + 4 x1 + 6 x2 + 5 x3
Subject To
 c0:    5 x0 + 10 x1 + 7 x2 + 6 x3 + s0 <= 14
 c1:    7 x0 + 8 x1 + 10 x2 + 7 x3 + s1 <= 10
 c2:    34 x0 + x1 + 4 x2 + 75 x3 + s2 <= 23
 c3:    5 x0 + x1 + 4 x2 + 12 x3 + s3 <= 35
 cut_1: 36 x0 + 3 x1 + 7 x2 + 76 x3 <= 25
 cut_2: 8 x0 + 7 x1 + 10 x2 + 9 x3 <= 10
 cut_3: 34 x0 + x1 + 5 x2 + 74 x3 <= 23
 cut_4: 36 x0 + 5 x1 + 10 x2 + 74 x3 <= 27
Bounds
 0 <= x0 <= 1
 0 <= x1 <= 1
 0 <= x2 <= 1
 0 <= x3 <= 1
End

"""
Analyze all 500 unicorn seals from Jamison's Appendix 7.1 (all sites combined)
Using ACTUAL offering stand (STAND column) frequencies - unconstrained analysis
"""

from collections import Counter
import numpy as np
from scipy.stats import powerlaw, expon, kstest
import matplotlib.pyplot as plt

# Complete table from Appendix 7.1 (all 500 seals)
full_table = """AD1 Allahdino 10 6 9 1 4 n/a n/a n/a n/a n/a n/a
AD2 Allahdino n/a n/a 10 4 4 12 n/a 1 n/a n/a n/a
AD3 Allahdino 2 24 10 1 4 12 n/a 1 1 9 44
AD4 Allahdino 10 6 4 1 4 12 2 1 1 9 40
AD5 Allahdino n/a 13 11 1 4 12 n/a 1 n/a 9 n/a
B1 Banawali 1 36 23 5 39 8 3 1 6 10 50
B2 Banawali 1 29 3 1 10 11a 3 1 6 10 28a
B3 Banawali 23 37 26 1 40 27 2 1 20 16 52
BLK1 Balakot 1 15 3 1 30 11 n/a n/a n/a n/a n/a
BLK2 Balakot 1 15 3 1 28b 11 2 n/a 5 5 n/a
BLK3 Balakot 7 39 11 4 2 12 4 1 1 5 54
BLK4 Balakot n/a 19 n/a 1 28 2 11 1 4 5 53
BSR 2037 Bagasra 9 25 11 2 21 22 4 5 25 n/a 25
BSR 5555 Bagasra n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a 101
BSR 6719 Bagasra 39 7 1 1 42 12 13 17 24 1 102
BSR 6952 Bagasra n/a n/a n/a n/a 20 15 2 18 37 3 103
BSR 7197 Bagasra 3 34 11 4 43 7 2 1 24 10 104
BSR 7368 Bagasra 21 45 14 2 20 21 14 1 1 12 n/a
BSR 8288 Bagasra 27 34 11 4 10 7 2 1 24 10 104
C1 Chanhu-daro n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
C10 Chanhu-daro 6 8 7 1 9 13 9 1 n/a 6 17
C11 Chanhu-daro n/a 34 n/a 1 n/a 2 6 n/a n/a 5 n/a
C12 Chanhu-daro n/a 4 7 n/a 33 23 n/a 1 10 1 44
C13 Chanhu-daro 9 27 13 1 28b 2 n/a 1 19 n/a 31
C14 Chanhu-daro n/a 35 18 1 33 15 3 2 17 1 n/a
C15 Chanhu-daro n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
C16 Chanhu-daro 2 8 4 1 28c 2 2 1 10 5 25
C17 Chanhu-daro 10 14 19 1 34 15 n/a 6 20 11 44
C18 Chanhu-daro n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
C19 Chanhu-daro n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
C2 Chanhu-daro 20 10 10 1 2 23 4 1 14 5 14
C20 Chanhu-daro 5 25 4 1 28b 2 11 6 12 9 25
C21 Chanhu-daro n/a 13 16 1 13 16 2 1 10 5 25
C3 Chanhu-daro 6 10 16 1 9 1 n/a 1 15 5 14
C4 Chanhu-daro n/a 27 n/a 2 4 10b 7 1 26 1 n/a
C5 Chanhu-daro 1 33 3 1 10 11 2 5 4 14 15
C6 Chanhu-daro n/a n/a 3 1 30 2 n/a n/a n/a 14 n/a
C7 Chanhu-daro n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
C8 Chanhu-daro 7 15 16 1 9 12 9 1 6 5 40
C9 Chanhu-daro 7 12 16 1 9 12 9 1 22 5 43
DHR-345 Dholavira 7 29 17 1 10 1 22 1 1 9 114
DHR-346 Dholavira 21 44 1 1 42 12 4 1 1 1 32
DHR-347 Dholavira 1 28 17 1 20 7 2 5 24 14 10
DHR-348 Dholavira 2 15 15 1 9 1 2 9 1 9 n/a
DHR-349 Dholavira 16 7 1 1 9 12 n/a 1 1 1 81
DLV-1 Dholavira n/a 18 1 1 17 7 n/a 2 6 6 4a
FMA1 Farmana 16 52 1 1 14 7 14 2 12 1 105
FMA2 Farmana 23 36 19 1 47 n/a 7 8 29 19 52
H1 Harappa 11 16 1 1 15 1 1 1 9 12 20
H10 Harappa 14 17 15 5 25g 29b 2 4 23 13 57
H102 Harappa 16 13 1 1 3 13 2 9 1 1 53
H1020 Harappa n/a n/a n/a n/a n/a 10 17 4 23 13 1b
H1021 Harappa 5 46 3 1 9 45 21 1 1 5 n/a
H1022 Harappa 16 17 16 1 9 1 17 1 31 1 39d
H1024 Harappa 14 n/a 15 5 25b 10 n/a 4 23 13 1
H1025 Harappa 14 26 15 5 25 10 1 9 23 11 73
H1029 Harappa n/a n/a n/a n/a n/a 10 4 4 24 13 55
H1030 Harappa n/a 21 3 1 29 1 14 2 12 13 48
H1032 Harappa 15 26 15 1 25e 10 2 4 23 13 30
H1033 Harappa 14 26 15 1 25e 10 2 n/a 23 13 n/a
H1035 Harappa 21 8 13 1 15 10b n/a 2 24 1 44
H1037 Harappa 2 4 1 1 16 11 7 1 17 1 25
H1038 Harappa n/a 38 n/a n/a 14 7 14 1 12 1 n/a
H1039 Harappa 31 41 5 1 29 2 n/a 1 14 n/a 25
H1046 Harappa 10 51 3 1 46 46 n/a 16 36 n/a n/a
H1047 Harappa 15 26 15 1 25h 10 1 4 23 13 30
H1048 Harappa 15 26 n/a 1 25h 10 n/a 4 n/a 13 1
H1050 Harappa 9 27 14 1 9 1 n/a 1 n/a 11 61b
H1051 Harappa n/a 6 16 4 45 15 14 1 1 1 44
H11 Harappa 14 n/a 15 5 25g 30 n/a 4 22 13 56b
H12 Harappa 18 21 1 1 31 1 2 2 11 4 38
H13 Harappa 8 12 3 1 9 1 2 1 1 1 39
H14 Harappa 2 38 13 1 4 1 2 1 1 1 16
H15 Harappa 23 18 4 1 4 1 2 2 17 5 58
H16 Harappa n/a n/a n/a n/a 9 1 1 1 4 11 59
H1657 Harappa 1 26 16 5 32b 10 17 4 23 1 73
H1660 Harappa n/a n/a n/a n/a n/a n/a 8 4 23 n/a n/a
H1662 Harappa 10 22 4 1 9 1 n/a n/a n/a n/a n/a
H1663 Harappa n/a n/a n/a n/a n/a 7 n/a n/a n/a 13 n/a
H1664 Harappa 21 19 4 1 32e 47 n/a 8 24 5 67b
H1666 Harappa 38 21 38 1 15 34 13 8 21 20 67
H1667 Harappa n/a n/a n/a n/a 9 1 n/a 1 1 n/a 39d
H1669 Harappa 28 52 4 1 23 1 n/a n/a 6 10 72
H1670 Harappa 2 22 1 1 45 11 7 2 11 11 34
H1671 Harappa 21 43 4 1 16 11 2 1 24 18 96
H1672 Harappa 1 41b 36 1 29 2 2 1 1 13 34
H1673 Harappa 15 31 39 1 32a 48 17 8 27 1 44
H1677 Harappa 27 19 4 1 9 12 n/a n/a n/a n/a 66
H1678 Harappa 2 21 4 1 9 13 17 1 24 10 68
H1679 Harappa 28 12 16 1 33 12 n/a 1 18 1 68
H1680 Harappa 5 13 24 1 9 13 3 n/a n/a 1 68
H1682 Harappa 1 34 17 1 29 38 13 15 11 5 100
H1684 Harappa 37 13 15 1 16 11 2 n/a n/a n/a n/a
H1687 Harappa n/a n/a n/a n/a n/a 12 4 1 1 5 63b
H17 Harappa 5 27 9 1 n/a 1 n/a n/a n/a n/a 58
H18 Harappa 8 12 n/a 1 4 1 n/a n/a n/a n/a n/a
H19 Harappa 13 30 4 2 10 12 n/a 1 1 1 33
H2 Harappa 10 15 n/a 1 2 1 2 1 23 11 21
H20 Harappa 15 26 15 1 25c 10 1 4 23 13 30
H21 Harappa 15 17 15 5 25d 30 1 4 22 14 n/a
H22 Harappa 15 26 15 1 25d 10 2 4 23 13 30
H23 Harappa 15 26 15 1 25e 10 2 4 23 13 30
H24 Harappa 25 12 7 1 25e 1 6 1 19 5 66
H25 Harappa 15 26 15 1 25d 10 2 4 23 13 30
H2590 Harappa 14 26 15 5 25k 10 n/a 4 23 n/a 1
H26 Harappa 15 40 15 5 25h 29c n/a 8 22 12 60
H266 Harappa 1 46 4 1 9 1 n/a 9 24 n/a 38b
H267 Harappa 15 22 15 1 25h n/a n/a n/a n/a n/a 1
H268 Harappa n/a 26 4 1 25d 10 n/a 4 n/a 13 30
H27 Harappa 15 1 15 5 25d 1a 2 8 22 13 1
H270 Harappa 16 45 35 1 25c 10 n/a 13 31 5 44
H28 Harappa 15 26 15 1 25e 10 n/a 4 23 13 1
H29 Harappa n/a 1 n/a 5 n/a 29 n/a 4 n/a n/a n/a
H3 Harappa 7 12 3 1 41 1 6 1 30 1 55
H30 Harappa 10 n/a 4 n/a 4 1 n/a 1 5 1 61
H31 Harappa 4 22 1 1 4 1 3 1 22 5 53
H32 Harappa 16 18 1 1 31 1 1 2 11 9 16?
H33 Harappa 2 38 16 1 4 1 1 1 10 11 n/a
H34 Harappa 1 4 1 1 26 1 7 6 9 8 8
H35 Harappa 2 13 4 1 9 16 2 1 10 1 62
H36 Harappa 5 32 1 1 4 16 4 1 1 1 32
H37 Harappa 8 19 1 1 9 16 7 1 1 1 32
H38 Harappa 19 n/a 27 1 9 1 1 1 10 5 61b
H383 Harappa 20 19 5 1 11 39 n/a 8 4 1 44
H385 Harappa 20 21 15 1 25k 10 n/a 1 n/a 1 1
H386 Harappa 15 22 1 1 25i 1 n/a 4 23 13 89
H388 Harappa 7 41 5 1 32a 13 2 1 1 5 90
H389 Harappa 28 48 5 1 32b 1 n/a 9 1 10 54
H39 Harappa 16 18 3 1 9 1 3 2 23 5 63
H390 Harappa 15 42 4 5 25f 10 n/a n/a n/a n/a 56
H391 Harappa 2 19 13 1 25c 1 n/a n/a n/a n/a n/a
H394 Harappa n/a n/a n/a n/a n/a 40 n/a 1 24 1 91
H395 Harappa n/a n/a n/a n/a 10 n/a 4 23 13 1
H396 Harappa n/a n/a n/a n/a n/a 10 13 4 23 13 n/a
H4 Harappa 15 18 15 5 25b 1 2 4 17 10 3
H40 Harappa 19 27 28 1 9 1 n/a 4 23 10 47
H400 Harappa n/a n/a n/a n/a n/a 10 13 4 23 13 n/a
H405 Harappa 21 3 9 1 4 1 16 14 1 1 89
H407 Harappa 29 32 9 1 31 1 17 1 1 1 58b
H408 Harappa 27 38 4 1 9 1 2 1 1 1 16
H41 Harappa 1 28 3 1 27 11 1 n/a 5 5 n/a
H410 Harappa 21 34 4 1 2 10b 17 1 10 18 61
H411 Harappa 6 4 4 1 14 11 n/a 1 9 9 92
H412 Harappa 28 45 14 1 8c 11 n/a 1 12 1 88b
H417 Harappa n/a n/a n/a n/a n/a 41 2 1 33 3 n/a
H419 Harappa 15 19 17 1 25e 10 n/a 6 27 n/a 90
H42 Harappa 2 41 3 n/a 28 11 n/a 9 5 17 64
H420 Harappa 15 26 15 1 25e 10 n/a n/a n/a 13 n/a
H421 Harappa 15 11 17 1 25j 1 17 8 1 14 n/a
H43 Harappa 13 19 16 1 26 29d 13 1 17 5 32
H44 Harappa 15 42 9 1 25h 1 2 4 23 6 65
H440 Harappa 8 19 1 1 4 42 19 1 34 6 58c
H441 Harappa 2 19 4 1 18 1 2 8 18 1 32
H442 Harappa 8 49 16 1 9 1 n/a 1 13 1 32
H443 Harappa 9 8 36 1 31 1 n/a 1 1 16 31
H444 Harappa 28 34 31 1 19b 43 n/a 1 1 18 53
H446 Harappa 8 8 14 1 4 12 7 1 11 9 93
H447 Harappa n/a 8 21 1 4 1 n/a 1 17 1 n/a
H448 Harappa 1 8 27 1 9 1 2 2 1 5 82
H449 Harappa 16 12 1 1 26 1 n/a 1 12 4 32
H45 Harappa 10 41 n/a 4 25e 1 n/a n/a n/a n/a n/a
H450 Harappa 2 8 4 1 9 2 2 8 17 5 32
H451 Harappa 34 8 22 1 4 1 n/a n/a n/a n/a 61b
H452 Harappa 5 25 n/a 1 44 23 7 1 1 11 n/a
H454 Harappa 35 12 4 1 4 16 2 1 17 10 94
H455 Harappa n/a 4 n/a 1 22 7 n/a n/a n/a n/a 61b
H456 Harappa 16 41 4 1 16 7 n/a 1 17 9 32
H457 Harappa 6 6 8 1 28 7 4 1 1 1 63
H458 Harappa 28 49 14 1 22 7 n/a 1 35 9 61b
H459 Harappa 9 12 4 1 23 44 2 1 17 1 61b
H46 Harappa 15 26 15 1 25e 10 2 4 23 13 30
H461 Harappa 9 49 14 1 23 7 2 1 35 1 63b
H464 Harappa 9 49 14 1 22 7 2 1 35 9 63b
H466 Harappa 6 38 37 1 29 14 n/a 1 5 16 61b
H468 Harappa 1 8 3 1 23 2 2 9 17 13 34b
H469 Harappa 9 8 3 1 28 2 4 9 11 13 95
H47 Harappa 15 17 15 5 25b 29 2 4 23 13 56
H470 Harappa 29 34 n/a n/a 29 2 n/a 9 9 16 4
H471 Harappa n/a 5 n/a n/a 28 38 n/a 1 8 5 n/a
H473 Harappa 2 26 1 1 32e 10 2 4 23 13 30
H474 Harappa 5 29 14 4 32e 1 n/a 4 27 n/a 44
H475 Harappa 2a 41 4 1 8b 10b 13 8 13 4 13
H476 Harappa n/a n/a n/a n/a n/a 10 5 8 12 4 89b
H477 Harappa 15 48 15 1 25h 1 20 1 1 14 89
H478 Harappa 15 38 28 4 25e 10b 2 4 22 13 44
H479 Harappa 15 34 13 1 25h 1 2 4 24 13 44
H48 Harappa 16 12 1 1 26 1 1 1 12 4 31
H49 Harappa 2 8 16 1 4 12 4 1 17 5 31
H499 Harappa 3 34 14 1 4 12 3 1 12 9 32
H5 Harappa 14 26 15 5 25 10 8 4 23 13 1
H50 Harappa 6 13 4 1 9 1 n/a 1 17 n/a 66b
H501 Harappa 6 27 4 1 9 12 2 1 12 13 44
H502 Harappa 6 27 4 1 13 12 3 1 1 9 81
H503 Harappa 1 34 14 1 4 2 3 1 9 1 96
H504 Harappa 6 12 4 1 9 1 n/a 8 9 11 97
H505 Harappa 26 6 14 1 11 9 2 1 1 1 61b
H506 Harappa 2 38 28 1 43b 15 14 1 9 1 61b
H508 Harappa 2 n/a 4 n/a 14 2 7 1 10 11 61b
H51 Harappa 13 18 29 1 29 2 14 1 17 10 34
H510 Harappa 20 19 n/a 1 16 26 7 n/a n/a 11 n/a
H511 Harappa 21 34 4 1 29 2 3 1 4 18 98
H512 Harappa 12 13 4 1 28 12 17 1 10 3 44
H513 Harappa 13 8 3 1 14 2 14 5 5 10 71b
H514 Harappa 2 29 3 1 28a 4 2 9 11 11 99
H515 Harappa 28 13 3 1 45 7 2 5 12 5 64e
H516 Harappa 2 45 14 1 14 7 7 9 1 n/a 64
H517 Harappa 28 8 17 1 23 15 14 1 12 6 64
H518 Harappa 36 22 36 1 32e 34 n/a 15 n/a 13 1
H519 Harappa 32 13 4 1 5 14 14 9 10 5 n/a
H52 Harappa 19 38 1 n/a 8c 11 n/a 7 10 7 64b
H520 Harappa 12 38 14 1 14 2 2 1 1 9 81b
H53 Harappa 2 19 30 1 29 15 3 1 20 1 67
H54 Harappa 6 15 n/a 1 14 7 14 1 12 11 61b
H55 Harappa 7 32 n/a 1 14 33 14 1 31 14 n/a
H56 Harappa 7 6 n/a 1 14 2 14 1 14 2 n/a
H57 Harappa 15 26 15 1 25e 10 2 4 23 13 30
H58 Harappa 14 26 17 1 25i 10 2 4 11 13 1
H59 Harappa n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
H597 Harappa 10 41 4 1 4 2 14 2 17 10 32
H598 Harappa 16 24 1 1 9 1 2 1 1 18 32
H6 Harappa 14 26 15 5 25 10 8 4 23 13 1
H60 Harappa 6 47 23 5 28 8 6 9 29 19 n/a
H61 Harappa 9 13 4 1 19 31 14 1 1 1 25
H610 Harappa 37 50 4 1 14 2 4 9 12 18 27
H62 Harappa 2 13 32 1 2 1 7 8 24 12 68
H63 Harappa 21 8 31 1 2 1 5 1 24 1 69
H64 Harappa 9 43 14 1 42 32 2 1 4 1 70
H65 Harappa 28 19 22 1 14 11 7 1 28 5 47
H66 Harappa 1 6 3 1 14 12 14 1 26 13 71
H67 Harappa 27 45 1 1 14 7 n/a 1 9 1 12
H68 Harappa 3 n/a 13 1 29 38 14 1 3 5 4
H69 Harappa n/a 38 13 1 29 7 n/a 9 19 11 25
H7 Harappa 14 26 15 5 25b 10 8 4 23 13 1
H70 Harappa 26 38 1 1 43 15 15 1 27 8 26
H71 Harappa 25 8 1 1 5 11 11 1 14 5 44
H72 Harappa 21 31 17 1 32 30b 2 6 27 14 26b
H73 Harappa 25 n/a 25 1 42 15 2 10 29 17 n/a
H74 Harappa 11 21 16 1 6 7 2 1 1 11 64c
H75 Harappa 5 6 9 1 16 2 14 1 10 16 25
H8 Harappa 24 14 15 5 25b 29 n/a 1 23 13 56
H9 Harappa 14 17 15 5 25d 29 2 4 23 13 56
JK2 Jhukar 7 19 1 1 4 12 4 1 9 14 32
KD5 Kot Diji n/a n/a n/a n/a n/a n/a 2 n/a 5 1 n/a
KLB1 Kalibangan n/a 19 1 1 15 1 2 2 2 4 14
KLB10 Kalibangan 8 6 16 1 8c 7 3 1 20 5 9
KLB11 Kalibangan 21 10 21 1 23 2 2 7 10 10 10
KLB12 Kalibangan 5 22 9 1 30 7 n/a 2 28 5a 47
KLB13 Kalibangan 16 8 14 1 14 7 2 1 26 9 48
KLB14 Kalibangan 1 29 3 1 20 7 2 2 6 13 15
KLB15 Kalibangan 1 9 22 5 7 8 1 4 11 10 11
KLB16 Kalibangan 5 36 23 5 36 25 2 1 6 10 49
KLB17 Kalibangan 1a 14 23 1 37 14 3 1 6 6 12
KLB18 Kalibangan 1 29 23 5 38 14 n/a 1 6 10 50
KLB19 Kalibangan 2a 16 4 1 8 1 11 8 13 4 13
KLB2 Kalibangan 1 18 3 5 23b 1 1 2 5 14 35b
KLB20 Kalibangan n/a 29 n/a 1 28 7 7 n/a 11 4 n/a
KLB21 Kalibangan n/a n/a n/a n/a n/a n/a 7 1 17 16 n/a
KLB22 Kalibangan 16 8 4 1 14 7 2 1 26 n/a 48
KLB23 Kalibangan 20 19 24 4 16 26 3 1 28 11 47
KLB24 Kalibangan n/a 21 n/a n/a 29 2 n/a n/a n/a n/a n/a
KLB26 Kalibangan 22 37 25 1 20 n/a 4 8 29 n/a 51
KLB3 Kalibangan n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
KLB4 Kalibangan 6 5 14 1 4 1 2 1 1 1 8
KLB5 Kalibangan 13 21 4 1 9 1 2 1 1 1 16
KLB6 Kalibangan 10 29 20 1 35 24 n/a 1 9 6 45
KLB7 Kalibangan n/a n/a n/a n/a n/a 1 4 1 1 10 46
KLB8 Kalibangan 6 5 14 1 4 1 2 1 1 10 8b
KLB9 Kalibangan 6 12 14 1 4 1 2 1 1 5 2
L1 Lothal 1 1 1 1 1 1 1 2 1 1 1
L10 Lothal n/a 12 n/a n/a 6 5 2 1 9 11 n/a
L11 Lothal 5 12 4 1 6 5 n/a 1 9 11 n/a
L12 Lothal n/a n/a n/a n/a 6 5 n/a 1 9 11 n/a
L13 Lothal n/a n/a n/a n/a n/a 1 3 11 24 12 23
L14 Lothal n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
L15 Lothal n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
L16 Lothal 2 21 1 1 n/a 1 n/a 8 n/a 4 n/a
L17 Lothal 1 21 n/a 1 9 1 n/a 1 1 1 16?
L18 Lothal 2 2 2 1 4 3 4 8 2 5 3
L19 Lothal 2 22 1 n/a 15 10 5 1 1 n/a 24
L2 Lothal 2 17 2 1 2 1 n/a n/a 2 2 n/a
L20 Lothal n/a n/a 1 1 n/a n/a 1 1 20 1 n/a
L21 Lothal 3 n/a 13 2 9 2 4 1 5 6 4
L22 Lothal n/a 4 3 1 13 18 n/a 13 10 2 n/a
L23 Lothal n/a 23 5 1 18 4 n/a 1 19 n/a 3
L24 Lothal 2 n/a 6 n/a 18 n/a n/a n/a n/a n/a n/a
L25 Lothal n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
L26 Lothal 13 3 7 1 19 4 2 1 21 11 5
L27 Lothal n/a n/a n/a n/a n/a 15 n/a 1 n/a 11 n/a
L28 Lothal 5 12 4 1 6 5 1 1 9 11 blank
L29 Lothal n/a 4 8 1 20 5 8 8 7 6
L3 Lothal n/a n/a n/a n/a n/a 1 n/a 13 24 n/a n/a
L30 Lothal n/a n/a n/a n/a n/a n/a n/a 1 9 11 blank
L35 Lothal 7 7 9 1 4 2 n/a 1 24 1 7
L36 Lothal n/a 24 10 1 13 15 1 1 7 2 blank
L37 Lothal n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
L38 Lothal n/a n/a n/a 2 16 19 6 1 24 n/a blank
L39 Lothal n/a 25 11 2 21 n/a n/a 3 25 5 25
L4 Lothal n/a 19 2 1 n/a 5 3 1 9 12 n/a
L40 Lothal n/a n/a n/a n/a n/a n/a n/a n/a 19 n/a n/a
L41 Lothal n/a n/a 12 3 13 n/a n/a 1 n/a n/a n/a
L42 Lothal n/a 25 13 1 n/a 12 1 1 5 5 26
L43 Lothal n/a n/a n/a n/a 13 n/a 2 n/a n/a 5 n/a
L5 Lothal 6 18 3 1 3 2 n/a 2 3 3 2
L6 Lothal n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a n/a
L65 Lothal 2 7 14 4 2b 1 n/a 11 10 n/a 23
L66 Lothal n/a 7 1 1 18 20 7 n/a 24 2 blank
L7 Lothal 12 n/a n/a n/a 3 n/a n/a 6 23 n/a n/a
L9 Lothal n/a n/a n/a 1 n/a 1 1 8 9 4 n/a
LH1 Lohumjodaro 6 12 10 4 4 12 n/a 1 17 1 32
M1 Mohenjo-daro 16 1 3 1 9 1 16 2 32 10 72
M10 Mohenjo-daro 21 26 15 5 25h 34 13 n/a n/a 1 n/a
M100 Mohenjo-daro 30 46 27 1 9 12 4 8 32 10 16
M104 Mohenjo-daro 16 7 1 1 42 12 13 1 24 1 40
M11 Mohenjo-daro n/a n/a n/a n/a n/a 10 8 8 23 1 73
M12 Mohenjo-daro 16 15 19 1 9 1 2 4 17 1 76
M13 Mohenjo-daro 1 21 17 1 9 1 8 2 26 1 54
M14 Mohenjo-daro 10 1 28 1 9 1 2 8 26 10 40b
M142 Mohenjo-daro 1 15 3 1 28 2 1 2 5 5 34
M144 Mohenjo-daro 10 41b 3 2 43 2 2 17 26 18 48
M145 Mohenjo-daro 1 15 3 1 23 11 1 2 5 1 34
M146 Mohenjo-daro 1 15 3 1 23 2 n/a 2 5 5 n/a
M15 Mohenjo-daro 20 43 33 1 19 35 2 8 10 8 54
M16 Mohenjo-daro 1 21 16 1 9 1 17 8 32 1 38
M1660 Mohenjo-daro 2 21 1 1 31 1 21 2 27 13 106
M1662 Mohenjo-daro 32 1 4 5 32f 49 21 8 37 1 78
M1673 Mohenjo-daro 16 29 3 1 14 1 n/a 1 11 14 34
M1683 Mohenjo-daro 15 26 17 1 25k 1 17 1 17 14 16
M1698 Mohenjo-daro 6 n/a 38 4 9 1 17 1 n/a 14 46
M17 Mohenjo-daro 26 38 1 1 9 1 4 1 1 14 39
M170 Mohenjo-daro 15 26 15 4 25e 10 2 4 23 13 30
M1711 Mohenjo-daro 40 21 3 1 23 1 7 2 32 14 28
M1718 Mohenjo-daro 27 26 22 5 28 12 2 8 11 14 107
M1720 Mohenjo-daro 15 26 15 4 25e 10 2 4 23 13 30
M173 Mohenjo-daro 2 1 36 1 32b 48 2 8 1 1 42b
M1743 Mohenjo-daro 1 38 1 1 9 12 19 1 1 1 84
M1746 Mohenjo-daro 30 38 1 1 9 12 14 1 1 10 84
M1765 Mohenjo-daro 41 38 14 4 9 49 17 1 1 5 62
M1767 Mohenjo-daro 2 32 30 1 2b 49 4 1 1 16 39
M1778 Mohenjo-daro 29 32 1 1 29 2 17 8 24 1 16
M1794 Mohenjo-daro 33 19 16 1 9 1 14 2 1 9 16
M18 Mohenjo-daro 16 21 21 1 19 1 17 1 1 1 77
M1827 Mohenjo-daro 30 7 1 1 9 12 4 8 11 1 94
M1833 Mohenjo-daro 8 21 3 1 14 2 14 9 n 18 9
M19 Mohenjo-daro 27 38 5 1 9 1 n/a 1 1 1 40
M2 Mohenjo-daro 28 n/a 4 n/a 31 n/a n/a 2 27 n/a 36
M20 Mohenjo-daro 1 8 28 1 9 1 n/a 8 32 14 38
M201 Mohenjo-daro 16 13 4 1 9 1 22 1 1 5 108
M21 Mohenjo-daro 27 21 17 1 9 1 17 1 21 10 78
M214 Mohenjo-daro 39 24 17 1 20 22 14 1 1 11 44
M22 Mohenjo-daro 12 42 16 1 9 1 n/a 8 32 10 72
M223 Mohenjo-daro 21 14 10 1 11 27 23 16 29 17 109
M227 Mohenjo-daro n/a 19 1 1 9 12 17 1 1 11 32
M23 Mohenjo-daro 27 29 3 1 22 1 17 2 11 10 28
M230 Mohenjo-daro 28 10 3 1 8c 21 n/a 9 35 11 27
M24 Mohenjo-daro 1 21 3 1 14 36 17 1 31 1 34
M25 Mohenjo-daro 1 29 3 1 10 2 n/a n/a n/a n/a n/a
M26 Mohenjo-daro 26 39 3 1 14 2 2 1 17 10 79
M27 Mohenjo-daro 29 8 24 1 3 2 n/a 8 1 11 46
M28 Mohenjo-daro 1 1 1 1 1 1 1 1 1 1 27
M29 Mohenjo-daro 14 17 15 5 32b 29 2 4 23 13 56
M3 Mohenjo-daro 16 15 1 1 9 1 n/a 1 26 1 39
M30 Mohenjo-daro 2 26 4 5 32e 34 8 9 32 13 73
M31 Mohenjo-daro 1 29 24 1 9 1 N/a 1 N/a 10 40
M32 Mohenjo-daro 6 21 3 1 9 12 4 1 31 1 25
M33 Mohenjo-daro 27 21 17 1 9 1 17 1 21 10 40
M34 Mohenjo-daro 27 21 17 1 9 1 17 1 21 10 40
M35 Mohenjo-daro 2 13 2 1 9 1 n/a 8 17 1 80
M36 Mohenjo-daro 8 29 21 1 9 12 17 1 31 1 40
M37 Mohenjo-daro 37 21 1 1 9 12 4 1 21 1 40
M38 Mohenjo-daro 8 29 1 1 9 12 4 1 1 1 40
M39 Mohenjo-daro 10 38 28 1 19 12 4 8 21 1 4
M4 Mohenjo-daro 10 28 4 1 9 1 8 1 21 1 36
M40 Mohenjo-daro 5 38 13 1 9 12 17 1 22 11 76
M41 Mohenjo-daro 21 12 1 1 9 1 2 1 1 1 56
M42 Mohenjo-daro 29 10 25 1 9 12 2 1 5 1 58
M43 Mohenjo-daro 31 21 13 4 9 1 n/a 8 10 5 81
M44 Mohenjo-daro 27 13 4 1 9 1 2 1 31 1 62
M45 Mohenjo-daro 31 41 1 4 9 1 17 1 9 1 82
M46 Mohenjo-daro 30 12 1 1 9 1 4 1 31 1 83
M47 Mohenjo-daro 8 4 28 1 9 12 2 1 1 1 84
M48 Mohenjo-daro 3 13 28 1 9 12 2 1 1 9 85
M49 Mohenjo-daro 2 7 4 1 15 1 17 1 32 10 84
M5 Mohenjo-daro n/a 41 13 1 9 1 3 1 1 5 36
M50 Mohenjo-daro 1 1 4 1 15 1 13 9 28 1 53
M51 Mohenjo-daro 20 44 15 1 13 12 17 1 9 1 81
M52 Mohenjo-daro 27 21 1 1 9 1 2 1 31 1 62
M53 Mohenjo-daro 2 21 4 1 9 1 2 4 31 10 20
M54 Mohenjo-daro 16 21 21 1 9 1 17 8 32 1 38
M55 Mohenjo-daro 19 8 9 1 31 1 1 1 6 8 39
M56 Mohenjo-daro 16 29 n/a 1 31 1 n/a 5 26 4 36
M57 Mohenjo-daro 16 30 1 1 31 1 2 2 26 4 37
M58 Mohenjo-daro 27 21 1 1 9 1 3 1 31 1 86
M59 Mohenjo-daro 2 21 1 1 9 1 8 8 31 1 42
M595 Mohenjo-daro 2 16 4 1 15 1 24 1 17 1 39
M6 Mohenjo-daro 6 31 17 1 32 10 10 6 27 10 42
M60 Mohenjo-daro n/a 10 n/a 1 9 12 n/a n/a n/a n/a 66
M61 Mohenjo-daro 16 29 3 1 9 1 2 2 11 3 29
M62 Mohenjo-daro 29 10 3 1 14 33 4 1 5 3 5
M624 Mohenjo-daro 2 21 4 1 31 52 n/a 8 35 14 78
M629 Mohenjo-daro 14 26 15 1 25f 10 8 4 23 13 30
M63 Mohenjo-daro 28 13 3 1 23 11 n/a 1 n/a 3 33
M631 Mohenjo-daro 15 48 11 5 25c 51 17 2 24 1 110
M633 Mohenjo-daro 14 31 15 5 32d 43 17 2 27 14 42
M64 Mohenjo-daro 27 22 3 1 23 1 2 2 11 14 34
M644 Mohenjo-daro 16 15 3 1 9 1 n/a 11 24 20 27b
M649 Mohenjo-daro 28 45 9 1 42 10b 7 1 26 1 81
M65 Mohenjo-daro 16 22 3 1 14 1 8 9 31 3 35
M653 Mohenjo-daro 16 21 1 1 31 1 n/a 2 11 14 n/a
M66 Mohenjo-daro 2 43 10 1 28 14 4 8 32 18 64
M662 Mohenjo-daro 1 21 22 1 8c 1 n/a 2 27 n/a 28
M67 Mohenjo-daro 16 22 3 1 3 1 2 8 3 3 34
M670 Mohenjo-daro 15 26 15 1 25d 10 1 4 23 13 30
M672 Mohenjo-daro 1 31 17 1 32a 1 10 6 27 14 41
M673 Mohenjo-daro 16 1 36 1 32b 29 n/a 11 1 18 65
M675 Mohenjo-daro 1 32 17 1 32b 1 n/a 6 27 14 42
M676 Mohenjo-daro n/a n/a 4 n/a 32b 34 1 4 23 14 73
M677 Mohenjo-daro 1 31 17 1 32b 23 10 6 27 14 42
M678 Mohenjo-daro 15 22 15 5 32b 29 n/a 6 31 11 111
M68 Mohenjo-daro 1 16 3 5 27 11 1 2 5 5 33
M69 Mohenjo-daro 2 38 17 1 29 21 2 1 10 1 81
M699 Mohenjo-daro 25 8 16 1 15 1 24 1 1 5 59
M7 Mohenjo-daro 10 42 1 5 32a 10 8 1 21 11 73
M70 Mohenjo-daro 29 3 27 1 29 2 2 1 1 1 62
M700 Mohenjo-daro 1 45 4 1 9 12 15 9 1 8 32
M705 Mohenjo-daro n/a 41b n/a 1 9 1 n/a 1 1 18 53
M709 Mohenjo-daro 33 39 4 1 9 1 14 17 31 14 39
M71 Mohenjo-daro 16 22 27 1 29 2 2 1 17 12 39
M72 Mohenjo-daro 32 3 34 1 40 27 18 1 1 10 n/a
M723 Mohenjo-daro 16 18 1 1 31 1 n/a n/a n/a n/a n/a
M729 Mohenjo-daro 7 n/a 3 1 14 11 n/a 2 26 10 34
M73 Mohenjo-daro 15 26 16 1 25j 10 8 4 23 13 1
M732 Mohenjo-daro 1 26 22 5 48 8 2 8 11 10 48
M734 Mohenjo-daro 1 15 3 5 23 11 1 2 5 5 35
M74 Mohenjo-daro 20 14 9 1 20 18 2 9 19 1 44
M740 Mohenjo-daro 1 28 3 1 29 2 n/a 2 5 n/a 33
M75 Mohenjo-daro 4 7 2 1 6 1 6 12 1 1 87
M751 Mohenjo-daro 42 29 4 5 25f 1 n/a 4 n/a n/a 73
M752 Mohenjo-daro 15 22 4 5 25d 41 17 4 11 13 73
M76 Mohenjo-daro n/a n/a n/a n/a n/a 1 2 8 1 13 n/a
M77 Mohenjo-daro 16 12 1 1 9 1 2 1 31 1 16
M78 Mohenjo-daro 3 18 4 4 9 12 4 1 26 8 16
M786 Mohenjo-daro 28 32 17 1 42 12 18 5 17 1 31
M788 Mohenjo-daro 6 32 16 1 9 12 13 1 1 10 40
M79 Mohenjo-daro 8 13 1 1 9 12 9 1 17 1 16
M793 Mohenjo-daro 5 34 18 4 42 4 22 1 1 16 112
M8 Mohenjo-daro 1 29 32 5 32d 10 1 11 26 1 74
M80 Mohenjo-daro 29 12 17 1 9 11 2 1 26 1 16
M802 Mohenjo-daro 16 52 1 1 9 1 n/a 1 n/a n/a 108
M806 Mohenjo-daro 7 18 n/a 1 9 12 n/a 1 6 5 40b
M807 Mohenjo-daro n/a n/a n/a n/a 9 12 n/a 1 6 5 40b
M81 Mohenjo-daro 31 12 19 1 9 12 3 1 31 10 65
M810 Mohenjo-daro 7 15 16 9 12 9 1 6 5 40
M814 Mohenjo-daro 30 6 16 2 9 12 2 5 1 17 32
M815 Mohenjo-daro 25 44 4 1 9 48 7 1 27 5 68
M819 Mohenjo-daro 2 24 4 1 4 12 2 1 1 9 16
M82 Mohenjo-daro 16 8 1 1 9 11 2 8 27 1 16
M83 Mohenjo-daro 9 45 9 1 9 1 12 9 14 1 66
M830 Mohenjo-daro 10 19 17 1 9 2 n/a 1 1 17 53
M836 Mohenjo-daro 2 6 1 1 9 1 2 9 17 1 3
M84 Mohenjo-daro 26 8 1 1 9 1 3 1 1 1 16
M85 Mohenjo-daro 16 8 1 1 9 1 8 1 24 1 62
M86 Mohenjo-daro 10 12 21 4 9 12 4 1 17 10 16
M861 Mohenjo-daro 2 8 4 1 45 7 2 1 1 16 72
M87 Mohenjo-daro 8 19 1 1 9 2 12 1 21 1 88
M872 Mohenjo-daro 13 19 10 1 20 7 n/a 1 17 1 113
M875 Mohenjo-daro 13 34 4 1 14 7 2 9 26 18 94
M878 Mohenjo-daro 6 18 3 1 24 2 n/a 3 3 29
M88 Mohenjo-daro 16 6 3 1 9 12 4 1 32 1 53
M880 Mohenjo-daro 27 34 3 1 29 2 16 1 17 10 34
M89 Mohenjo-daro 4 43 1 1 9 12 2 1 17 1 84
M9 Mohenjo-daro 1 31 17 1 32d 10 n/a 8 21 1 75
M90 Mohenjo-daro 10 15 1 1 9 12 2 1 5 1 16
M91 Mohenjo-daro 30 13 16 1 13 12 3 1 17 14 53
M916 Mohenjo-daro 28 49 9 1 9 12 2 1 21 5 66
M92 Mohenjo-daro 31 7 24 1 9 12 4 1 1 1 16
M921 Mohenjo-daro 30 21 15 1 9 12 n/a 1 1 1 32
M926 Mohenjo-daro 30 38 39 1 9 12 14 9 1 13 32
M93 Mohenjo-daro 31 45 9 1 9 12 4 1 17 1 16
M931 Mohenjo-daro 16 13 4 1 9 1 2 1 1 5 39
M94 Mohenjo-daro 16 38 27 1 9 12 2 1 1 1 84
M95 Mohenjo-daro 3 7 28 1 9 12 4 1 28 10 16
M953 Mohenjo-daro 16 21 5 1 9 12 4 1 17 14 71
M96 Mohenjo-daro 21 22 1 1 9 12 4 1 17 10 16
M967 Mohenjo-daro 1 13 4 1 28b 1 17 1 1 9 114
M97 Mohenjo-daro 27 22 1 1 9 12 17 8 32 10 16
M973 Mohenjo-daro 1 n/a 3 1 28 2 1 2 5 5 34
M98 Mohenjo-daro 6 8 3 1 9 12 n/a 1 21 1 16
M99 Mohenjo-daro 33 12 16 1 9 12 4 1 32 14 16
ND1 Nindowari 1 16 3 5 27b 11 1 2 5 5 35b
ND2 Nindowari 6 25 14 1 20 12 n/a 1 5 11 2
NS5 Nausharo 3 28 3 1 10 2 2 2 5 2 15
NS6 Nausharo 11 38 14 1 28b 28 2 2 5 13 48
NS7 Nausharo 11 25 3 1 41 12 1 1 1 1 39
NS8 Nausharo n/a 25 4 1 4 n/a 2 n/a n/a n/a n/a
PBM1 Pabumath n/a 38 n/a n/a 4 12 n/a n/a n/a n/a n/a
RGR1 Rakigarhi 5 38 4 1 18 12 12 1 24 11 n/a
RGR2 Rakigarhi 2 38 3 1 14 2 4 1 n/a n/a 71
RGR3 Rakigarhi 6 n/a 28 1 11 4 n/a 4 23 n/a 9
SKTD1 Surkotada n/a 5 3 1 16 19 2 1 10 11 22"""

def extract_stand_column(table_text):
    """Extract STAND column (offering stand types) from table - keeps all values"""
    stand_values = []
    for line in table_text.split('\n'):
        parts = line.split()
        if len(parts) >= 13:  # Column 12 is STAND
            stand = parts[12]
            # Keep the raw value exactly as-is (including n/a, blank, letter suffixes, ?)
            stand_values.append(stand)
    return stand_values

def extract_stand_column_normalized(table_text):
    """Extract STAND column and normalize (e.g., 40b->40, remove n/a/blank)"""
    stand_values = []
    for line in table_text.split('\n'):
        parts = line.split()
        if len(parts) >= 13:  # Column 12 is STAND
            stand = parts[12]
            if stand != 'n/a' and stand != 'blank' and stand != 'N/a':
                # Normalize variants (e.g., "16?" -> "16")
                stand_clean = stand.rstrip('?').rstrip('a').rstrip('b').rstrip('c').rstrip('d').rstrip('e').rstrip('f').rstrip('h').rstrip('i').rstrip('j').rstrip('k')
                try:
                    stand_clean = int(stand_clean)
                    stand_values.append(stand_clean)
                except ValueError:
                    continue
    return stand_values

def extract_simplified_table(table_text):
    """Extract site code, site name, and STAND value for manual verification"""
    # List of known site names to correctly identify site code boundaries
    SITE_NAMES = {'Allahdino', 'Bagasra', 'Balakot', 'Banawali', 'Chanhu-daro', 
                   'Dholavira', 'Farmana', 'Harappa', 'Jhukar', 'Kalibangan', 
                   'Lothal', 'Lohumjodaro', 'Mohenjo-daro', 'Nindowari', 'Nausharo', 
                   'Pabumath', 'Rakigarhi', 'Surkotada'}
    
    simplified = []
    for line in table_text.split('\n'):
        parts = line.split()
        if len(parts) < 13:
            continue
        
        # Find the site name in the parts
        site_name_idx = None
        for i, part in enumerate(parts):
            if part in SITE_NAMES:
                site_name_idx = i
                break
        
        if site_name_idx is not None:
            site_code = ' '.join(parts[:site_name_idx])
            site_name = parts[site_name_idx]
            stand = parts[-1]
            simplified.append((site_code, site_name, stand))
    
    return simplified

# Extract and analyze
stands = extract_stand_column(full_table)
stands_normalized = extract_stand_column_normalized(full_table)
simplified_table = extract_simplified_table(full_table)
stand_freq = Counter(stands)

print("=" * 70)
print("SIMPLIFIED TABLE: SITE CODE | SITE NAME | OFFERING STAND")
print("=" * 70)
print(f"{'Site Code':<12} {'Site Name':<18} {'Stand':<8}")
print("-" * 70)
for site_code, site_name, stand in simplified_table:
    print(f"{site_code:<12} {site_name:<18} {stand:<8}")

# Save to sites_table.txt with headers and formatted columns
with open('sites_table.txt', 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("SIMPLIFIED TABLE: SITE CODE | SITE NAME | OFFERING STAND\n")
    f.write("=" * 70 + "\n")
    f.write(f"{'Site Code':<12} {'Site Name':<18} {'Stand':<8}\n")
    f.write("-" * 70 + "\n")
    for site_code, site_name, stand in simplified_table:
        f.write(f"{site_code:<12} {site_name:<18} {stand:<8}\n")
print("\nSaved to sites_table.txt")

# Save to guilds.txt with all stand type frequencies (including n/a and blank)
with open('guilds.txt', 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("OFFERING STAND TYPE FREQUENCY DISTRIBUTION (ALL VALUES)\n")
    f.write("=" * 70 + "\n")
    f.write(f"{'Stand Type':<12} {'Total Count':<15} {'% of Total Seals':<20}\n")
    f.write("-" * 70 + "\n")
    
    total_seals = len(stands)
    for stand_type, count in stand_freq.most_common():
        percentage = 100.0 * count / total_seals
        f.write(f"{stand_type:<12} {count:<15} {percentage:>6.2f}%\n")
    
    f.write("-" * 70 + "\n")
    f.write(f"{'TOTAL TYPES':<12} {len(stand_freq):<15} {'100.00%':>18}\n")

print("Saved to guilds.txt")

# Save to guilds_valid.txt excluding n/a and blank
stand_freq_valid = {k: v for k, v in stand_freq.items() if k != 'n/a' and k != 'blank'}
with open('guilds_valid.txt', 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("OFFERING STAND TYPE FREQUENCY DISTRIBUTION (VALID ONLY)\n")
    f.write("=" * 70 + "\n")
    f.write(f"{'Stand Type':<12} {'Total Count':<15} {'% of Total Seals':<20}\n")
    f.write("-" * 70 + "\n")
    
    total_valid_seals = sum(stand_freq_valid.values())
    for stand_type in sorted(stand_freq_valid.keys(), key=lambda x: stand_freq_valid[x], reverse=True):
        count = stand_freq_valid[stand_type]
        percentage = 100.0 * count / total_seals  # Still % of total 500 seals
        f.write(f"{stand_type:<12} {count:<15} {percentage:>6.2f}%\n")
    
    f.write("-" * 70 + "\n")
    f.write(f"{'TOTAL TYPES':<12} {len(stand_freq_valid):<15} {'':<20}\n")
    f.write(f"{'Valid Seals':<12} {total_valid_seals:<15} {100.0*total_valid_seals/total_seals:>6.2f}%\n")

print("Saved to guilds_valid.txt")

print("\n" + "=" * 70)
print("ANALYSIS OF ALL 500 UNICORN SEALS - APPENDIX 7.1")
print("=" * 70)
print(f"\nTotal seals in Appendix 7.1: 500")
print(f"Seals with valid STAND values (raw): {len(stands)}")
print(f"Seals with normalized numeric STAND values: {len(stands_normalized)}")
print(f"Unique STAND types represented (raw, including variants): {len(stand_freq)}")
print(f"\nTop 20 most common offering stand types (raw values):")
for stand_type, count in stand_freq.most_common(20):
    print(f"  Type {str(stand_type):<6s}: {count:3d} seals ({100*count/len(stands):.1f}%)")

# Power law analysis on normalized numeric frequencies
print("\n" + "=" * 70)
print("POWER LAW ANALYSIS ON NORMALIZED NUMERIC FREQUENCIES")
print("=" * 70)

# Fit power law using only normalized numeric values
stand_freq_normalized = Counter(stands_normalized)
xmin = 1
data = np.array(sorted(list(stand_freq_normalized.values()), reverse=True))

# Clauset et al. method: find optimal xmin
alpha_estimates = []
xmin_candidates = sorted(set(data))[:20]  # Check first 20 unique values

for xmin_test in xmin_candidates:
    data_above = data[data >= xmin_test]
    if len(data_above) > 1:
        alpha = 1 + len(data_above) / np.sum(np.log(data_above / (xmin_test - 0.5)))
        alpha_estimates.append((xmin_test, alpha, len(data_above)))

print(f"\nClauset criterion candidates:")
for xmin_test, alpha, n in alpha_estimates[:10]:
    print(f"  xmin={xmin_test}, alpha={alpha:.3f}, n={n}")

# Use xmin=1 for full analysis
xmin = 1
data_above = data[data >= xmin]
alpha_mle = 1 + len(data_above) / np.sum(np.log(data_above / (xmin - 0.5)))

print(f"\nUsing xmin={xmin}:")
print(f"  MLE alpha (power law exponent): {alpha_mle:.3f}")
print(f"  Number of types at/above xmin: {len(data_above)}")

# Goodness-of-fit test: KS test
# Fit both power law and exponential
pk = np.arange(1, len(data) + 1) / len(data)

# Power law CDF
pl_cdf = 1 - (xmin / data) ** (alpha_mle - 1)

# KS statistic
ks_stat = np.max(np.abs(pl_cdf - pk[:len(data_above)]))

print(f"\nGoodness-of-fit:")
print(f"  KS statistic: {ks_stat:.4f}")
print(f"  (Lower is better; p>0.1 typically indicates good fit)")

# Bootstrap p-value (2500 iterations)
print(f"\nRunning 2500 bootstrap iterations for power law p-value...")
n_bootstrap = 2500
ks_bootstrap = []
np.random.seed(42)

for _ in range(n_bootstrap):
    # Sample with replacement
    sample = np.random.choice(data_above, size=len(data_above), replace=True)
    sample_alpha = 1 + len(sample) / np.sum(np.log(sample / (xmin - 0.5)))
    
    # Generate synthetic data from fitted distribution
    synthetic = xmin * (1 - np.random.uniform(0, 1, len(sample))) ** (-1 / (sample_alpha - 1))
    synthetic = synthetic[synthetic >= xmin]
    
    # KS test on synthetic
    if len(synthetic) > 1:
        synthetic_sorted = np.sort(synthetic)
        pk_syn = np.arange(1, len(synthetic_sorted) + 1) / len(synthetic_sorted)
        pl_cdf_syn = 1 - (xmin / synthetic_sorted) ** (sample_alpha - 1)
        ks_bootstrap.append(np.max(np.abs(pl_cdf_syn - pk_syn)))

p_value_pl = np.mean(np.array(ks_bootstrap) >= ks_stat)
print(f"  Power law p-value: {p_value_pl:.4f}")
print(f"  Interpretation: Power law {'PASSES' if p_value_pl > 0.1 else 'FAILS'} GoF test (p>0.1)")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Distribution shape: alpha ~= {alpha_mle:.2f}")
print(f"Goodness-of-fit (p-value): {p_value_pl:.4f}")
print(f"Conclusion: Power law conformance is {'STRONG' if p_value_pl > 0.1 else 'WEAK'}")
print(f"\nComparison to paper's constraints-based result:")
print(f"  Original paper: alpha ~= 2.3-2.6 (constrained reconstruction)")
print(f"  This analysis: alpha ~= {alpha_mle:.2f} (direct from actual data)")
print(f"  Match: {'GOOD' if 2.1 < alpha_mle < 2.8 else 'DIFFERENT'}")

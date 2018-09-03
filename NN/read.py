with open('norX', 'r') as input:
    data = input.readlines()
 
    for line in data:
        odom = line.split()
        numbers_float = map(float, odom)
        print numbers_float
def Fun1(i, n):
    print(i)
    if i == n:
        return
    else:
        Fun1(i+1, n)

Fun1(1, 5)
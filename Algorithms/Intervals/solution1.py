#!/Users/stanley/opt/anaconda3/bin/python3

TEST_CASE_1 = [
    (6,10),(15,25),(12,13),(-3,0),(0,5)
]

TEST_CASE_2 = [
    (18,42),(10,12),(5,11),(-10,4),(0,6)
]

TEST_CASE_3 = [
    (0,5),(1,5),(2,5),(3,5),(4,5)
]

intervals = TEST_CASE_2

# Runtime is O(nlog(n)) from the sorting step. Is it possible to get
# O(n)? I don't know the answer to this.
def check_intersections(intervals: list[tuple[int,int]]) -> bool:

    sorted_intervals = sorted(intervals)

    for i in range(1, len(sorted_intervals)):

        cur_interval = sorted_intervals[i]
        prev_interval = sorted_intervals[i-1]

        if prev_interval[1] > cur_interval[0]:

            return True
        
    return False


if __name__ == "__main__":
    print(f"Input intervals = {intervals}")
    print(f"Any intersections: {check_intersections(intervals)}")
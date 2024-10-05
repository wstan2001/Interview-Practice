#!/Users/stanley/opt/anaconda3/bin/python3

# For priority queue
import heapq
from attrs import define

TEST_CASE_1 = [
    (6,10),(15,25),(12,13),(-3,0),(0,5)
]

TEST_CASE_2 = [
    (18,42),(10,12),(5,11),(-10,4),(0,6)
]

TEST_CASE_3 = [
    (0,5),(1,5),(2,5),(3,5),(4,5)
]

intervals = TEST_CASE_3

@define
class HeapItem:
    a: int
    b: int

    def __lt__(self, other) -> bool:

        return (self.b < other.b)


# Runtime is O(nlog(n))
def num_intersections(intervals: list[tuple[int,int]]) -> int:

    # O(nlog(n)) upfront cost
    sorted_intervals = sorted(intervals)
    ret = 0

    # we maintain a priority queue of intervals sorted by
    # right endpoint, with the smaller right endpoint intervals
    # coming first
    heap = []

    for interval in sorted_intervals:

        cur = HeapItem(interval[0], interval[1])

        # first delete any irrelevant intervals from the PQ.
        # These are intervals whose right endpoint is <= the
        # current PQ's left endpoint and will not give us any
        # more intersections.
        # Runtime: O(log(n)) per heappop
        while len(heap) > 0 and heap[0].b <= cur.a:
            heapq.heappop(heap)

        # at this point, all remaining intervals in the PQ satisfy
        # the property that their left endpoint is <= cur.a and their
        # right endpoint is > cur.a, so all remaining intervals will
        # intersect cur
        ret += len(heap)

        # now insert the cur interval into the PQ.
        # Runtime: O(log(n)) per heappush
        heapq.heappush(heap, cur)
        
    return ret


if __name__ == "__main__":
    print(f"Input intervals = {intervals}")
    print(f"Num intersections: {num_intersections(intervals)}")
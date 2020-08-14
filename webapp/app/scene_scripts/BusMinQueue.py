import heapq
from scene_scripts.Bus import Bus


class BusMinQueue:

    def __init__(self):
        self._data = []

    def extract_min(self):
        return heapq.heappop(self._data)

    def peek_min(self):
        return self._data[0]

    def push(self, entry) -> None:
        heapq.heappush(self._data, entry)

    def empty(self) -> bool:
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    # REQUIRES: the bus exists within the MinQueue
    # EFFECTS: updates the distance of a bus
    def update_dist(self, distance: float, tuple_entry: ()) -> None:
        for i, entry in enumerate(self._data):
            if tuple_entry == entry:
                self._data[i] = (distance, self._data[i][1])
                heapq.heapify(self._data)
                return

    # EFFECTS: Finds and returns an entry in a MinQueue based on custom criteria
    def find(self, bus: Bus) -> () or None:
        result = list(filter(lambda x: x[1] == bus, self._data))
        if len(result) != 0:
            return result[0]
        else:
            return None

    # EFFECTS: Find and remove
    def remove(self, bus: Bus) -> None:
        result = list(filter(lambda x: x[1] == bus, self._data)) # returns the tuple with the matching bus
        if len(result) > 0:
            self._data.remove(result[0])
            heapq.heapify(self._data)


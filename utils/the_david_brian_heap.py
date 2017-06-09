from random import randint

class DavidsAndBriansHeapForCellPriorityWithAReallyLongName(object):
    def __init__(self):
        self.array = [[None, float('-inf')]]  # 0th index is -infinity so that this will always stay the first element
        # tbh this value can be anything so no sweat.
        # other definitions ensure we'll never get this crazy element from pop()

    def print_heap_list(self):
        print(self.array)

    def insert(self, vertex, key):
        self.array.append([vertex, key])  # first append this new cell to the end of our current array
        index = len(self.array) - 1  # we start our index at the cell we just inserted

        while index > 0 and self.array[self._parent_index(index)][1] > key:  # while we are not at the 0th index and the parent's priority # > child priority #...
            self.array[index] = self.array[self._parent_index(index)]  # make that child node take on values of parent node
            self.array[self._parent_index(index)] = [vertex, key]  # make that parent node take on value of what we want inserted
            index = self._parent_index(index)  # set index to the parent node we just discarded and continue checking till done

        return

    def remove(self, vertex):
        if self.is_empty():
            return
        if self.array[-1][0] is vertex:  # if cell to remove is last one in array:
            del self.array[-1]
            return

        index = 0
        for element in self.array[1:]:
            index += 1
            if element[0] is vertex:  # cell found
                self.array[index] = self.array[-1]  # set the found element to be the last element
                del self.array[-1] # delete the last element

                while index > 0 and self.array[index][1] < self.array[self._parent_index(index)][1]: # if priority is less than new parent...
                    old_parent = self.array[self._parent_index(index)]  # set a tmp value for parent value
                    self.array[self._parent_index(index)] = self.array[index]
                    self.array[index] = old_parent
                    index = self._parent_index(index)


                self._heapify(index) # finally, heapify
                return


        return

    def pop(self):  # returns the root node: i.e, the cell with the highest priority (aka lowest number in min heap)
        if self.is_empty():
            return None
        cell_to_return = self.array[1]  # keep track of the root node so we can return it at end of function
        self.array[1] = self.array[len(self.array) - 1]  # make the root node the last element in the array
        del self.array[-1]  # remove the last element that we just set as the root
        self._heapify(1)  # give index of root element so that heapify can sift the root down if necessary
        return cell_to_return[0]

    def peek_min_priority(self):
        if self.is_empty():
            return None
        else:
            return self.array[1][1]

    def is_empty(self):
        if len(self.array) < 2:
            return True
        else:
            return False

    def _heapify(self, index):  # preserve heap order property (used after pop or remove)
        left_index = self._left_child_index(index)
        right_index = self._right_child_index(index)

        if left_index <= len(self.array) - 1 and self.array[left_index][1] < self.array[index][1]:  # if left is a valid index and priority # of left child is < # of parent...
            lowest_priority_num_index = left_index
        else:
            lowest_priority_num_index = index

        if right_index <= len(self.array) - 1 and self.array[right_index][1] < self.array[lowest_priority_num_index][1]:  # if right is a valid index and priority # of right child is < # of left child...
            lowest_priority_num_index = right_index

        if lowest_priority_num_index != index:  # if index was not already the index containing lowest priority num, swap them
            tmp_stuff = self.array[index]
            self.array[index] = self.array[lowest_priority_num_index]
            self.array[lowest_priority_num_index] = tmp_stuff
            self._heapify(lowest_priority_num_index)

        return

    def _parent_index(self, index):
        return index//2

    def _left_child_index(self, index):
        return 2*index

    def _right_child_index(self, index):
        return 2*index + 1

#
# q = DavidsAndBriansHeapForCellPriorityWithAReallyLongName()
#
# for x in range(100000, -1, -1):
#     i = randint(0, 1000000)
#     q.insert("data{}".format(i), i)
#
# q.insert("data{}".format(66666), 66666)
# q.insert("data{}".format(66667), 66667)
# q.insert("data{}".format(66668), 66668)
# q.insert("data{}".format(66669), 66669)
# q.remove("data66666")
# q.remove("data66667")
# q.remove("data66668")
# q.remove("data66669")
#
# while not q.is_empty():
#     print(q.pop())

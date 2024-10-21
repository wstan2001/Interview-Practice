#! /Users/stanley/opt/anaconda3/bin/python3
from enum import Enum
from attrs import define

import argparse

class Op(Enum):
    
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"

    
@define
class Node:
    
    @property
    def value(self) -> int:
        raise NotImplementedError
    
    def __str__(self) -> str:
        raise NotImplementedError
        
        
@define
class RootNode(Node):
    
    val: int
    
    @property
    def value(self) -> int:
        return self.val
    
    def __str__(self) -> str:
        return str(self.value)
    
    
@define
class CombinedNode(Node):
    
    left: Node
    right: Node
    op: Op
        
    @property
    def value(self) -> int:
        if self.op == Op.ADD:
            return self.left.value + self.right.value
        elif self.op == Op.SUB:
            return self.left.value - self.right.value
        elif self.op == Op.MUL:
            return self.left.value * self.right.value
        elif self.op == Op.DIV:
            return self.left.value / self.right.value
        else:
            raise ValueError(f"Unexpected {op=}")
                             
    def __str__(self) -> str:
        return "( " + str(self.left) + " " + self.op.value + " " + str(self.right) + " )"
    
@define
class TwentyFour:
    
    @classmethod
    def solve(cls, l: list[int], target: int=24) -> bool:
        
        node_list = [RootNode(val) for val in l]
        
        success, method = cls.solveImpl(node_list, target)
        
        if success:
            print(method)
            
        return success
        
    
    @classmethod
    def solveImpl(cls, l: list[Node], target: int=24) -> tuple[bool,str]:
        
        if len(l) == 1:
            
            node = l[0]
            
            if node.value == target:
                return True, str(node)
            else:
                return False, ""
            
        # try all ordered pairs of two nodes with all possible Ops
        for i in range(len(l)):
            for j in range(len(l)):
                
                # can't use the same number twice
                if i == j:
                    continue
                
                left = l[i]
                right = l[j]
                tmp_l = l[:]
                
                tmp_l.remove(left)
                tmp_l.remove(right)
                
                for op in Op:
                    
                    if op == Op.DIV and right.value == 0:
                        continue
                    
                    tmp_l.append(CombinedNode(left, right, op))
                    success, method = cls.solveImpl(tmp_l, target)
                    
                    if success:
                        return success, method
                    
                    # oops, didn't work, delete this attempt from the search
                    # space and go onto the next possibility
                    tmp_l.pop()
                    
        # we failed :'(
        return False, ""
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="enter the numbers to form 24 with")
    parser.add_argument("--values", type=int, nargs="+", help="numbers to form 24 with")

    args = parser.parse_args()

    print(TwentyFour.solve(args.values))

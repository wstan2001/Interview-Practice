#!/Users/stanley/opt/anaconda3/bin/python3
from attrs import define, field
from enum import Enum

class Side(Enum):
    Bid = 0
    Ask = 1
    
    def opposite(self):
        return Side.Ask if self == Side.Bid else Side.Bid
    
    @classmethod
    def side_converter(cls, s):
        if type(s) == str:
            return cls[s]
        elif type(s) == cls:
            return s
        else:
            raise ValueError(f"failed to convert {s} to Side!")
            
class Price:
    
    @staticmethod
    def is_px_better(px1: float, px2: float, side: Side) -> bool:
        # by "better", we mean more aggressive
        if side == Side.Bid:
            return px1 > px2
        elif side == Side.Ask:
            return px1 < px2
        else:
            raise ValueError(f"unknown side {side}")
            
    @staticmethod
    def is_px_better_or_eq(px1: float, px2: float, side: Side) -> bool:
        # by "better", we mean more aggressive
        if side == Side.Bid:
            return px1 >= px2
        elif side == Side.Ask:
            return px1 <= px2
        else:
            raise ValueError(f"unknown side {side}")
    

@define
class LimitOrder:
    id: int
    side: Side = field(converter=Side.side_converter)
    px: float
    size: int
         
        
@define
class Trade:
    side: Side
    px: float
    size: int
        
@define
class ListNode:
    val: LimitOrder
    next: "LinkedList" = None
    prev: "LinkedList" = None
        
@define 
class LinkedList:
    # NOT the general kind of linked list! We are going
    # to order our values here by price-time priority, so
    # this is more like a linked list implementation of
    # a priority queue
    
    # defines how we order the nodes
    side: Side
    head: ListNode = None
        
    def walk(self) -> list[ListNode]:
        
        ret = []
        cur_node = self.head
        
        while cur_node is not None:
            ret.append(cur_node)
            cur_node = cur_node.next
            
        return ret
            
    
    def insert(self, order: LimitOrder) -> ListNode:
        # insert the order into the list and return the inserted
        # ListNode.
        
        assert order.side == self.side, \
            f"Trying to insert order with {order.side=} into half with {self.side=}!"
                    
        if (self.head is None) \
            or Price.is_px_better(order.px, self.head.val.px, self.side):
            # insert at the beginning
            new_head = ListNode(val=order, next=self.head, prev=None)
            if self.head is not None:
                self.head.prev = new_head
            self.head = new_head
            
            return self.head
        else:
            # insert somewhere in the middle or end
            cur_node = self.head
            
            # advance cur_node until the order we wish to insert should
            # lie in between cur_node and cur_node.next
            while (cur_node.next is not None) \
            and Price.is_px_better_or_eq(cur_node.next.val.px, order.px, order.side):
                cur_node = cur_node.next

            # now insert the current order right after cur_node
            new_node = ListNode(val=order, next=cur_node.next, prev=cur_node)
            if cur_node.next is not None:
                cur_node.next.prev = new_node
            cur_node.next = new_node
            
            return new_node
                
    def remove(self, node: ListNode) -> None:
        # given a reference to the node, try to remove it from the list
        if node.prev is not None:
            node.prev.next = node.next
        if node.next is not None:
            node.next.prev = node.prev
            
        # note that node == self.head is incorrect here. Why?
        if node is self.head:
            self.head = node.next

@define
class OrderBook:
    
    # implement our order book as two LinkedList, each representing a 
    # side, each sorted by price-time priority
    halves: dict[Side, LinkedList] = field(
        factory=lambda : {
            Side.Bid: LinkedList(Side.Bid), 
            Side.Ask: LinkedList(Side.Ask),
        }
    )
        
    # order_dict provides order lookup for fast cancellation
    order_dict: dict[int, ListNode] = field(factory=dict)
        
    # Question: why do we want to use factory methods for initialization
    # rather than simply use a dict as the default value?
            
    def __str__(self) -> str:
        s = ""
        
        # gather linked list into list
        limit_orders = {Side.Bid: [], Side.Ask: []}
        
        for side in Side:
            cur_node = self.halves[side].head
            while cur_node is not None:
                limit_orders[side].append(cur_node.val)
                cur_node = cur_node.next
        
        # print all prices from highest to lowest
        for o in limit_orders[Side.Ask][::-1]:
            s += str(o) + "\n"
        
        s += "^ Asks:\n"
        s += "\n"
        s += "v Bids:\n"
        
        for o in limit_orders[Side.Bid]:
            s += str(o) + "\n"
            
        return s
        
        
    def add_order(self, order: LimitOrder) -> list[Trade]:
        # Add a limit order to our book.
        # Return a list of all trades that occurred as a result.
        
        trades = []
        
        opp_half = self.halves[order.side.opposite()]
        
        # 1. See if the current order crosses any other orders        
        while ((opp_head := opp_half.head) != None) \
            and order.size > 0 \
            and Price.is_px_better_or_eq(order.px, opp_head.val.px, order.side):
            # we have a trade
            trade_side = order.side
            trade_px = opp_head.val.px
            trade_size = min(order.size, opp_head.val.size)
            t = Trade(trade_side, trade_px, trade_size)
            
            trades.append(t)
            
            order.size -= trade_size
            opp_head.val.size -= trade_size
            
            # check if we need to delete the resting order from book
            if opp_head.val.size == 0:
                # ideally these two ops are atomic
                del self.order_dict[opp_head.val.id]
                opp_half.remove(opp_head)
                
        # 2. If there's any remaining size on the order, insert it into
        #    the appropriate half
        if order.size > 0:
            # ideally these two ops are atomic
            new_node = self.halves[order.side].insert(order)
            self.order_dict[order.id] = new_node
                     
        return trades
    
    def cancel_order(self, order_id: int) -> None:
        # this will throw if we try to cancel an order that's
        # not in the book...
        node = self.order_dict[order_id]
        side = node.val.side
        # ideally these two ops are atomic
        self.halves[side].remove(node)
        del self.order_dict[order_id]

def main(events: list[tuple]):
        
    all_trades = []
    book = OrderBook()
    
    for e in events:
        if len(e) == 4:
            # this is a new order
            lo = LimitOrder(*e)
            all_trades += book.add_order(lo)
        elif len(e) == 1:
            # this is a cancel request
            order_id = e[0]
            book.cancel_order(order_id)
        else:
            raise ValueError(f"Expected a tuple of length 1 or 4, got {e}")
        
        
    print(f"Trades:")
    print("-------------------")
    for t in all_trades:
        print(t)
    print("\n\n")
    print(f"Final book state:")
    print("-------------------")
    print(str(book))
    
if __name__ == "__main__":

    book = OrderBook()

    events = [
            (1, "Bid", 9.52, 300),
            (2, "Ask", 10.01, 100),
            (3, "Ask", 10.05, 100),
            (4, "Ask", 10.02, 100),
            (5, "Ask", 10.04, 100),
            (6, "Ask", 10.10, 3000),
            (5,),                   # cancel!
            (3,),                   # cancel!
            (4,),                   # cancel!
            (7, "Bid", 11, 1000),
    ]

    main(events)
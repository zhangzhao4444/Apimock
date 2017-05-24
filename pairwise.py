#!/usr/bin/evn python
# -*- coding:utf-8 -*-
# @author: zhangzhao_lenovo@126.com
# @date: 2017/4/17
# @version: 1.0.0.1001
# https://pypi.python.org/pypi/AllPairs/

#allpairs for python3

from functools import reduce
import operator

def xcombinations(items, n):
    if n== 0:
        yield []
    else:
        for i in range(len(items)):
            for cc in xcombinations(items[:i] + items[i + 1:], n - 1):
                yield [items[i]] + cc

def zzcombinsations(items, n):
    if n == 0:
        yield []
    else:
        for i in range(len(items)):
            for cc in zzcombinsations(items[i + 1:], n - 1):
                yield [items[i]] + cc

def xselections(items, n):
    if n == 0:
        yield []
    else:
        for i in range(len(items)):
            for ss in xselections(items, n - 1):
                yield [items[i]] + ss

def xpermutations(items):
    return xcombinations(items, len(items))

def permutations2(L):
    if len(L) <= 1:
        yield L
    else:
        a = [L.pop(0)]
        for p in xpermutations(L):
            for i in range(len(p) + 1):
                yield p[:i] + a + p[i:]

class node:
    def __init__(self, id):
        self.id = id
        self.counter = 0
        self.in_ = set()
        self.out = set()

    def __str__(self):
        return str(self.__dict__)

def key(items):
    return "->".join([x.id for x in items])

class pairs_storage:
    def __init__(self, n):
        self.__n = n
        self.__nodes = {}
        self.__combs_arr = []
        for i in range(n):
            self.__combs_arr.append(set())

    def add(self, comb):
        n = len(comb)
        assert (n > 0)

        self.__combs_arr[n - 1].add(key(comb))
        if n == 1 and comb[0].id not in self.__nodes:
            self.__nodes[comb[0].id] = node(comb[0].id)
            return

        ids = [x.id for x in comb]
        for i, id in enumerate(ids):
            curr = self.__nodes[id]
            curr.counter += 1
            curr.in_.update(ids[:i])
            curr.out.update(ids[i + 1:])

    def add_sequence(self, seq):
        for i in range(1, self.__n + 1):
            for comb in zzcombinsations(seq, i):
                self.add(comb)

    def get_node_info(self, item):
        return self.__nodes.get(item.id, node(item.id))

    def get_combs(self):
        return self.__combs_arr

    def __len__(self):
        return len(self.__combs_arr[-1])

    def count_new_combs(self, seq):
        s = set([key(z) for z in zzcombinsations(seq, self.__n)]) - self.__combs_arr[-1]
        print(len(s))
        return len(s)

class item:
    def __init__(self, id, value):
        self.id        = id
        self.value     = value
        self.weights = []
        
    def __str__(self):
        return str(self.__dict__)

    def __lt__(self, other):
        return operator.lt(self.weights,other.weights)

def get_max_comb_number( arr, n ):
    items = [len(x) for x in arr]
    f = lambda x,y:x*y
    total = sum([reduce(f, z) for z in zzcombinsations( items, n) ])
    return total
    
class all_pairs2:
    def __iter__( self ):
        return self
        
    def __init__( self, options, filter_func = lambda x: True, previously_tested = [[]], n = 2 ):
        """
        TODO: check that input arrays are:
            - (optional) has no duplicated values inside single array / or compress such values
        """
        if len( options ) < 2:
            raise Exception("must provide more than one option")
        for arr in options:
            if not len(arr):
                raise Exception("option arrays must have at least one item")

        self.__filter_func = filter_func
        self.__n = n
        self.__pairs = pairs_storage(n)
        self.__max_unique_pairs_expected = get_max_comb_number( options, n )
        self.__working_arr = []

        for i in range( len( options )):
            self.__working_arr.append( [ item("a%iv%i" % (i,j), value) \
                                         for j, value in enumerate(options[i] ) ] )
        for arr in previously_tested:
            if len(arr) == 0:
                continue
            elif len(arr) != len(self.__working_arr):
                raise Exception("previously tested combination is not complete")
            if not self.__filter_func(arr):
                raise Exception("invalid tested combination is provided")
            tested = []
            for i, val in enumerate(arr):
                idxs = [item(node.id, 0) for node in self.__working_arr[i] if node.value == val]
                if len(idxs) != 1:
                    raise Exception("value from previously tested combination is not found in the options or found more than once")
                tested.append(idxs[0])
            self.__pairs.add_sequence(tested)

    def __next__(self):
        assert( len(self.__pairs) <= self.__max_unique_pairs_expected )
        p = self.__pairs
        if len(self.__pairs) == self.__max_unique_pairs_expected:
            # no reasons to search further - all pairs are found
            raise StopIteration
        previous_unique_pairs_count= len(self.__pairs)
        chosen_values_arr          = [None] * len(self.__working_arr)
        indexes                    = [None] * len(self.__working_arr)
        direction = 1
        i = 0
        while -1 < i < len(self.__working_arr):
            if direction == 1: # move forward
                self.resort_working_array( chosen_values_arr[:i], i )
                indexes[i] = 0
            elif direction == 0 or direction == -1: # scan current array or go back
                indexes[i] += 1
                if indexes[i] >= len( self.__working_arr[i] ):
                    direction = -1
                    if i == 0:
                        raise StopIteration
                    i += direction    
                    continue
                direction = 0
            else:
                raise Exception("next(): unknown 'direction' code.")
            chosen_values_arr[i] =  self.__working_arr[i][ indexes[i] ]
            if self.__filter_func( self.get_values_array( chosen_values_arr[:i+1] ) ):
                assert(direction > -1)
                direction = 1
            else:
                direction = 0
            i += direction
        if  len( self.__working_arr ) != len(chosen_values_arr):
            raise StopIteration
        self.__pairs.add_sequence( chosen_values_arr )
        if len(self.__pairs) == previous_unique_pairs_count:
            # could not find new unique pairs - stop
            raise StopIteration
        # replace returned array elements with real values and return it
        return self.get_values_array( chosen_values_arr )
        
    def get_values_array( self, arr ):
        return [ item.value for item in arr ]
    
    def resort_working_array( self, chosen_values_arr, num ):
        for item in self.__working_arr[num]:
            data_node = self.__pairs.get_node_info( item )
            new_combs = []
            for i in range(0, self.__n):
                # numbers of new combinations to be created if this item is appended to array
                new_combs.append( set([key(z) for z in zzcombinsations( chosen_values_arr+[item], i+1)]) - self.__pairs.get_combs()[i] )
            # weighting the node
            item.weights =  [ -len(new_combs[-1]) ]    # node that creates most of new pairs is the best
            item.weights += [ len(data_node.out) ] # less used outbound connections most likely to produce more new pairs while search continues
            item.weights += [ len(x) for x in reversed(new_combs[:-1])]
            item.weights += [ -data_node.counter ]  # less used node is better
            item.weights += [ -len(data_node.in_) ] # otherwise we will prefer node with most of free inbound connections; somehow it works out better ;)
        self.__working_arr[num].sort()

    # statistics, internal stuff        
    def get_pairs_found( self ):
        return self.__pairs


def test():
    # value = ['fun:del', 'fun:more', 'fun:blank', 'fun:none', 'fun:null', 'fun:0', 'fun:-1', 'fun:0.00002',
    #                    'fun:2.00001', 'fun:maxint', 'fun:maxlong', 'fun:*n', 'fun:/n', 'fun:ext', 'fun:cut', 'fun:overlen', 'fun:illega']
    # key = ['errno','errmsg','data']
    # parameters = [key,value]
    # print(parameters)
    # case = all_pairs2(parameters)
    # for i, v in enumerate(case):
    #     List = list(v)
    #     item = List[0] + '=' + List[1]
    #     print('%i : %s'%(i+1,item))

    value = ['fun:del', 'fun:more', 'fun:blank', 'fun:none', 'fun:null', 'fun:0', 'fun:-1', 'fun:0.00002',
             'fun:2.00001', 'fun:maxint', 'fun:maxlong', 'fun:*n', 'fun:/n', 'fun:ext', 'fun:cut', 'fun:overlen',
             'fun:illega']
    key = ['errno', 'errmsg', 'data']
    # errno = ['']
    # errmsg = ['']
    # data = ['']
    parameters = []
    for k in key:
        exec(k + "=['']")
        for v in value:
            exec(k + '.append('+"'"+ k + '='+ v+"'"+')')
        parameters.append(eval(k))
    print(parameters)
    case = all_pairs2(parameters)
    for i, v in enumerate(case):
        print('%i : %s' % (i + 1, v))

if __name__ == "__main__":
    test()









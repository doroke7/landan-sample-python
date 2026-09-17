# 1. 函數接收不定數量參數

def sum_all(*args):

    print(args)

sum_all(1, 2, 3)


'''
function sumAll(...args) {
    console.log(args);
}

sumAll(1, 2, 3);
// [1, 2, 3]

'''

# 2. “陣列”展開：

nums = [1, 2, 3]
print(*nums)
# 1 2 3


'''
const nums = [1, 2, 3];
console.log(...nums);
// 1 2 3

'''

# 3. “陣列”展開：

def add(a, b, c):
    print(a + b + c)

nums = [1, 2, 3]
add(*nums)
# 6


'''
function add(a, b, c) {
    console.log(a + b + c);
}
const nums = [1, 2, 3];
add(...nums);
// 6

'''


# 4. “陣列”合併：

a = [1, 2]
b = [3, 4]

c = [*a, *b]

print(c)
# [1, 2, 3, 4]


'''
a = [1, 2]
b = [3, 4]

c = [*a, *b]

print(c)
# [1, 2, 3, 4]

'''

# 5. “陣列”解構剩餘元素：

nums = [1, 2, 3, 4, 5]

first, *rest = nums

print(first)
# 1

print(rest)
# [2, 3, 4, 5]


'''
const nums = [1, 2, 3, 4, 5];

const [first, ...rest] = nums;

console.log(first);
// 1

console.log(rest);
// [2, 3, 4, 5]

'''



# 11. 字典 dict 合併

a = {
    "name": "Tom"
}

b = {
    "age": 18
}

c = {**a, **b}

print(c)

# {'name': 'Tom', 'age': 18}


'''
const a = {
    name: "Tom"
};

const b = {
    age: 18
};

const c = {
    ...a,
    ...b
};

console.log(c);

// { name: 'Tom', age: 18 }
'''
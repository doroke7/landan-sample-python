d_id_to_name = {0: 'Dog', 1: 'Cat', 2: 'Bird', 3: 'Tree'}

d_name_to_id = {s_name: i_id for i_id, s_name in d_id_to_name.items()}


print(d_name_to_id)


# Dict Comprehension 反轉 key/value：Python 圈子的共識寫法
# 	1.	好讀：一行就看出「把 dict 的 key/value 互換」，不用追 for 迴圈裡在幹嘛
# 	2.	前提：value 要是唯一、可 hash 的，不然反轉時後面的值會蓋掉前面的

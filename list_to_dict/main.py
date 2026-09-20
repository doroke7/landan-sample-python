a_names = ['Dog', 'Cat', 'Bird', 'Tree']

d_id_to_name = {i_id: s_name for i_id, s_name in enumerate(a_names)}


print(d_id_to_name)


# Dict Comprehension：Python 圈子的共識寫法，大家都這樣寫 array -> dict
# 	1.	好讀：一行就看出「用 enumerate 把 array 轉成 {index: value} 的 dict」，不用追 for 迴圈裡在幹嘛
# 	2.	前提：這一行只做「組字典」這一件事，不要在裡面塞其他運算邏輯，不然又變得難讀

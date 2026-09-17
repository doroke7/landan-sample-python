aNames = ['Tom', 'Mary', 'Hose', 'James']

aUpperNames = [ sName.upper() for sName in aNames]



# Python 的 List Comprehension（列表推導式）
# 	1.	速度更快：它在底層是由 C 實現的，比手寫 for 循環接 append() 要快。
#	2.	簡潔：邏輯在一行內清晰展現。
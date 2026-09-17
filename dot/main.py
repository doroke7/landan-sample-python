# from .helper.rsa_helper import RsaHelper # 這個語法不行，因為 .只在模組目錄生效 
from helper.rsa_helper import RsaHelper # 這個語法不行，因為 .只在模組目錄生效 

o_ras_helper = RsaHelper()
o_ras_helper.encode()
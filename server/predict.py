import os

#
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "nmt-API-07b7802bb743.json"
from main_func import *

# print(os.listdir())
main('product-analytics-group7/server/examples/img10.jpg',
     'product-analytics-group7/server/examples/img10_trn.jpg')
# print(os.listdir())

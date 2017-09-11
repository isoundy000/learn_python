# -*-coding:utf-8-*-
'''
Created on 2017年9月8日

@author: houguangdong
'''
# Python计算地图上两点经纬度间的距离
# 处理地图数据时，经常需要用到两个地理位置间的距离。比如A点经纬度（110.0123, 23.32435），B点经纬度（129.1344,25.5465），求AB两点之间的距离。我们可以用haversine()函数求出距离结果。Python版本的haversine()如下所示：
from math import radians, cos, sin, asin, sqrt, fabs
  
def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）  
    """ 
    Calculate the great circle distance between two points  
    on the earth (specified in decimal degrees) 
    """  
    # 将十进制度数转化为弧度  
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])  
  
    # haversine公式  
    dlon = lon2 - lon1   
    dlat = lat2 - lat1   
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2  
    c = 2 * asin(sqrt(a))   
    r = 6371 # 地球平均半径，单位为公里  
    return c * r * 1000


# python利用地图两个点的经纬度计算两点间距离
#!/usr/bin/python3  
EARTH_RADIUS=6371           # 地球平均半径，6371km  

def hav(theta):  
    s = sin(theta / 2)  
    return s * s  
   
def get_distance_hav(lat0, lng0, lat1, lng1):  
    "用haversine公式计算球面两点间的距离。"  
    # 经纬度转换成弧度  
    lat0 = radians(lat0)  
    lat1 = radians(lat1)  
    lng0 = radians(lng0)  
    lng1 = radians(lng1)  
   
    dlng = fabs(lng0 - lng1)  
    dlat = fabs(lat0 - lat1)  
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)  
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))  
    return distance  


lon1,lat1 = (22.599578, 113.973129)   # 深圳野生动物园(起点）  
lon2,lat2 = (22.6986848, 114.3311032) # 深圳坪山站 (百度地图测距：38.3km)  
d2 = get_distance_hav(lon1,lat1,lon2,lat2)  
print(d2)  
  
lon2,lat2 = (39.9087202, 116.3974799) #北京天安门(1938.4KM)  
d2 = get_distance_hav(lon1,lat1,lon2,lat2)  
print(d2)  
  
lon2,lat2 =(34.0522342, -118.2436849) #洛杉矶(11625.7KM)  
d2 = get_distance_hav(lon1,lat1,lon2,lat2)  
print(d2)  


if __name__ == '__main__':
    print haversine(110.123, 23.32, 110.124, 23.32)
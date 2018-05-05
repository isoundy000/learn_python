# -*- encoding: utf-8 -*-
'''
Created on 2018年5月2日

@author: houguangdong
'''

# 背景
# 关于tornado，我这里就不详细讲了，有兴趣的同学可以通过以下两篇博客了解一下：
# 
#   http://yunjianfei.iteye.com/blog/2185476
#   http://yunjianfei.iteye.com/blog/2185446
# 我们一般用tornado来编写web程序，但实际上，tornado底层的代码非常优秀，也可以用这些代码来编写TCP应用。
# 代码
# tornado最突出的特点就是“异步”，所以，我这里编写了一个异步的TCPServer和一个异步的TCPClient来帮助大家理解，下面直接看代码：
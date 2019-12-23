# Python 2.x中可以编译成功
# 以上的代码我们可以在Python2.x的版本中编译成功。以Python2.6.6中为例。
Z = open('data1.bin','wb')
import struct
data = struct.pack('>i4sh',7,'spam',8)
Z.write(data)
Z.close()

Z = open('data1.bin','rb')
data = F.read()
print(data)
values = struct.unpack('>i4sh',data)
print(values)
# 可以看到c,s,p这几个在Python 中的类型都是string。
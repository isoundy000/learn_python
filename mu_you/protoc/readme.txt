# 安装文件夹名查找
find / -type d -iname "protoc-gen-lua-master"
# 生成xxx_pb.lua的命令
protoc  --lua_out=./ --plugin=protoc-gen-lua=./protoc-gen-lua-master/plugin/protoc-gen-lua ./slots.proto 
protoc --lua_out=./ --plugin=protoc-gen-lua-master/plugin/protoc-gen-lua ./slots.proto

# py的命令
cd /Users/houguangdong/svn/jpzmg/trunk/tjpzmg/apps/game/proto
protoc --python_out=./ ./item_package.proto
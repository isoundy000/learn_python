#!/usr/bin/env python
#-*- coding: UTF-8 -*-


# svn add foo.c
# 当添加一个目录，svn add缺省的行为方式是递归的：
# $ svn add testdir
# 你可以只添加一个目录而不包括其内容：
# $ svn add --non-recursive otherdir
# 通常情况下，命令svn add *会忽略所有已经在版本控制之下的目录，有时候，你会希望添加所有工作拷贝的未版本化文件，
# 包括那些隐藏在深处的文件，可以使用svn add的--force递归到版本化的目录下：
# svn add * --force


# 1、保证我们拿到的是最新代码：
# svn update
# 假设最新版本号是28。

# 2、然后找出要回滚的确切版本号：
# svn log
# 假设根据svn log日志查出要回滚的版本号是25，此处的something可以是文件、目录或整个项目
# 如果想要更详细的了解情况，可以使用svn diff -r 28:25 ""

# 3、回滚到版本号25：
# svn merge -r 28:25 ""
# 为了保险起见，再次确认回滚的结果：
# svn diff ""
# 发现正确无误，提交。

# 4、提交回滚：
# svn commit -m "Revert revision from r28 to r25,because of ..."
# 提交后版本变成了29。

# 1. svn update，svn log，找到最新版本（latest revision）
# 2. 找到自己想要回滚的版本号（rollbak revision）
# 3. 用svn merge来回滚： svn merge -r : something

# 7、删除文件
# 删除远端
# svn delete svn://192.168.1.1/pro/domain/test.php -m "delete test file"
# 删除本地在提交
# svn delete test.php
# svn ci -m 'delete test file‘
# svn delete 简写：svn del／remove／rm

# 8、查看日志（显示文件的所有修改记录，及其版本号的变化）
# svn log path
# svn log -l 3查看最新的三条记录
# 例如：svn log test.php

# 9、查看文件详细信息
# svn info path
# 例如：svn info test.php

# 10、比较差异
# svn diff path(将修改的文件与基础版本比较)
# 例如：svn diff test.php
# svn diff -r m:n path(对版本m和版本n比较差异)
# 例如：svn diff -r 200:201 test.php
# svn diff 简写：svn di

# 11、合并文件（将两个版本之间的差异合并到当前文件）
# svn merge -r m:n path
# 例如：
# svn merge -r 200:205 test.php（将版本200与205之间的差异合并到当前文件，但是一般都会产生冲突，需要处理一下）

# 12、SVN 帮助
# svn help	全部功能选项
# svn help ci 具体功能的说明

# 13、版本库下的文件和目录列表
# svn list path
# 显示path目录下的所有属于版本库的文件和目录
# svn list 简写：svn ls

# 14、创建纳入版本控制下的新目录
# svn mkdir newdir
# 例如：
# svn mkdir -m "Making a new dir." svn://localhost/test/newdir
# 用法:
# 创建版本控制的目录。
# 1、mkdir PATH...
# 1、每一个以工作副本 PATH 指定的目录，都会创建在本地端，并且加入新增
# 调度，以待下一次的提交。

# 2、mkdir URL...
# 2、每个以URL指定的目录，都会透过立即提交于仓库中创建。
# （在这两个情况下，所有的中间目录都必须事先存在）

# 注：添加完子目录后，一定要回到根目录更新svn update一下，不然在该目录下提交文件会提示“提交失败”
# 注：如果手动在checkout出来的目录里创建了一个新文件夹newsubdir，
# 　　 再用svn mkdir newsubdir命令后，SVN会提示：
# 　　svn: 尝试用 “svn add”或 “svn add --non-recursive”代替？
# 　　svn: 无法创建目录“hello”: 文件已经存在
# 　　 此时，用如下命令解决：
# 　　svn add --non-recursive newsubdir
# 在进入这个newsubdir文件夹，用ls -a查看它下面的全部目录与文件，会发现多了：.svn目录
# 　　再用 svn mkdir -m "添hello功能模块文件" svn://localhost/test/newdir/newsubdir 命令，
# 　　SVN提示：
# 　　svn: File already exists: filesystem '/data/svnroot/test/db', transaction '4541-1',
# 　　path '/newdir/newsubdir '

# 15、恢复本地修改
# svn revert: 恢复原始未改变的工作副本文件 (恢复大部份的本地修改)。
# 用法: revert PATH...
# 注意: 本子命令不会存取网络，并且会解除冲突的状况。但是它不会恢复
# 被删除的目录
# svn revert foo.c ＜－ 丢弃对一个文件的修改
# svn revert --recursive . ＜－恢复一整个目录的文件，. 为当前目录

# 16、代码库URL变更
# svn switch (sw): 更新工作副本至不同的URL。
# 用法:
# 1、switch URL [PATH]
# 2、switch --relocate FROM TO [PATH...]
# 1、更新你的工作副本，映射到一个新的URL，其行为跟“svn update”很像，也会将
# 服务器上文件与本地文件合并。这是将工作副本对应到同一仓库中某个分支或者标记的
# 方法。
# 2、改写工作副本的URL元数据，以反映单纯的URL上的改变。当仓库的根URL变动
# (比如方案名或是主机名称变动)，但是工作副本仍旧对映到同一仓库的同一目录时使用
# 这个命令更新工作副本与仓库的对应关系。
# svn switch 间写： svn sw

# 17、解决冲突
# svn resolved: 移除工作副本的目录或文件的“冲突”状态。
# 用法: resolved PATH...
# 注意: 本子命令不会依语法来解决冲突或是移除冲突标记；
# 它只是移除冲突的相关文件，然后让 PATH 可以再次提交。

# 18、输出指定文件或URL的内容
# svn cat 目标[@版本]...如果指定了版本，将从指定的版本开始查找。
# svn cat -r PREV filename > filename (PREV 是上一版本,也可以写具体版本号,这样输出结果是可以提交的)

# 19、查看svn版本
# svn —-version

# 20、新建分支branchs，在分支上继续开发
# 1、svn mkdir branches
# 2、svn copy svn://server/trunk svn://server/branches/ep -m "init ep"

# 21、该版本完成，打tag，发布版本
# 1、svn mkdir tags
# 2、svn copy svn://server/trunk svn://server/tags/release-1.0 -m "1.0 released"


# 2、问题：
# 不小心提交了一些动态改变根本不需要的文件到svn服务器上
# 解决：
# svn resolved filename 放弃对文件的修改，
# svn ci -m "update" 提交所有文件
# svn rm test.log 删除掉这个文件。
# svn ci -m "update" 再次提交
#
#
# 3、发生冲突：
# 两人同时修改同一文件同一部分，先后提交，出现冲突
# svn ci -m "update"
# svn: Commit failed (details follow):
# svn: Aborting commit: 'test.log' remains in conflict
# 解决：
# A、放弃自己的更新，使用svn revert（回滚），然后提交。在这种方式下不需要使用svn resolved（解决）
# B、放弃自己的更新，使用别人的更新。使用最新获取的版本覆盖目标文件，执行resolved filename并提交(选择文件—右键—解决)。
# C、手动解决：冲突发生时，通过和其他用户沟通之后，手动更新目标文件。然后执行resolved filename来解除冲突，最后提交。
#
# 坚持使用自己的更新，找到.mine的文件名，恢复为原文件名，然后执行：
# svn resolved file_name
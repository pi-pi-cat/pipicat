sudo mkdir /test
sudo chown root:users /test
sudo chmod 2775 /test
sudo setfacl -d -m g::rwx /test
ls -ld /test


在 CentOS 上，你可以使用以下命令来管理用户组和查看用户所属的组：

将用户添加到 users 组：
Copysudo usermod -aG users 用户名
这里的 -a 选项表示追加，这样不会将用户从其他组中移除。
查看用户所属的组：
a. 查看当前用户所属的组：
Copygroups
b. 查看特定用户所属的组：
Copygroups 用户名
c. 更详细的方法，显示用户ID(UID)和组ID(GID)：
Copyid 用户名

查看系统中所有的组：
Copycat /etc/group

查看特定组的成员：
Copygetent group 组名

创建新组（如果需要）：
Copysudo groupadd 新组名

从组中移除用户（如果需要）：
Copysudo gpasswd -d 用户名 组名


实际操作示例：

将用户 john 添加到 users 组：
Copysudo usermod -aG users john

查看 john 所属的组：
Copygroups john

查看 users 组的所有成员：
Copygetent group users

查看 john 的详细组信息：
Copyid john
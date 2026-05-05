# qqchan
> QQ酱，一个运行在Onebot11上的、类似于Server酱的消息推送服务

## 用法

| 命令 | 说明 |
| --- | --- |
| `/register` | 为当前用户注册，会返回一个id |
| `/register <群号>` | 为指定群聊注册（必须是管理员） |
| `/list` | 列出当前用户的所有id |
| `/list <群号>` | 列出当前用户在指定群聊的所有id |
| `/list all` | 列出当前用户的所有id，以及当前用户注册的所有群聊id |
| `/revoke <id>` | 注销指定id（当前用户或当前用户注册的群聊） |
| `/revoke me` | 注销当前用户的所有id |
| `/revoke all` | 注销当前用户的所有id，以及当前用户注册的所有群聊id |

拿到id之后，访问
`http://<机器人所运行的ip和端口>/qqchan/send?id=<你得到的id>&m=<要发送的消息>`
即可向指定目标推送消息

## 部署方法

1. 安装nonebot2脚手架
    ```bash
    uv tool install nb-cli
    ```

2. 创建项目
    ```bash
    nb create
    ```
    创建项目时，`driver`选择`FastAPI`，`adapter`选择`Onebot11`。

3. 添加依赖
    ```bash
    uv add git+https://github.com/BailPlus/qqchan.git
    ```

4. 启动项目
    ```bash
    nb run
    ```

5. 运行Onebot11实现端，并配置连接

## TODO

- [ ] 增加推送失败监测功能，自动移除已删除的好友或已退出的群聊
- [ ] 增加ServerChan兼容接口
- [ ] 移除群管理员限制
- [ ] 增加推送消息长度限制和推送频率限制

import asyncio
import os
import random
from loguru import logger 
import aiohttp

from api import *
from datetime import datetime, timezone, timedelta


def generate_random_private_ip():
    # 定义内网IP地址段
    private_ranges = [
        {"start": (10, 0, 0, 0), "end": (10, 255, 255, 255)},
        {"start": (172, 16, 0, 0), "end": (172, 31, 255, 255)},
        {"start": (192, 168, 0, 0), "end": (192, 168, 255, 255)}
    ]
    
    # 随机选择一个地址段
    selected_range = random.choice(private_ranges)
    start = selected_range["start"]
    end = selected_range["end"]
    
    # 生成四个随机字节
    ip_parts = []
    for i in range(4):
        # 在当前段的起始和结束范围内生成随机数
        ip_part = random.randint(start[i], end[i])
        ip_parts.append(str(ip_part))
    
    return ".".join(ip_parts)

class kurobbs_request():
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rq.close()

    def __init__(self, DID=None, TOKEN=None, BAT=None):
        self.DID =  DID if DID != None else os.getenv("DID")
        self.TOKEN = TOKEN if TOKEN != None else os.getenv("TOKEN")
        self.BAT = BAT if BAT != None else os.getenv("BAT")

        self.ip = generate_random_private_ip()
        self.headers = {
            "devCode": f"{self.ip}, Mozilla/5.0 (Linux; Android 15; V2408A Build/AP3A.240905.015.A2_V0101L11; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.71 Mobile Safari/537.36 Kuro/2.4.4 KuroGameBox/2.4.4",
            "User-Agent": "Mozilla/5.0 (Linux; Android 15; V2408A Build/AP3A.240905.015.A2_V0101L11; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.71 Mobile Safari/537.36 Kuro/2.4.4 KuroGameBox/2.4.4",
            "X-Forwarded-For": str(self.ip),
            "source": "android",
            "token": self.TOKEN,
            "b-at": self.BAT,
            "did": self.DID,
            "version": "2.50"
        }
        self.rq = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        self.rq.headers.update(self.headers)

    async def get_user_game_list(self):
        """
        取绑定游戏账号列表
        https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/user/role/findRoleList.md
        
        先调用以获取所需数据
        """
        data = {"gameId": GAME_ID}

        async with self.rq.post(FIND_ROLE_LIST_API_URL, data=data) as res:
            return await res.json()
    
    async def sign_in(self, roleId: str):
        """
        游戏签到 V2
        https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/encourage/signIn/v2.md
        """
        data = {
            "gameId": GAME_ID,
            "serverId": SERVER_ID,
            "roleId": roleId,
            "reqMonth": f"{datetime.now(timezone(timedelta(hours=8))).month:02}",
        }
        async with self.rq.post(SIGNIN_URL, data=data) as res:
            return await res.json()

    async def sign_in_task_list(self, roleId: str):
        """
        取游戏签到信息 V2
        https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/encourage/signIn/initSignInV2.md
        """
        data = {
            "gameId": GAME_ID,
            "serverId": SERVER_ID,
            "roleId": roleId,
        }
        async with self.rq.post(SIGNIN_TASK_LIST_URL, data=data) as res:
            return await res.json()
 
    async def do_like(
        self, postId, toUserId
    ):
        """
        通用论坛点赞
        https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/forum/like.md
        """
        data = {
            "gameId": "3",  # 鸣潮
            "likeType": "1",  # 1.点赞帖子 2.评论
            "operateType": "1",  # 1.点赞 2.取消
            "postId": postId,
            "toUserId": toUserId,
        }
        async with self.rq.post(LIKE_URL, data=data) as res:
            return await res.json()
    
    async def do_sign_in(self):
        """签到"""
        data = {"gameId": "2"}
        async with self.rq.post(SIGN_IN_URL, data=data) as res:
            return await res.json()

    async def do_post_detail(self, postId: str):
        """浏览
        取帖子详情
        https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/forum/getPostDetail.md
        """
        data = {
            "postId": postId,
            "showOrderType": "2",
            "isOnlyPublisher": "0",
        }
        headers = {
            "devCode": self.DID
        }
        async with self.rq.post(POST_DETAIL_URL, headers=headers, data=data) as res:
            return await res.json()
    
    async def do_share(self):
        """
        社区分享任务
        https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/encourage/level/shareTask.md
        """
        # 定义请求参数
        data = {"gameId": "3"}
        # 发送POST请求，获取返回结果
        async with self.rq.post(SHARE_URL, data=data) as res:
            return await res.json()

    async def get_task(self):
        """
        获取任务进度
        https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/encourage/level/getTaskProcess.md
        """
        data = {"gameId": "0"}
        async with self.rq.post(GET_TASK_URL, data=data) as res:
            return await res.json()

    async def get_form_list(self):
            """
            取帖子列表
            https://github.com/TomyJan/Kuro-API-Collection/blob/master/API/forum/list.md
            """
            headers = {"version": "2.25"}
            data = {
                "pageIndex": "1",
                "pageSize": "20",
                "timeType": "0",
                "searchType": "1",
                "forumId": "9",
                "gameId": "3",
            }
            async with self.rq.post(FORUM_LIST_URL, headers=headers, data=data) as res:
                return await res.json()

    async def get_notLike_list(self, num=5):
        """
        获取num个未点赞的帖子信息
        return [{postId: ..., userId: ...}]
        """
        n = 0
        l = []
        fl = await self.get_form_list()
        for i in fl["data"]["postList"]:
            if i["isLike"] == 0:
                l.append({"postId": i["postId"], "userId": i["userId"]})
                num += 1
                if n == num:
                    break
        return l
    

async def main():
    async with kurobbs_request() as kr:
        user_list = await kr.get_user_game_list()
        for i in user_list["data"]:
            do_share = await kr.do_share()
            do_sign_in = await kr.do_sign_in()
            sign_in = await kr.sign_in(i["roleId"])

            nk = await kr.get_notLike_list()
            for i in nk:
                await kr.do_like(postId=i["postId"], toUserId=i["userId"])
                await kr.do_post_detail(postId=i["postId"])

        progress = await kr.get_task()

        logger.debug(do_share)
        logger.debug(do_sign_in)
        logger.debug(sign_in)
        logger.debug(nk)
        logger.info(progress)

if __name__ == '__main__':
    asyncio.run(main())
